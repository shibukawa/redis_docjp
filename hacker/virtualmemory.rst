.. Virtual Memory technical specification

==================
仮想メモリ技術仕様
==================

.. This document details the internals of the Redis Virtual Memory subsystem. The 
   intended audience is not the final user but programmers willing to understand 
   or modify the Virtual Memory implementation.

このドキュメントでは、Redisの仮想メモリサブシステムの内部の詳細を説明します。このドキュメントはユーザのためのものではなく、仮想メモリ実装を理解したい人や、手を加えたいプログラマーのためのものです。

.. Keys vs Values: what is swapped out?

キーvs値: スワップアウトとは何か？
===================================

.. The goal of the VM subsystem is to free memory transferring Redis Objects from memory
   to disk. This is a very generic command, but specifically, Redis transfers only
   objects associated with values. In order to understand better this concept we'll
   show, using the DEBUG command, how a key holding a value looks from the point of
   view of the Redis internals:

VMサブシステムの目標は、Redisのオブジェクトをメモリからディスクに移すことによって、メモリを空けることにあります。Redisは値のオブジェクトのみを転送します。この概念を理解しやすくするために、 :com:`DEBUG` コマンドを使用して、Redisの内部では、どのようにキーと値がひもづけられているのかを確認してみましょう。

.. code-block:: erlang

   redis> set foo bar
   OK
   redis> debug object foo
   Key at:0x100101d00 refcount:1, value at:0x100101ce0 refcount:1 encoding:raw serializedlength:4

.. As you can see from the above output, the Redis top level hash table maps Redis 
   Objects (keys) to other Redis Objects (values). The Virtual Memory is only able 
   to swap values on disk, the objects associated to keys are always taken in memory: 
   this trade off guarantees very good lookup performances, as one of the main
   design goals of the Redis VM is to have performances similar to Redis with VM
   disabled when the part of the dataset frequently used fits in RAM.

上記の出力例から分かるように、Redisのトップレベルのハッシュテーブルは、Redisオブジェクト(キー)から、他のRedisオブジェクト(値)への対応表となっています。仮想メモリは、値のオブジェクトだけをディスクにスワップし、キーのオブジェクトはメモリ内に保持します。これは、VMが無効状態のRedisと、VMが有効になっているRedisで、良く使われるデータセットがメモリに収まっている場合は同じぐらいのパフォーマンスを発揮するようにするという設計の主な目標を達成する仕様になっています。

.. How does a swapped value looks like internally

スワップの内部動作
==================

.. When an object is swapped out, this is what happens in the hash table entry:

オブジェクトがスワップされる時は、次のようなことが発生します。

.. * The key continues to hold a Redis Object representing the key.
   * The value is set to NULL

* キーには、引き続きキーを表すRedisオブジェクトが保持される
* 値には ``NULL`` がセットされる

.. So you may wonder where we store the information that a given value 
   (associated to a given key) was swapped out. Just in the key object!

これだけを見ると、キーに関連した値の情報はどこに格納されているのか疑問に思うでしょう。それは、キーオブジェクトの中に格納されます。

.. This is how the Redis Object structure robj looks like:

Redisオブジェクト構造体のrobjは次のような実装になっています。

..
   /* The actual Redis Object */
   typedef struct redisObject {
       void *ptr;
       unsigned char type;
       unsigned char encoding;
       unsigned char storage;  /* If this object is a key, where is the value?
                                * REDIS_VM_MEMORY, REDIS_VM_SWAPPED, ... */
       unsigned char vtype; /* If this object is a key, and value is swapped out,
                             * this is the type of the swapped out object. */
       int refcount;
       /* VM fields, this are only allocated if VM is active, otherwise the
        * object allocation function will just allocate
        * sizeof(redisObjct) minus sizeof(redisObjectVM), so using
        * Redis without VM active will not have any overhead. */
       struct redisObjectVM vm;
   } robj;

.. code-block:: c

   /* Redisオブジェクトの実体 */
   typedef struct redisObject {
       void *ptr;
       unsigned char type;
       unsigned char encoding;
       unsigned char storage;  /* もしこのオブジェクトがキーなら、値がどこにあるのか？
                                * REDIS_VM_MEMORY, REDIS_VM_SWAPPED, ... */
       unsigned char vtype;    /* もしこのオブジェクトがキーでスワップされている場合、,
                                * スワップされたたオブジェクトの種類を表す */
       int refcount;
       /* VM属性。これはVM機能が有効な時だけ割り当てられられる。
        * そうでない時は、オブジェクトの割り当て関数は、 
        * ``sizeof(redisObjct) - sizeof(redisObjectVM)sizeof(redisObjct)`` の分のメモリ
        * しか確保しないため、VMが無効の場合は常に他のオブジェクトに上書きされる。 */
       struct redisObjectVM vm;
   } robj;

.. As you can see there are a few fields about VM. The most important one is storage, 
   that can be one of this values:

この中には、VMに関する属性がいくつかあります。この中で最も重要なのは、 ``storage`` です。

``REDIS_VM_MEMORY``

   .. the associated value is in memory.

   関連する値はメモリの中にある。

``REDIS_VM_SWAPPED``

   .. the associated values is swapped, and the value entry of the hash table is 
      just set to NULL.

   関連する値はスワップされていて、ハッシュテーブルの値のエントリーには ``NULL`` が設定されている。

``REDIS_VM_LOADING``

   .. the value is swapped on disk, the entry is NULL, but there is a job to 
      load the object from the swap to the memory (this field is only used when 
      threaded VM is active).

   値はディスクにスワップされてエントリーは ``NULL`` であるが、現在メモリにスワップされたオブジェクトをロードするジョブが実行中。このフィールドはスレッド対応仮想メモリが有効な場合にのみ使用される。

``REDIS_VM_SWAPPING``

   .. the value is in memory, the entry is a pointer to the actual Redis Object, 
      but there is an I/O job in order to transfer this value to the swap file.

   値はメモリにあり、このポインタは実際にRedisオブジェクトを指しているが、この値をスワップファイルに転送するI/Oジョブが稼働中。

.. If an object is swapped on disk (REDIS_VM_SWAPPED or REDIS_VM_LOADING), how do we know 
   where it is stored, what type it is, and so forth? That's simple: the vtype field is 
   set to the original type of the Redis object swapped, while the vm field (that is 
   a redisObjectVM structure) holds information about the location of the object. This 
   is the definition of this additional structure:

オブジェクトがディスクにスワップされている(``REDIS_VM_SWAPPED`` あるいは ``REDIS_VM_LOADING``)場合、どこに格納されているのかを知るにはどうすればいいのでしょうか？また、その値のタイプはなんでしょうか？これはとてもシンプルです。スワップされたオリジナルのRedisオブジェクトのタイプは、 ``vtype`` 属性に格納されています。また、格納されている場所も、 ``redisObjectVM`` 構造体型の ``vm`` 属性の中に保持されています。この構造体には追加の属性が定義されています。

.. /* The VM object structure */
   struct redisObjectVM {
       off_t page;         /* the page at which the object is stored on disk */
       off_t usedpages;    /* number of pages used on disk */
       time_t atime;       /* Last access time */
   } vm;

.. code-block:: c

   /* 仮想メモリオブジェクトの構造体 */
   struct redisObjectVM {
       off_t page;         /* オブジェクトが格納されているディスク上のページ */
       off_t usedpages;    /* ディスクで使用しているページ数*/
       time_t atime;       /* 最後にアクセスした時間 */
   } vm;

.. As you can see the structure contains the page at which the object is located 
   in the swap file, the number of pages used, and the last access time of the object
   (this is very useful for the algorithm that select what object is a good candidate
    for swapping, as we want to transfer on disk objects that are rarely accessed).

この構造体には、スワップファイルの中のどこにオブジェクトが格納されているかというページの場所の情報と、使用しているページ数、また、最後にアクセスした時間の情報が書かれています。この時間情報は、アクセスの少ないオブジェクトをスワップするときに、候補を選択するアルゴリズムから使用されます。

.. As you can see, while all the other fields are using unused bytes in the old Redis
   Object structure (we had some free bit due to natural memory alignment concerns), the
   vm field is new, and indeed uses additional memory. Should we pay such a memory cost
   even when VM is disabled? No! This is the code to create a new Redis Object:

このコードを見ての通り、以前のRedisオブジェクトの構造体の他のすべての属性は使われても(メモリのアラインで空白領域はできるかもしれませんが)、この新しい ``vm`` 属性によって、追加のメモリが使用されます。このメモリのコストはVMが無効な時は払う必要はありません。次のコードはRedisオブジェクトを作るときのコードになります。

.. code-block:: c

   ... some code ...
        if (server.vm_enabled) {
            pthread_mutex_unlock(&server.obj_freelist_mutex);
            o = zmalloc(sizeof(*o));
        } else {
            o = zmalloc(sizeof(*o)-sizeof(struct redisObjectVM));
        }
   ... some code ...

.. As you can see if the VM system is not enabled we allocate just 
   sizeof(*o)-sizeof(struct redisObjectVM) of memory. Given that the vm field is 
   the last in the object structure, and that this fields are never accessed 
   if VM is disabled, we are safe and Redis without VM does not pay the memory overhead.

仮想メモリが無効な場合には、 ``sizeof(*o)-sizeof(struct redisObjectVM)`` 分しかメモリを確保していません。 ``vm`` 属性は構造体の最後にあるため、他のオブジェクトとメモリ空間がオーバーラップしても問題はなく、仮想メモリを使用しない場合にはメモリのオーバーヘッドは発生しません。

.. The Swap File

スワップファイル
================

.. The next step in order to understand how the VM subsystem works is understanding
   how objects are stored inside the swap file. The good news is that's not some kind
   of special format, we just use the same format used to store the objects in .rdb
   files, that are the usual dump files produced by Redis using the SAVE command.

VMサブシステムを理解するための次のステップとして、オブジェクトがスワップファイルに格納される仕組みを見て行きます。スワップファイルで使っているフォーマットは特別なものではなく、 :com:`SAVE` コマンドを使った時にRedisが通常作成しているダンプファイルに、 :file:`.rdb` ファイル内にオブジェクトが格納される時に使われるのと同じフォーマットです。

.. The swap file is composed of a given number of pages, where every page size is a
   given number of bytes. This parameters can be changed in redis.conf, since different
   Redis instances may work better with different values: it depends on the actual data
   you store inside it. The following are the default values:

スワップファイルは指定されたサイズ(バイト数)と、指定されたページ数を持つように作られます。これらのパラメータは :file:`redis.conf` の中で変えることができます。実際に格納するデータのサイズによって、適切なサイズは変わってくるでしょう。下の設定がデフォルト値です。

.. code-block:: nginx

   vm-page-size 32
   vm-pages 134217728

.. Redis takes a "bitmap" (an contiguous array of bits set to zero or one) in memory,
   every bit represent a page of the swap file on disk: if a given bit is set to 1, it
   represents a page that is already used (there is some Redis Object stored there),
   while if the corresponding bit is zero, the page is free.

Redisは「ビットマップ」をメモリ中に保持しています。これは、連続したビット列で、ゼロかイチが格納されます。それぞれのビットは、スワップファイル中のページを表します。もし、1がセットされていれば、そのページは既に仕様されていて、Redisのオブジェクトが格納されています。ゼロがセットされている場合は、そのページは利用可能であることを表しています。

.. Taking this bitmap (that will call the page table) in memory is a huge win in terms
   of performances, and the memory used is small: we just need 1 bit for every page on
   disk. For instance in the example below 134217728 pages of 32 bytes each (4GB swap
   file) is using just 16 MB of RAM for the page table.

このビットマップ(ページテーブルと呼ばれます)をメモリ中に持つことで、パフォーマンスの面で優れていると同時に、メモリ使用量も押さえられた実装になっています。ページごとに1ビットしか必要でないため、デフォルトの32ビット、1.3億ページ(4GBのスワップ)が確保された場合でも、ページテーブルは16MBしかありません。

.. Transfering objects from memory to swap

メモリからスワップにオブジェクトを転送する
==========================================

.. In order to transfer an object from memory to disk we need to perform the 
   following steps (assuming non threaded VM, just a simple blocking approach):

オブジェクトをメモリからディスクにスワップする場合は、次のステップで行われます。なお、この説明はブロック処理がシンプルな、スレッドを使わない仮想メモリを想定しています。

.. * Find how many pages are needed in order to store this object on the swap file. 
     This is trivially accomplished just calling the function rdbSavedObjectPages that 
     returns the number of pages used by an object on disk. Note that this function 
     does not duplicate the .rdb saving code just to understand what will be the
     length after an object will be saved on disk, we use the trick of opening
     /dev/null and writing the object there, finally calling ftello in order check
     the amount of bytes required. What we do basically is to save the object on a
     virtual very fast file, that is, /dev/null.

* このオブジェクトをディスクにスワップするには、何ページのブロックが必要かを探します。 :c:func:`rdbSavedObjectPages` 関数がこの計算を行い、オブジェクトが使用することになるページ数を返します。この関数は :file:`.rdb` ファイルに保存するコードの複製、ディスクに保存した後のサイズを計算するものです。この中では、 :file:`/dev/null` にオブジェクトを書き込んで、最後の :c:func:`ftello` を呼び出すことで必要なバイト数を計算するというトリックを使っています。この中で行っているのは基本的に仮想のとても高速なファイルである :file:`/dev/null` への書き込みです。

.. * Now that we know how many pages are required in the swap file, we need to find 
     this number of contiguous free pages inside the swap file. This task is accomplished
     by the vmFindContiguousPages function. As you can guess this function may fail if
     the swap is full, or so fragmented that we can't easily find the required number
     of contiguous free pages. When this happens we just abort the swapping of the
     object, that will continue to live in memory.

* スワップファイル内に、何ページのスペースが必要かが分かったら、次はスワップファイル内の連続したフリーのページを探しに行きます。これを行うのが :c:func:`vmFindContiguousPages` です。この関数は、スワップファイルがいっぱいになっているか、断片化して十分な容量がない場合に失敗します。この場合はスワップ処理が異常終了し、オブジェクトはメモリ内に存在し続けます。

.. * Finally we can write the object on disk, at the specified position, just calling 
     the function vmWriteObjectOnSwap.

最後に、決まった位置にオブジェクトをディスクに書きこみます。これを行うのは :c:func:`vmWriteObjectOnSwap` です。

.. As you can guess once the object was correctly written in the swap file, it is
   freed from memory, the storage field in the associated key is set to REDIS_VM_SWAPPED,
   and the used pages are marked as used in the page table.

オブジェクトがスワップファイルに正しく書き込まれると、メモリは解放されます。関連するキーの ``storage`` 属性には ``REDIS_VM_SWAPPED`` が設定され、 ``usedpages`` にはページテーブル内のページが書き込まれます。

.. Loading objects back in memory

メモリにオブジェクトをロードする
================================

.. Loading an object from swap to memory is simpler, as we already know where the 
   object is located and how many pages it is using. We also know the type of the 
   object (the loading functions are required to know this information, as there is 
   no header or any other information about the object type on disk), but this is 
   stored in the vtype field of the associated key as already seen above.

スワップファイルからメモリにオブジェクトをロードする仕組みはシンプルです。スワップファイルのどこに、何ページ分保存されているかということは既にわかっています。また、オブジェクトの種類(ディスク上にはこの情報は保存されていないため、ロードする関数はこれを知っている必要がある)を知る必要がありますが、これも上記の構造体の ``vtype`` 属性に保存されています。

.. Calling the function vmLoadObject passing the key object associated to the value 
   object we want to load back is enough. The function will also take care of fixing 
   the storage type of the key (that will be REDIS_VM_MEMORY), marking the pages as
   freed in the page table, and so forth.

``key`` オブジェクトを渡して :c:func:`vmLoadObject` 関数を呼べば、ロードは完了します。この関数の中では、保存場所の情報の修正をしたり(``REDIS_VM_MEMORY`` になる)、ページテーブルを解放したりします。

.. The return value of the function is the loaded Redis Object itself, that we'll have to 
   set again as value in the main hash table (instead of the NULL value we put in place
   of the object pointer when the value was originally swapped out).

この関数の返り値はロードされたRedisオブジェクトそのものであり、スワップされたときに ``NULL`` に設定されたメインのハッシュテーブルに設定しなければなりません。

.. How blocking VM works

どのようにブロッキング仮想メモリは動作するのか？
================================================

.. Now we have all the building blocks in order to describe how the blocking VM works.
   First of all, an important detail about configuration. In order to enable blocking
   VM in Redis server.vm_max_threads must be set to zero. We'll see later how this max
   number of threads info is used in the threaded VM, for now all it's needed to now
   is that Redis reverts to fully blocking VM when this is set to zero.

これまでのところで、仮想メモリの動作のブロッキングに必要な材料がそろいました。まず最初に設定の重要なところを紹介します。仮想メモリのブロッキングを有効にするには、Redisサーバの :conf:`vm_max_threads` をゼロに設定する必要があります。スレッド対応の仮想メモリの時に、どのようにこの最大スレッド数の設定が使用されるかは、この後で説明します。この値をゼロにすることで、完全なブロッキングを行う仮想メモリとして動作します。

.. We also need to introduce another important VM parameter, that is, server.vm_max_memory.
   This parameter is very important as it is used in order to trigger swapping: Redis will
   try to swap objects only if it is using more memory than the max memory setting, 
   otherwise there is no need to swap as we are matching the user requested memory usage.

もうひとつの重要な仮想メモリの属性として、 :conf:`vm_max_memory` があります。このパラメータはスワップのトリガーを設定するために重要となります。Redisは、このメモリの設定値を超えたメモリを使用した場合にのみ、スワップを行おうとします。この値に到達しない場合は、スワップの必要はないものとして動作します。

.. Blocking VM swapping

ブロッキング仮想メモリのスワップ
--------------------------------

.. Swapping of object from memory to disk happens in the cron function. This function
   used to be called every second, while in the recent Redis versions on git it is
   called every 100 milliseconds (that is, 10 times per second). If this function
   detects we are out of memory, that is, the memory used is greater than the
   vm-max-memory setting, it starts transferring objects from memory to disk in a loop
   calling the function vmSwapOneObect. This function takes just one argument, if 0 it
   will swap objects in a blocking way, otherwise if it is 1, I/O threads are used.
   In the blocking scenario we just call it with zero as argument.

メモリからディスクへのスワップは、 ``cron`` 関数の中で行われます。現在のバージョンではこの関数は毎秒呼び出されますし、git上の最新バージョンでは100ミリ秒(1秒に10回)呼ばれます。この関数の中で、メモリ使用量の限界(``vm-max-memory`` の設定値)を超えたことが検知されると、ループの中で :c:func:`vmSwapOneObect` を呼び出して、ディスクへの移動を行います。この関数は1つ引き数を取りますが、もし0を渡すと、ブロッキングした状態でスワップを行います。1が設定されると、I/Oスレッドがしようされます。このブロッキング仮想メモリの説明の中では、0が渡されたものとして話を進めます。

.. vmSwapOneObject acts performing the following steps:

:c:func:`vmSwapOneObject` は次のように動作します。

.. * The key space in inspected in order to find a good candidate for swapping (we'll
     see later what a good candidate for swapping is).

* キーのテーブルを探索して、スワップするデータの候補を探す。スワップの候補の選び方は後で紹介します。

.. * The associated value is transfered to disk, in a blocking way.

* ブロックされた中で、ディスクに値を転送する。

.. * The key storage field is set to REDIS_VM_SWAPPED, while the vm fields of the
     object are set to the right values (the page index where the object was swapped,
     and the number of pages used to swap it).

* キーの ``storage`` 属性に ``REDIS_VM_SWAPPED`` をセットし、 ``vm`` 属性の中の変数(ページ番号や、ページ数)に正しい値を設定する。

.. * Finally the value object is freed and the value entry of the hash table is set to NULL.

* 最後に値オブジェクトを会報誌、ハッシュテーブルの値のエントリーに ``NULL`` を設定する。

.. The function is called again and again until one of the following happens: there
   is no way to swap more objects because either the swap file is full or nearly all
   the objects are already transfered on disk, or simply the memory usage is already
   under the vm-max-memory parameter.

この関数は次の状態になるまで繰り返し呼ばれます。

* スワップファイルがいっぱいになった
* すべてのオブジェクトがすでにディスクに転送されている
* メモリ使用量が :conf:`vm-max-memory` の設定よりも少なくなった

.. What values to swap when we are out of memory?

メモリがあふれたときに、どの値をスワップするのか？
--------------------------------------------------

.. Understanding what's a good candidate for swapping is not too hard. A few objects at random are
   sampled, and for each their swappability is commuted as:

スワップする候補を選ぶロジックの理解は難しくありません。いくつかのオブジェクトをランダムでサンプリングし、それぞれの ``swappability`` 値を次のように計算します。

.. code-block:: c

   swappability = age*log(size_in_memory)

.. The age is the number of seconds the key was not requested, while size_in_memory is a fast
   estimation of the amount of memory (in bytes) used by the object in memory. So we try to
   swap out objects that are rarely accessed, and we try to swap bigger objects over smaller
   one, but the latter is a less important factor (because of the logarithmic function used).
   This is because we don't want bigger objects to be swapped out and in too often as the
   bigger the object the more I/O and CPU is required in order to transfer it.

``age`` は最後にアクセスされてからの秒数です。 ``size_in_memory`` はオブジェクトが利用している、メモリのバイト数です。アクセスされる頻度が少なく、大きいオブジェクトほど、スワップされやすくなります。ただし、logをとっているため、大きさの重みは小さくなっています。サイズの大きなオブジェクトを読み書きすることは、I/OやCPUに負荷をかけるので、あまり転送したくはないためです。

.. Blocking VM loading

ブロッキング仮想メモリのロード
------------------------------

.. What happens if an operation against a key associated with a swapped out object is requested?
   For instance Redis may just happen to process the following command:

スワップされたオブジェクトを持つキーに対する命令が発行された場合、どのようなことが行われるのでしょうか？例えば、次のような操作が行われる可能性があります。

.. code-block:: nginx

   GET foo

.. If the value object of the foo key is swapped we need to load it back in memory before
   processing the operation. In Redis the key lookup process is centralized in the lookupKeyRead
   and lookupKeyWrite functions, this two functions are used in the implementation of all the
   Redis commands accessing the keyspace, so we have a single point in the code where to handle
   the loading of the key from the swap file to memory.

``foo`` キーの値オブジェクトがスワップされている場合、操作を実行する前に、メモリにロードし直す必要があります。Redisのキー探索の処理は、 :c:func:`lookupKeyRead()` と、 :c:func:`lookupKeyWrite()` の2つの関数に集約されています。これらの関数は、キー空間にアクセスするすべてのRedisコマンドの実装の中から使用されています。そのため、スワップファイルからメモリにロードする処理も、この場所で行われます。

.. So this is what happens:

次のようなことが行われます。

.. * The user calls some command having as argumenet a swapped key
.. * The command implementation calls the lookup function
.. * The lookup function search for the key in the top level hash table.
     If the value associated with the requested key is swapped 
     (we can see that checking the storage field of the key object),
     we load it back in memory in a blocking way before to return to the user.

* ユーザが、スワップされたキーを引き数に取るコマンドを呼び出す
* コマンドの実装コードから、キー探索関数が呼ばれる
* 探索関数は、トップレベルのハッシュテーブルからキーを探す。もしキーに関連付けられた値がスワップされている場合(``key`` オブジェクトの ``storage`` 属性を見て確認)、ブロックを行い、ユーザに処理が返る前に、メモリにロードしなおす。

.. This is pretty straightforward, but things will get more interesting with the threads.
   From the point of view of the blocking VM the only real problem is the saving of the
   dataset using another process, that is, handling BGSAVE and BGREWRITEAOF commands.

この場合は極めて素直な処理になっていますが、スレッドが絡んでくると、もっと動きが楽しくなってきます。ブロッキング仮想メモリの観点で見ると、 :com:`BGSAVE` や、 :com:`BGREWRITEAOF` コマンドなどにより、データセットが別のプロセスから保存されることだけが注意すべきことになります。

.. Background saving when VM is active

仮想メモリがアクティブな時の、バックグラウンドセーブ
----------------------------------------------------

.. The default Redis way to persist on disk is to create .rdb files using a child process.
   Redis calls the fork() system call in order to create a child, that has the exact copy
   of the in memory dataset, since fork duplicates the whole program memory space (actually
   thanks to a technique called Copy on Write memory pages are shared between the parent and
   child process, so the fork() call will not require too much memory).

Redisはデフォルトでは、子プロセスを使って、ディスク上に :file:`.rdb` ファイルを作って、保存をします。Redis()は :c:func:`fork` システムコールを呼び出して子プロセスを作ります。このとき、プログラムのメモリ空間が複製されます。(実際には、copy on writeと呼ばれる技術により、親プロセスと子プロセスの間ではメモリが共有されるため、forkが使用するメモリは2倍にはなりません。)

.. In the child process we have a copy of the dataset in a given point in the time. Other
   commands issued by clients will just be served by the parent process and will not modify
   the child data.

子プロセスでは、forkされたタイミングでのデータセットのコピーを持っています。クライアントから何かコマンドを受け取って、親プロセスが処理を行ったとしても、子のデータは変更されません。

.. The child process will just store the whole dataset into the dump.rdb file and finally will
   exit. But what happens when the VM is active? Values can be swapped out so we don't have all
   the data in memory, and we need to access the swap file in order to retrieve the swapped values.
   While child process is saving the swap file is shared between the parent and child process, since:

子プロセスはすべてのデータセットを、 :file:`dump.rdb` ファイルにダンプして終了します。もし仮想メモリがアクティブになっている場合、何が起きるのでしょうか？値がスワップされているため、すべてのデータがメモリに格納されているわけではありません。そのため、スワップされた値を読み込むためには、スワップファイルにアクセスしなければなりません。

.. * The parent process needs to access the swap file in order to load values back 
     into memory if an operation against swapped out values are performed.

* 親プロセスも、スワップされた値を処理する時は、スワップファイルにアクセスする必要があります。

.. * The child process needs to access the swap file in order to retrieve the 
     full dataset while saving the data set on disk.

* 子プロセスも、全データセットをディスクに保存する場合に、スワップファイルにアクセスする必要があります。

.. In order to avoid problems while both the processes are accessing the same swap file we do a 
   simple thing, that is, not allowing values to be swapped out in the parent process while a 
   background saving is in progress. This way both the processes will access the swap file in 
   read only. This approach has the problem that while the child process is saving no new values
   can be transfered on the swap file even if Redis is using more memory than the max memory 
   parameters dictates. This is usually not a problem as the background saving will terminate
   in a short amount of time and if still needed a percentage of values will be swapped on disk ASAP.

同じスワップファイルに同時にアクセスする問題を避けるために、Redisではバックグラウンドセーブを行っているあいだは、親プロセスが値をスワップアウトすることを許可しない、というシンプルな方法を採用しています。この場合、両方のプロセスは、読み込み専用でのアクセスすることになります。このアプローチでは、子プロセスが保存をしているあいだは、親プロセスが一時的に最大メモリ使用量のパラメータ以上のメモリを使用してしまう可能性がある、という問題があります。ですが、バックグラウンドのセーブは短時間で終了されるため、あまり問題になりませんし、スワップが必要であれば、すぐにスワップが行われるでしょう。

.. An alternative to this scenario is to enable the Append Only File that will have this 
   problem only when a log rewrite is performed using the BGREWRITEAOF command.

追記専用ファイルモードを有効にしていると、 :com:`BGREWRITEAOF` コマンドを実行して、ログの再書き込みをしている場合にのみ、この問題が起きる可能性があります。

.. The problem with the blocking VM

ブロッキング仮想メモリの問題
----------------------------

.. The problem of blocking VM is that... it's blocking :) This is not a problem when Redis
   is used in batch processing activities, but for real-time usage one of the good points of
   Redis is the low latency. The blocking VM will have bad latency behaviors as when a client
   is accessing a swapped out value, or when Redis needs to swap out values, no other clients
   will be served in the meantime.

ブロッキング仮想メモリの問題は・・・ブロッキングすることです :) これは、Redisをバッチプロセスに対して使用している場合には問題になりませんが、遅延時間が少ないことが要求される場面で、リアルタイムにどんどん処理を行うようなRedisサーバを運用している場合は、問題となるでしょう。ブロッキング仮想メモリは、クライアントがスワップされた値にアクセスする命令が送ったり、Redisが値をスワップする必要がある場合、他のクライアントに対するサービスが止まるため、非常に処理が遅くなります。

.. Swapping out keys should happen in background. Similarly when a client is accessing a
   swapped out value other clients accessing in memory values should be served mostly as
   fast as when VM is disabled. Only the clients dealing with swapped out keys should be delayed.

スワップはバックグラウンドで行われるべきです。また、スワップされた値にアクセスされている時に、他のクライアントからメモリ上にある値へのアクセスが行われても、仮想メモリがオフになっているときと同じぐらい高速で行われるべきです。スワップされたキーに対するアクセスがあったときの遅延だけが許されます。

.. All this limitations called for a non-blocking VM implementation.

このような制約をすべて回避したいですよね？　ノンブロッキング仮想メモリ実装の出番です。

.. Threaded VM

スレッド対応仮想メモリ
======================

.. There are basically three main ways to turn the blocking VM into a non blocking one.

ブロッキング仮想メモリを、ノンブロッキング仮想メモリにするには、主に次の3通りの方法があります。

.. 1. One way is obvious, and in my opionion, not a good idea at all, that is, turning 
      Redis itself into a theaded server: if every request is served by a different
      thread automatically other clients don't need to wait for blocked ones. 
      Redis is fast, exports atomic operations, has no locks, and is just 10k
      lines of code, because it is single threaded, so this was not an option for me.

1. 1つ目の方法はRedis自身をスレッド化したサーバとして実装する方法です。もし、すべてのリクエストを異なるスレッドで自動で処理するようになれば、クライアントは他のクライアントによるブロックを待つ必要がなくなります。これは、分かりやすいのですが、私の意見ではあまり良いアイディアではありません。Redisは高速で、アトミックな操作を行えるようにしています。この1万行ほどのコードはシングルスレッドで処理されるため、この中ではロックが行わないで処理されます。そのため、これは私の選択肢には入りません。

.. 2: Using non-blocking I/O against the swap file. After all you can think Redis already
    event-loop based, why don't just handle disk I/O in a non-blocking fashion? I also
    discarded this possiblity because of two main reasons. One is that non blocking file
    operations, unlike sockets, are an incompatibility nightmare. It's not just like calling
    select, you need to use OS-specific things. The other problem is that the I/O is just one
    part of the time consumed to handle VM, another big part is the CPU used in order to
    encode/decode data to/from the swap file. This is I picked option three, that is...

2. スワップファイルに対して、ノンブロッキングI/Oを使用します。Redisはすでにイベントループベースの実装になっているため、なぜノンブロッキングな方法でディスクI/Oを扱わないのでしょうか？私は、次に挙げる2つの理由から、この選択肢を捨てました。一つ目は、ノンブロッキングなファイル操作は、ソケットとは異なり、不一致による悪夢が起きる、ということです。単に :c:func:`select` を呼べば良いというだけではなく、OS依存のAPIを使う必要があります。他の問題は、I/Oは仮想メモリを取り扱うために消費する時間の一部(残りはスワップファイルの入出力時のデータのエンコード/デコードにかかるCPU時間)を占めているということです。このため、私は3番目の選択肢を選ぶことにしました。

.. 3: Using I/O threads, that is, a pool of threads handling the swap I/O operations. 
      This is what the Redis VM is using, so let's detail how this works.

3. I/Oスレッドを使用します。スワップの入出力操作を行うための、スレッドプールを用意します。Redis仮想メモリの実装で利用されているのは、これです。それでは、この仕組の動きの詳細を説明します。

.. I/O Threads

I/Oスレッド
-----------

.. The threaded VM design goals where the following, in order of importance:

スレッド化された仮想メモリは、次のような目標を掲げて設計されました。重要度順になっています。

.. * Simple implementation, little room for race condtions, simple locking, 
     VM system more or less completeley decoupled from the rest of Redis code.

* シンプルな実装。競合状態が少なく、ロックがシンプルで、仮想メモリのシステムがなるべく完全に他のRedisコードと疎になる。

.. * Good performances, no locks for clients accessing values in memory.

* 良いパフォーマンス。メモリ内の値にクライアントがアクセスする場合に、ロックされない。

.. * Ability to decode/encode objects in the I/O threads.

* オブジェクトのデコード/エンコードはI/Oスレッド上で行う

.. The above goals resulted in an implementation where the Redis main thread (the one serving
   actual clients) and the I/O threads communicate using a queue of jobs, with a single mutex.
   Basically when main thread requires some work done in the background by some I/O thread, it
   pushes an I/O job structure in the server.io_newjobs queue (that is, just a linked list). If
   there are no active I/O threads, one is started. At this point some I/O thread will process the
   I/O job, and the result of the processing is pushed in the server.io_processed queue. The I/O
   thread will send a byte using an UNIX pipe to the main thread in order to signal that a new job
   was processed and the result is ready to be processed.

このような目標を目指して実装したところ、Redisのメインスレッドと、I/Oスレッドがキューと、1つのミューテックスを使ってジョブのやりとりをする、という実装になりました。基本的には、メインスレッドが、バックグラウンドのI/Oスレッドにお願いしたい仕事を持った場合、I/Oジョブ構造体を、 ``server.io_newjobs`` キュー(単なるリンクドリスト)に積みます。アクティブなI/Oスレッドがなければ、スレッドを起動します。この時に、I/OスレッドがI/Oジョブを処理して、 ``server.io_processed`` キューに結果を積みます。I/Oスレッドは、UNIXパイプにデータを送ることによって、メインスレッドに対して新しいジョブが実行され、処理が終わったことを通知します。

.. This is how the iojob structure looks like:

``iojob`` 構造体は次のような実装になっています。

.. 
   typedef struct iojob {
       int type;   /* Request type, REDIS_IOJOB_* */
       redisDb *db;/* Redis database */
       robj *key;  /* This I/O request is about swapping this key */
       robj *val;  /* the value to swap for REDIS_IOREQ_*_SWAP, otherwise this
                    * field is populated by the I/O thread for REDIS_IOREQ_LOAD. */
       off_t page; /* Swap page where to read/write the object */
       off_t pages; /* Swap pages needed to save object. PREPARE_SWAP return val */
       int canceled; /* True if this command was canceled by blocking side of VM */
       pthread_t thread; /* ID of the thread processing this entry */
   } iojob;

.. code-block:: c

   typedef struct iojob {
       int type;   /* リクエストタイプ, REDIS_IOJOB_* */
       redisDb *db;/* Redisデータベース*/
       robj *key;  /* どのキーをスワップするI/Oリクエストか？ */
       robj *val;  /* REDIS_IOREQ_*_SWAPコマンドによって処理される値オブジェクト。
                    * もしくは、REDIS_IOREQ_LOADの処理を行うI/Oスレッド
                    * がこの変数に値を設定する。 */
       off_t page; /* オブジェクトの読み/書きを行うページ番号 */
       off_t pages; /* オブジェクトを保存するのに必要なページ数。PREPARE_SWAPの返り値 */
       int canceled; /* ブロッキング仮想メモリが処理をキャンセルしたいときに、
                      * 値を設定する。 */
       pthread_t thread; /* このエントリーを処理する、スレッドのID */
   } iojob;

.. There are just three type of jobs that an I/O thread can perform 
   (the type is specified by the type field of the structure):

I/Oスレッドによって実行可能なジョブは、次の3種類あります。これは ``type`` 属性で設定されます。

.. REDIS_IOJOB_LOAD: load the value associated to a given key from swap to memory. 
   The object offset inside the swap file is page, the object type is key->vtype. 
   The result of this operation will populate the val field of the structure.

``REDIS_IOJOB_LOAD`` 
   与えられたキーの値を、スワップファイルからメモリに読み込みます。スワップファイル内の位置は ``page`` 属性に、オブジェクトの種類は ``key->vtype`` に格納されています。処理の結果は、構造体の ``val`` 属性に格納されます。

.. REDIS_IOJOB_PREPARE_SWAP: compute the number of pages needed in order to save 
   the object pointed by val into the swap. The result of this operation will 
   populate the pages field.

``REDIS_IOJOB_PREPARE_SWAP``
   ``val`` 属性に格納されているオブジェクトをスワップに保存するために、必要なページ数を計算します。処理の結果は ``pages`` フィールドに格納されます。

.. REDIS_IOJOB_DO_SWAP: Transfer the object pointed by val to the swap file, at page offset page.

``REDIS_IOJOB_DO_SWAP``
   ``val`` 属性に格納されているオブジェクトを、スワップファイルの ``page`` で指定されたオフセットのページに送ります。

.. The main thread delegates just the above three tasks. All the rest is handled by the main thread 
   itself, for instance finding a suitable range of free pages in the swap file page table (that is 
   a fast operation), deciding what object to swap, altering the storage field of a Redis object to 
   reflect the current state of a value.

メインスレッドは、上記の3つのタスクだけを委譲します。スワップファイルの格納する場所を探したり、スワップするオブジェクトを決定したり、Redisオブジェクトの ``storage`` 属性の値に、現在の状態を反映したりといった残りの処理はすべてメインスレッド自身が行います。

.. Non blocking VM as probabilistic enhancement of blocking VM

ブロッキング仮想メモリの確率論的拡張としてのノンブロッキング仮想メモリ
----------------------------------------------------------------------

.. So now we have a way to request background jobs dealing with slow VM operations. How to add this 
   to the mix of the rest of the work done by the main thread? While blocking VM was aware that an 
   object was swapped out just when the object was looked up, this is too late for us: in C it is 
   not trivial to start a background job in the middle of the command, leave the function, and 
   re-enter in the same point the computation when the I/O thread finished what we requested (that 
   is, no co-routines or continuations or alike).

ここまでのところで、処理の重い仮想メモリの操作を、バックグラウンドジョブとして処理できるようになりました。どのようにして、メインスレッドで行う他の処理と歩調を合わせて行くのでしょうか？ブロッキング仮想メモリの場合、検索している時にオブジェクトがスワップアウトされていることに気づきますが、これでは遅すぎます。C言語では、コルーチンや継続がないため、コマンド処理の途中でバックグラウンドのジョブを起動して、関数の実行を中断し、I/Oスレッドの処理が終わったタイミングで中断したポイントから処理を再開するということは簡単ではありません。

.. Fortunately there was a much, much simpler way to do this. And we love simple things: basically 
   consider the VM implementation a blocking one, but add an optimization (using non the no blocking 
   VM operations we are able to perform) to make the blocking very unlikely.

再話、もっと簡単な方法がありました。私たちはシンプルな方が好きです。仮想メモリの実装は、基本的にブロッキング仮想メモリと考えますが、ブロッキングが発生していないように見えるように最適化します。

.. This is what we do:

行っていることは次の通りです。

.. * Every time a client sends us a command, before the command is executed, we examine the argument 
     vector of the command in search for swapped keys. After all we know for every command what 
     arguments are keys, as the Redis command format is pretty simple.

* クライアントからコマンドが送信されるたびに、コマンド実行前に、コマンドの引き数リストに含まれるキーが、スワップされたものではないか確認します。Redisのコマンドの形式がシンプルであるため、コマンドごとに、どの引き数がキーを表しているかは知っています。

.. * If we detect that at least a key in the requested command is swapped on disk, we block the 
     client instead of really issuing the command. For every swapped value associated to a 
     requested key, an I/O job is created, in order to bring the values back in memory. The 
     main thread continues the execution of the event loop, without caring about the blocked client.

* もし、要求されたコマンドで渡されたキーがスワップされていることを検出したら、コマンドを実行する代わりに一端クライアントをブロックします。スワップされた値に関連するキーごとに、メモリに戻すためのI/Oジョブが作られます。この間も、ブロックされたクライアントのことは気にしないで、メインスレッドのイベントループの実行は継続されます。

.. * In the meanwhile, I/O threads are loading values in memory. Every time an I/O thread 
     finished loading a value, it sends a byte to the main thread using an UNIX pipe. The 
     pipe file descriptor has a readable event associated in the main thread event loop, that
     is the function vmThreadedIOCompletedJob. If this function detects that all the values needed
     for a blocked client were loaded, the client is restarted and the original command called.

* その間、I/Oスレッドはメモリの値をロードします。I/Oスレッドが値をロードし終えたら、UNIXパイプに1バイトのデータを送信します。vmThreadedIOCompletedJob関数の中で、パイプファイルディスクリプタは、メインスレッドのイベントループに関連付けられた、読み込み可能なイベントを保持します。もしこの関数が、ブロックされたクライアントに必要なすべての値の読み込みを検知したら、クライアントの起動は再開し、元のコマンドを呼び出します。

.. So you can think at this as a blocked VM that almost always happen to have the right keys 
   in memory, since we pause clients that are going to issue commands about swapped out values 
   until this values are loaded.

スワップされた値を使うコマンドが発生すると、値がロードされるまではクライアントの動作が一時停止するため、正しいキーがメモリ上置かれているブロッキング仮想メモリとほぼ同じように考えることができます。

.. If the function checking what argument is a key fails in some way, there is no problem: the 
   lookup function will see that a given key is associated to a swapped out value and will block
   loading it. So our non blocking VM reverts to a blocking one when it is not possible to
   anticipate what keys are touched.

どの引き数がキーかを調べる関数が失敗しても問題はありません。ルックアップの関数は与えられたキーの値がスワップされていることを気づいて、ブロックしてそれをロードしにいきます。そのため、利用しようとしたキーが利用できない場合には、ブロッキング仮想メモリに戻ります。

.. For instance in the case of the SORT command used together with the GET or BY options, it
   is not trivial to know beforehand what keys will be requested, so at least in the first
   implementation, SORT BY/GET resorts to the blocking VM implementation.

たとえば、 ``GET`` や ``BY`` オプション付きの :com:`SORT` コマンドの場合、どのキーが必要となるかを事前に把握することが困難なため、少なくとも最初の実装では、 ``SORT BY/GET`` の実行はブロッキング仮想メモリとして実行されます。

.. Blocking clients on swapped keys

クライアントのブロック
----------------------

.. How to block clients? To suspend a client in an event-loop based server is pretty trivial. 
   All we do is cancelling its read handler. Sometimes we do something different (for instance
   for BLPOP) that is just marking the client as blocked, but not processing new data (just
   accumulating the new data into input buffers).

どのようにクライアントをブロックしているのでしょうか？サーバ上のイベントループで、クライアントを一時停止させるのはとても簡単です。読み込みハンドラをキャンセルします。例えば、 :com:`BLPOP` のようなコマンドの場合は、これとは異なり、新しいデータを処理(新しいデータを入力バッファ積む)するのではなく、単にブロックしているとクライアントにマークを付けるだけの場合もあります。

.. Aborting I/O jobs

I/Oジョブの中断
---------------

.. There is something hard to solve about the interactions between our blocking and non blocking
   VM, that is, what happens if a blocking operation starts about a key that is also
   "interested" by a non blocking operation at the same time?

ブロッキング仮想メモリと、ノンブロッキング仮想メモリの間でインタラクションすることは、簡単ではありません。ノンブロッキング命令と、ブロッキング命令が同じキーに対して同時に発生すると何が起きるでしょうか？

.. For instance while SORT BY is executed, a few keys are being loaded in a blocking manner by the
   sort command. At the same time, another client may request the same keys with a simple GET key
   command, that will trigger the creation of an I/O job to load the key in background.

例えば、 :com:`SORT` ``BY`` が実行されていると、いくつかのキーは :com:`SORT` コマンドの流儀に従って、ブロッキング仮想メモリの仕組みをつかってロードされます。これと同時に、同じキーに対して、値をスワップからロードする場合にI/Oジョブを作って行う :com:`GET`
コマンドが他のクライアントから呼ばれたとします。

.. The only simple way to deal with this problem is to be able to kill I/O jobs in the main thread,
   so that if a key that we want to load or swap in a blocking way is in the REDIS_VM_LOADING or
   REDIS_VM_SWAPPING state (that is, there is an I/O job about this key), we can just kill the
   I/O job about this key, and go ahead with the blocking operation we want to perform.

この問題を解決する唯一シンプルな方法は、メインスレッドからI/Oジョブをkillできるようにすることです。もしブロッキング仮想メモリキーをロードしたり、スワップしたい場合には、 ``REDIS_VM_LOADING`` や ``REDIS_VM_SWAPPING`` といったフラグを設定します。ここで、このキーに関するI/Oジョブをkillして、実行したいブロッキング操作を行います。

.. This is not as trivial as it is. In a given moment an I/O job can be in one of the following three queues:

これは言うほど簡単ではありません。これを行おうとした瞬間、I/Oジョブは次の3つのうち、どれかの状態になります。

.. * server.io_newjobs: the job was already queued but no thread is handling it.
   * server.io_processing: the job is being processed by an I/O thread.
   * server.io_processed: the job was already processed.

* server.io_newjobs: ジョブがキューに入れられただけの状態で、スレッドはまだ処理していません。
* server.io_processing: ジョブは今現在、I/Oスレッドによって処理されています。
* server.io_processed: ジョブはすでに完了しています。

.. The function able to kill an I/O job is vmCancelThreadedIOJob, and this is what it does:

I/Oジョブは、 :c:func:`vmCancelThreadedIOJob` を使ってkillすることができます。

.. * If the job is in the newjobs queue, that's simple, removing the iojob structure from the
     queue is enough as no thread is still executing any operation.
   * If the job is in the processing queue, a thread is messing with our job (and possibly
     with the associated object!). The only thing we can do is waiting for the item to move
     to the next queue in a blocking way. Fortunately this condition happens very rarely so
     it's not a performance problem.
   * If the job is in the processed queue, we just mark it as canceled marking setting the
     canceled field to 1 in the iojob structure. The function processing completed jobs will
     just ignored and free the job instead of really processing it.

* Jobがまだにnewjobsのキューに格納されている状態であれば、スレッドはこのジョブの処理をまったく行っていないため、キューからiojob構造体を削除するだけでkillすることができます。
* もしジョブがprocessingキューにある場合は、スレッドが我々の仕事に干渉してきています。関連するオブジェクトに対して処理を行っている可能性もあります。ここで行えることは、ブロッキングされた方法で、次のキューに移動されるのを待つことだけです。幸い、このようなことが起きる確率は極めて低いため、パフォーマンス上の問題となることはありません。
* もし、ジョブがprocessedキューにある場合は、iojob構造体の ``canceled`` 属性に1をセットし、キャンセルされたとするマークをつけます。これにより、完了したジョブが実行されるぜに、無視されるようになり、ジョブの構造体が開放されるようになります。
