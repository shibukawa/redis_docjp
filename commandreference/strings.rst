.. -*- coding: utf-8 -*-;

.. Redis String Type

.. index::
   pair: データ型; 文字列型

.. _strings:

==========
 文字列型
==========

.. Strings are the most basic Redis kind of values. Redis Strings are binary safe, this means a Redis string can contain any kind of data, for instance a JPEG image or a serialized Ruby object, and so forth.

文字列型はRedisで扱う型の中で最も基本的なものです。Redis文字列型はバイナリセーフです。つまりRedis文字列型はどんな種類のデータも保持できるということです。たとえばJPEGイメージやシリアライズされたRubyオブジェクトなども持つことができます。

.. A String value can be at max 1 Gigabyte in length.

文字列は最大1GBまで扱うことが出来ます。

.. Strings are treated as integer values by the INCR commands family, in this respect the value of an intger is limited to a singed 64 bit value.

文字列型は :com:`INCR` コマンド群からは整数値として扱われます。この点において、整数値は符号付き64bit値に制限されます。

.. Note that the single elements contained in Redis Lists, Sets and Sorted Sets, are Redis Strings.

Redisリスト型、Redisセット型、Redisソート済みセット型、Redisハッシュ表型で保持される各要素はRedis文字列型であることを覚えておいてください。

.. Implementation details

実装の詳細
============

.. Strings are implemented using a dynamic strings library called sds.c (simple dynamic strings). This library caches the current length of the string, so to obtain the length of a Redis string is an O(1) operation (but currently there is no such STRLEN command. It will likely be added later).

Redis文字列型は ``sds.c`` (simple dynamic strings) という動的文字列ライブラリを用いて実装されています。このライブラリは文字列のある時点での長さをキャッシュするので、Redis文字列型の長さの取得はO(1)の操作となっています。（現在 :com:`STRLEN` コマンドはないですが、そのうち実装されると思います）

.. Redis strings are incapsualted into Redis Objects. Redis Objects use a reference counting memory management system, so a single Redis String can be shared in different places of the dataset. This means that if you happen to use the same strings many times (especially if you have object sharing turned on in the configuration file) Redis will try to use the same string object instead to allocate one new every time.

Redis文字列はRedisオブジェクト内にカプセル化されています。Redisオブジェクトは参照カウントのメモり管理システムを持っているので、１つのRedisストリングは異なるデータセット内で共有されても大丈夫です。つまり、同じ文字列をたくさん使いたい場合には、Redisは同じ文字列を毎回作成してアロケートするのではなく、１つの文字列を使い回そうとします。（設定ファイル内でオブジェクトの共有の項目をオンにしている場合です）

.. Starting from version 1.1 Redis is also able to encode in a special way strings that are actually just numbers. Instead to save the string as an array of characters Redis will save the integer value in order to use less memory. With many datasets this can reduce the memory usage of about 30% compared to Redis 1.0.

バージョン1.1からRedisでは文字列を特別な方法でエンコードして数値のみの形にすることができるようになりました。メモリ使用量を減らすために文字列を文字の配列として保存する代わりに、Redisは整数値を保存しています。これによって、Redis 1.0と比較してメモリ使用量を30%減らすことができました。


文字列型のコマンド
====================

.. command:: SET key value

   計算時間: O(1)

   .. Set the string value as value of the key. The string can't be longer than 1073741824 bytes (1 GB).

   文字列値 ``value`` をキー ``key`` にセットします。文字列は1073741824バイト(1GB)以下でなければいけません。

   **返り値**

     Status code replyを返す。


.. command:: GET key

   計算時間: O(1)

   .. Get the value of the specified key. If the key does not exist the special value 'nil' is returned. If the value stored at key is not a string an error is returned because GET can only handle string values.

   指定したキー ``key`` に対応する値を取得します。もしキーが存在しなかったら特別な値 "nil" を返します。もしキーに対応する値が文字列型ではなかったらエラーが返ります。なぜなら :com:`GET` は文字列型にしか対応していないからです。

   **返り値**

     Bulk replyを返す。


.. command:: GETSET key value

   計算時間: O(1)

   .. GETSET is an atomic set this value and return the old value command. Set key to the string value and return the old value stored at key. The string can't be longer than 1073741824 bytes (1 GB).

   :com:`GETSET` はキー ``key`` に新しい値 ``value`` をセットして、そのキーにセットされていた古い値を返すアトミックなコマンドです。文字列型は1073741824バイト（1GB）以下でなければなりません。

   .. Return value

   **返り値**

     Bulk replyが返ります。

   .. Design patterns

   **デザインパターン**

   .. GETSET can be used together with INCR for counting with atomic reset when a given condition arises. For example a process may call INCR against the key mycounter every time some event occurred, but from time to time we need to get the value of the counter and reset it to zero atomically using GETSET mycounter 0.

     :com:`GETSET` は :com:`INCR` と一緒に使ってある条件の時にアトミックにリセットするカウンターを作ることができます。たとえば、あるプロセスがあるイベントが起きるたびに :com:`INCR` をキー ``mycounter`` に対して呼び出すとします。しかし時々その値を取り出して自動的にゼロにリセットしたい、というようなときに ``GETSET mycounter 0`` として使うのです。


.. command:: MGET key1 key2 ... keyN

   計算時間: キー1つにつきO(1)

   .. Get the values of all the specified keys. If one or more keys dont exist or is not of type String, a 'nil' value is returned instead of the value of the specified key, but the operation never fails.

   指定したすべてのキー ``keyN`` にひもづいた値を取得します。もし一つ以上のキーが存在しない、または紐づいた値が文字列型でない場合 "nil" が返ってきます。操作が失敗で終了することはありません。

   .. Return value

   **返り値**

     Multi bulk replyが返ります。

   .. Example

   例::

     $ ./redis-cli set foo 1000
     +OK
     $ ./redis-cli set bar 2000
     +OK
     $ ./redis-cli mget foo bar
     1. 1000
     2. 2000
     $ ./redis-cli mget foo bar nokey
     1. 1000
     2. 2000
     3. (nil)
     $


.. command:: SETNX key value

   計算時間: O(1)

   .. SETNX works exactly like SET with the only difference that if the key already exists no operation is performed. SETNX actually means "SET if Not eXists".

   :com:`SETNX` は :com:`SET` と似たコマンドです。唯一の違いはキーが存在する場合は処理が行われない点です。 :com:`SETNX` の意味は "SET if Not eXists" です。


   **返り値**
   
     Integer が帰って来ます。具体的には下記::

       1 if the key was set
       0 if the key was not set

   .. Design pattern: Implementing locking with SETNX

   **デザインパターン: SETNXを用いてロックを実装する**

     .. SETNX can also be seen as a locking primitive. For instance to acquire the lock of the key foo, the client could try the following:

     :com:`SETNX` はロックのためのプリミティブとみなすこともできます。たとえば ``foo`` というキーのロックを取得するには、クライアントは次のように書くことができます::

       SETNX lock.foo <current UNIX time + lock timeout + 1>

     .. If SETNX returns 1 the client acquired the lock, setting the lock.foo key to the UNIX time at witch the lock should no longer be considered valid. The client will later use DEL lock.foo in order to release the lock.

     :com:`SETNX` はクライアントがロックを取得したら1を返し、 ``lock.foo`` というキーにUNIX時間をセットし、その時間からロックが他のクライアントから収得できない状況にします。クライアントは :com:`DEL` を使って ``look.foo`` を削除しロックをリリースします。

      .. If SETNX returns 0 the key is already locked by some other client. We can either return to the caller if it's a non blocking lock, or enter a loop retrying to hold the lock until we succeed or some kind of timeout expires.

      もし :com:`SETNX` が0を返した場合はロックが他のクライアントに既に収得されていることを意味します。この場合、呼び出し元にノンブロッキングロックを返すかタイムアウトするかロックを無事取得できるまでリトライを繰り返すかどちらかになるでしょう。

      
   .. Handling deadlocks


   **デッドロックを扱う**

   .. In the above locking algorithm there is a problem: what happens if a client fails, crashes, or is otherwise not able to release the lock? It's possible to detect this condition because the lock key contains a UNIX timestamp. If such a timestamp is <= the current Unix time the lock is no longer valid.

   上記のロックアルゴリズムでは問題があります。クライアントが失敗したり、クラッシュしたり、とにかくロックを解放できなくなった場合どうなるでしょうか。ロックキーはUNIX時間を保持しているのでこの状況を検知することは可能です。もしタイムスタンプが現在のUNIX時間以前のものであれば、ロックを取得することはできません。

   .. When this happens we can't just call DEL against the key to remove the lock and then try to issue a SETNX, as there is a race condition here, when multiple clients detected an expired lock and are trying to release it.
   
   このような状況が起きた時は競合状態なので、そのキーに対して単純に :com:`DEL` を呼び出すことはできません。代わりに :com:`SETNX` を呼びます。

   .. * C1 and C2 read lock.foo to check the timestamp, because SETNX returned 0 to both C1 and C2, as the lock is still hold by C3 that crashed after holding the lock.
   .. * C1 sends DEL lock.foo
   .. * C1 sends SETNX => success!
   .. * C2 sends DEL lock.foo
   .. * C2 sends SETNX => success!
   .. * ERROR: both C1 and C2 acquired the lock because of the race condition.

   * :com:`SETNX` がC1とC2に0を返すので、C1とC2がlock.fooを読み取ってタイムスタンプを確認します。これはC3がロックを取得した後にクラッシュしてそのままになってしまったことによります。

   * C1が ``DEL lock.foo`` を呼び出します

   * C1が ``SETNX`` を呼び出します => 成功！

   * C2が ``DEL lock.foo`` を呼び出します

   * C2が ``SETNX`` を呼び出します => 成功！

   * ERROR: 競合状態だったのでC1とC2がロックを取得しました

   .. Fortunately it's possible to avoid this issue using the following algorithm. Let's see how C4, our sane client, uses the good algorithm:

   幸いにも、このような問題は以下のようなアルゴリズムを使うことで避けられます。試しに良識あるクライアントC4が参加した場合にこのアルゴリズムを使ったとしてどうなるか、見てみましょう::

   .. - C4 sends SETNX lock.foo in order to acquire the lock
   .. - The crashed C3 client still holds it, so Redis will reply with 0 to C4.
   .. - C4 GET lock.foo to check if the lock expired. If not it will sleep one second (for instance) and retry from the start.
   .. - If instead the lock is expired because the UNIX time at lock.foo is older than the current UNIX time, C4 tries to perform GETSET lock.foo <current unix timestamp + lock timeout + 1>
   .. - Thanks to the GETSET command semantic C4 can check if the old value stored at key is still an expired timestamp. If so we acquired the lock!
   .. - Otherwise if another client, for instance C5, was faster than C4 and acquired the lock with the GETSET operation, C4 GETSET operation will return a non expired timestamp. C4 will simply restart from the first step. Note that even if C4 set the key a bit a few seconds in the future this is not a problem.

   * C4がロックを取得するために ``SETNX lock.foo`` を送ります

   * クラッシュしたクライアントC3がまだロックを保持しています。なのでRedisはC4に0を返します。

   * C4は ``GET lock.foo`` を送ってロックの有効期限が切れたか確認します。もし（たとえば）取得に1秒かかったとしたら始めからやり直します。

   * もしロックlock.fooのUNIX時間が現在のUNIX時間よりも昔のもので有効期限切れになっているとわかったら、C4は ``GETSET lock.foo <現在のUNIX時間 + ロックのタイムアウト + 1>`` の呼び出しを試みます

   * :com:`GETSET` コマンドのおかげで、C4には有効期限切れの値がセットされていたか確認できます。もし確認できたら、ロックを取得できたということになります！

   * あるいはもし他のクライアントC5がC4よりも早く :com:`GETSET` コマンドを発行してロックを収得してしまったら、C4の :com:`GETSET` の操作は有効期限切れでないタイムスタンプを返します。C4は単純に手順を最初からやり直します。ここでC4がキーに値をセットしてしまったとしても、ちょっと経てばこれは問題にならないということに注意してください。

  .. IMPORTANT NOTE: In order to make this locking algorithm more robust, a client holding a lock should always check the timeout didn't expired before to unlock the key with DEL because client failures can be complex, not just crashing but also blocking a lot of time against some operation and trying to issue DEL after a lot of time (when the LOCK is already hold by some other client).

  .. warning:: このロック機構をよりロバストにするために、ロックを保持しているクライアントはロックを解放するために :com:`DEL` を実行する前にタイムアウト時間が有効期限切れになっていないか常に確認すべきです。なぜならクライアントのクライアントの失敗は複雑になりがちで、単純にクラッシュするだけじゃなく多くの操作に対してなギア何度もブロックをかけてしまったり、さらにはそのあと何回も ``DEL`` を発行しようとしたりしてしまいます。（ロックが既にほかのクライアントに保持されているときの話です）

