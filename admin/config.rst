============
設定ファイル
============

単位について
============

.. Note on units: when memory size is needed, it is possible to specifiy
   it in the usual form of 1k 5GB 4M and so forth:

メモリサイズが飛鳥となる部分では、 ``1k`` 、 ``5GB`` 、``4MB`` など、良く使われる方法で設定することができます。

.. 1k => 1000 bytes
   1kb => 1024 bytes
   1m => 1000000 bytes
   1mb => 1024*1024 bytes
   1g => 1000000000 bytes
   1gb => 1024*1024*1024 bytes

.. list-table::
   
   - * 1k
     * 1,000バイト
   - * 1kb
     * 1,024バイト
   - * 1m
     * 1,000,000バイト
   - * 1mb
     * 1,024 * 1,024バイト
   - * 1g
     * 1,000,000,000バイト
   - * 1gb
     * 1,024 * 1,024 * 1,024バイト

.. units are case insensitive so 1GB 1Gb 1gB are all the same.

単位に関しては大文字、小文字の区別はしないため、 ``1GB`` 、 ``1Gb`` 、 ``1gB`` はどれも同じ意味になります。

起動モード設定
==============

.. confval:: daemonize yes/no

   .. By default Redis does not run as a daemon. Use 'yes' if you need it.
      Note that Redis will write a pid file in /var/run/redis.pid when 
      daemonized.

   デフォルトではRedisは通常のプログラムとして動作します。必要に応じて ``'yes'`` を設定してください。デーモンとして動作する場合は、Redisはpidを :file:`/var/run/redis.pid` に書き込みます。

   .. code-block:: nginx
 
      daemonize no

.. confval:: pidfile filename

   .. When running daemonized, Redis writes a pid file in /var/run/redis.pid by
      default. You can specify a custom pid file location here.

   デーモンとして起動するときに、デフォルトではRedisはpidを :file:`/var/run/redis.pid` というファイルに書き出します。この設定を変えることで、pidファイルの位置を変えることができます。

   .. code-block:: nginx

      pidfile /var/run/redis.pid

.. confval:: port portnumber

   .. Accept connections on the specified port, default is 6379

   コネクションを受け付けるポートを指定します。デフォルトは ``6379`` です。

   .. code-block:: nginx

      port 6379

.. confval:: bind 127.0.0.1

   .. If you want you can bind a single interface, if the bind option is not
      specified all the interfaces will listen for incoming connections.

   もし、特定の一つのインタフェースにバインドしたい場合に設定します。もし :conf:`bind` オプションが指定されなかった場合には、コネクションがやってきたすべてのインタフェースを ``listen`` します。

   .. code-block:: nginx

       bind 127.0.0.1

.. confval:: timeout N

   .. Close the connection after a client is idle for N seconds (0 to disable)

   指定されたN秒数間、コマンドが送信されなければ、クライアントとの通信を切断します。

   ``0`` を指定するとタイムアウトが行われなくなります。

   .. code-block:: nginx

      timeout 300

.. confval:: loglevel level

   .. Set server verbosity to 'debug'
      it can be one of:

   サーバのログの情報量を設定します。設定できる項目は次の通りです。

   .. debug (a lot of information, useful for development/testing)
      verbose (many rarely useful info, but not a mess like the debug level)
      notice (moderately verbose, what you want in production probably)
      warning (only very important / critical messages are logged)

   ``debug``
      多くの情報を出します。開発/テスト用です。

   ``verbose``
      あまり重要でない情報も含めて多くの情報を出力しますが、 ``debug`` レベルよりは減ります。

   ``notice``
      運用時に使用したいと思うような、適度な量のログを出力します。

   ``warning``
      とても重要なメッセージや、重大なメッセージだけをログに出力します。
      
   .. code-block:: nginx

      loglevel verbose

.. confval:: logfile filename

   .. Specify the log file name. Also 'stdout' can be used to force
      Redis to log on the standard output. Note that if you use standard
      output for logging but daemonize, logs will be sent to /dev/null

   ログファイルの名前を指定します。 ``'stdout'`` を指定すると、Redisは標準出力にログを出力します。ただし、デーモンとして起動しているときに標準出力にログを出そうとしても、ログは :file:`/dev/null` に出力されてしまうので注意してください。

   .. code-block:: nginx

      logfile stdout

.. confval:: databases num

   .. Set the number of databases. The default database is DB 0, you can select
      a different one on a per-connection basis using SELECT <dbid> where
      dbid is a number between 0 and 'databases'-1

   データベースの番号を設定します。デフォルトのデータベースは ``DB 0`` です。ユーザは、 :com:`SELECT` ``<dbid>`` を使うことで、コネクションごとに違うデータベースを選択することができます。この ``dbid`` には、0から、 :conf:`databases` - 1 まで設定できます。

   .. code-block:: nginx

      databases 16

.. SNAPSHOTTING

スナップショットの設定
======================

.. confval:: save seconds changes

   .. Save the DB on disk:

   データベースをディスクに保存するタイミングを設定することができます。

   .. code-block:: nginx

      save <seconds> <changes>

   .. Will save the DB if both the given number of seconds and the given
      number of write operations against the DB occurred.

   このような設定があると、与えられた秒数経過するか、指定された回数分、書き込み命令を受け付けるとデータベースを保存します。

   .. code-block:: nginx

      save 900 1
      save 300 10
      save 60 10000
   
   .. In the example below the behaviour will be to save:
      after 900 sec (15 min) if at least 1 key changed
      after 300 sec (5 min) if at least 10 keys changed
      after 60 sec if at least 10000 keys changed

   このような設定がされると、次のようなタイミングで保存します:

   * もし最低1回、キーの変更が発生すると、900秒(15分)後
   * もし最低10回、キーの変更が発生すると、300秒(5分)後
   * もし最低10,000回、キーの変更が発生すると、60秒後

   .. note::

      .. you can disable saving at all commenting all the "save" lines.

      :conf:`save` 行をすべてコメントアウトすると、保存が行われなくなります。

.. confval:: rdbcompression yes/no

   .. Compress string objects using LZF when dump .rdb databases?
      For default that's set to 'yes' as it's almost always a win.
      If you want to save some CPU in the saving child set it to 'no' but
      the dataset will likely be bigger if you have compressible values or 
      keys.

   ``.rdb`` データベースにダンプするときに、文字列オブジェクトをLZFを使って圧縮するかどうかを設定します。デフォルトでは ``'yes'`` になっており、常に圧縮するようになっています。もし保存時にCPUパワーを節約したい場合は ``'no'`` を設定してください。ただし、値やキーを圧縮すると指定した場合に比べると、データセットの大きさは大きくなります。

   .. code-block:: nginx

      rdbcompression yes

.. confval:: dbfilename filename

   .. The filename where to dump the DB

   DBをダンプするファイル名を指定します。

   .. code-block:: nginx

      dbfilename dump.rdb

.. confval:: dir path

   .. The working directory.

   作業ディレクトリを設定します。

   .. The DB will be written inside this directory, with the filename specified
      above using the 'dbfilename' configuration directive.

   DBは、このディレクトリ内に、 :conf:`dbfilename` 設定ディレクティブで設定された名前で書き出されます。

   .. Also the Append Only File will be created inside this directory.

   :ref:`append_only_file` もこのディレクトリ内に作成されます。
 
   .. note::

      .. that you must specify a directory here, not a file name.

      この設定では、ファイル名ではなく、ディレクトリ名を設定してください。

   .. code-block:: nginx

      dir ./

.. REPLICATION

レプリケーションの設定
======================

.. confval:: slaveof masterip masterport

   .. Master-Slave replication. Use slaveof to make a Redis instance a copy of
      another Redis server. Note that the configuration is local to the slave
      so for example it is possible to configure the slave to save the DB with a
      different interval, or to listen to another port, and so on.

   マスター/スレーブ間のレプリケーションの設定です。 :conf:`slaveof` を使うと、他のRedisサーバのコピーとなるインスタンスが作られます。この設定ファイルで設定される設定値はスレーブに限定して行われるため、マスターとは異なる間隔でDBを保存したり、別のポートでlistenしたり、といったこともできます。

   .. code-block:: nginx

       slaveof 192.168.1.10 6379

.. confval:: masterauth master-password

   .. If the master is password protected (using the "requirepass" configuration
      directive below) it is possible to tell the slave to authenticate before
      starting the replication synchronization process, otherwise the master 
      will refuse the slave request.

   もし、マスターサーバーがパスワードで保護されているのであれば(:conf:`requirepass` 設定ディレクティブが使用されている)、レプリケーション同期プロセスを開始する前に認証をパスさせることができます。もし、パスワードが異なる、この設定が行われていないなどの場合は、マスターはスレーブからのリクエストを拒絶します。

   .. code-block:: nginx

      masterauth foobared

.. SECURITY

セキュリティの設定
==================

.. confval:: requirepass password

   .. Require clients to issue AUTH <PASSWORD> before processing any other
      commands.  This might be useful in environments in which you do not trust
      others with access to the host running redis-server.

   クライアントが他のコマンドを送る前に、 :com:`AUTH` を実行するように要求します。これは、Redisサーバが実行しているホストに、信頼できないホストからのアクセスがある場合に便利です。

   .. This should stay commented out for backward compatibility and because most
      people do not need auth (e.g. they run their own servers).

   後方互換性のためや、自分自身のためにサーバを立てている場合など、認証が必要ない場合にはコメントアウトしておいてください。
 
   .. Warning::

      .. since Redis is pretty fast an outside user can try up to
         150k passwords per second against a good box. This means that you 
         should use a very strong password otherwise it will be very easy 
         to break.

      Redisはとても高速なため、性能の良いマシン上で実行している場合は、毎秒150,000回程度のパスワードチェックを行うことがでいます。そのため、弱いパスワードであれば簡単に突破されてしまうため、非常に強いパスワードを設定するようにしてください。

   .. code-block:: nginx

      requirepass foobared

.. LIMITS

リソース制限の設定
==================

.. confval:: maxclients clientcount

   .. Set the max number of connected clients at the same time. By default there
      is no limit, and it's up to the number of file descriptors the Redis 
      process is able to open. The special value '0' means no limits.
      Once the limit is reached Redis will close all the new connections sending
      an error 'max number of clients reached'.

   同時に接続できるクライアント数を設定します。デフォルトでは無制限になっており、Redisプロセスがオープンできる最大のファイルディスクリプタの数まで接続を許可します。 ``'0'`` を設定すると無制限になります。最大の接続数に達する津お、Redisは全ての新しいコネクションを閉じ、 ``'max number of clients reached'`` エラーを送信します。

   .. code-block:: nginx

      maxclients 128

.. confval:: maxmemory bytes

   .. Don't use more memory than the specified amount of bytes.
      When the memory limit is reached Redis will try to remove keys with an
      EXPIRE set. It will try to start freeing keys that are going to expire
      in little time and preserve keys with a longer time to live.
      Redis will also try to remove objects from free lists if possible.

   指定された量以上のメモリを使用しなくなります。Redisは、メモリ使用量の限界に達すると、 :com:`EXPIRE` されたセットのキーを削除しようとします。キーを開放しようとします。また、少しで期限が切れそうなキーや、長い間維持されてきたキーを削除しようとします。可能であれば、フリーのリストのオブジェクトも可能であれば削除しようとします。

   .. If all this fails, Redis will start to reply with errors to commands
      that will use more memory, like SET, LPUSH, and so on, and will continue
      to reply to most read-only commands like GET.

   もしこれらがすべて失敗した場合には、 :com:`SET` や :com:`LPUSH` などの、メモリを使用するコマンドに対してエラーを返すようになります。 :com:`GET` などの読み込み専用のコマンドは引き続き処理可能です。

   .. warning::

      .. maxmemory can be a good idea mainly if you want to use Redis as a
         'state' server or cache, not as a real DB. When Redis is used as a real
         database the memory usage will grow over the weeks, it will be 
         obvious if it is going to use too much memory in the long run, 
         and you'll have the time to upgrade. With maxmemory after the limit 
         is reached you'll start to get errors for write operations, 
         and this may even lead to DB inconsistency.

      もしRedisを本物のDBではなく、状態の保持やキャッシュに使おうとしている場合は :conf:`maxmemory` を使うのは良い選択です。Redisが本当のデータベースとして使用されるのであれば、使用される記憶容量は徐々に成長していきます。長期間運用していると、大量のメモリを使用することになり、アップグレードのために時間を取る必要があるでしょう。もし限界を超えてしまうと、書き込み操作がエラーを返すようになるため、DBのデータが予期されない矛盾を含むことになるかもしれません。

    .. code-block:: nginx

       maxmemory 500MB

.. confval:: maxmemory-policy policy

   .. how Redis will select what to remove when maxmemory
      is reached? You can select among five behavior:

   Redisのメモリ使用量が :conf:`maxmemory` に達した場合、何から削除していくのか、というのを選択します。次の5つの振る舞いから選択することができます。
 
   .. volatile-lru -> remove the key with an expire set using an LRU algorithm
      allkeys-lru -> remove any key accordingly to the LRU algorithm
      volatile-random -> remove a random key with an expire set
      allkeys->random -> remove a random key, any key
      volatile-ttl -> remove the key with the nearest expire time (minor TTL)

   ``volatile-lru``
      LRUアルゴリズムを使用し、期限切れになったセットのキーを削除します

   ``allkeys-lru``
      LRCアルゴリズムに従い、どれかのキーを削除します

   ``volatile-random``
     期限切れになったセットの中から、ランダムにキーを削除します

   ``allkeys-random``
     どれかのキーをランダムに削除します

   ``volatile-ttl``
     一番期限に近いキーから削除していきます


   .. code-block:: nginx

      maxmemory-policy volatile-lru

.. confval:: maxmemory-samples number

   .. LRU and minimal TTL algorithms are not precise algorithms but approximated
      algorithms (in order to save memory), so you can select as well the sample
      size to check. For instance for default Redis will check three keys and
      pick the one that was used less recently, you can change the sample size
      using the following configuration directive.

   LRCと最小TTL(生存期間)アルゴリズムは正確なアルゴリズムではなく、メモリの節約のために近似アルゴリズムになっています。そのため、チェックを行うサンプルの数を選択できるようになっています。デフォルトのRedisでは3つのキーをチェックし、その中からもっと使われたのが古いものを1つ選ぶというアルゴリズムになっています。この設定ディレクティブを使用すると、このサンプル値を変更することができます。
   
   .. code-block:: nginx

      maxmemory-samples 3

.. APPEND ONLY MODE

追記専用モードの設定
=====================

.. confval:: appendonly yes/no

   .. By default Redis asynchronously dumps the dataset on disk. If you can live
      with the idea that the latest records will be lost if something like a 
      crash happens this is the preferred way to run Redis. If instead you 
      care a lot about your data and don't want to that a single record 
      can get lost you should enable the append only mode: when this mode 
      is enabled Redis will append every write operation received in the 
      file appendonly.aof. This file will be read on startup in order 
      to rebuild the full dataset in memory.

   Redisはデフォルトでは非同期でデータセットをディスクに書き出します。もし、クラッシュした場合に最新のいくつかのデータが失われても良いのであれば、Redisの実行方法として、これがベストな方法です。もしデータが大切で、1データも失いたくないのであれば、 :ref:`append_only_mode` を有効にすべきです。このモードが設定されると、Redisは :file:`appendonly.aof` に書き込み操作を受け取るたびにすべて記録していきます。このファイルは起動時に全データセットをメモリ内に構築していくときに読み込まれます。

   .. Note that you can have both the async dumps and the append only file 
      if you like (you have to comment the "save" statements above to 
      disable the dumps). Still if append only mode is enabled Redis will 
      load the data from the log file at startup ignoring the dump.rdb file.

   もし使用したければ、非同期のダンプと、追記専用モードの両方を併用することもできます。もしダンプを止めたければ、 :conf:`save` 文をコメントアウトする必要があります。その場合でも、もし追記専用モードが有効になっているのであれば、Redisは起動時に、ログファイルからデータをロードしようとして、 :file:`dump.rdb` ファイルを無視します。

   .. note::

      .. Check the BGREWRITEAOF to check how to rewrite the append
         log file in background when it gets too big.

      追記ログファイルが大きくなりすぎる場合には、バックグラウンドのリライト方法を確認するために、 :com:`BGREWRITEAOF` をチェックしてください。

   .. code-block:: nginx

      appendonly no

.. confval:: appendfilename filename

   .. The name of the append only file (default: "appendonly.aof")

   追記専用ファイルの名前です。デフォルトは :file:`appendonly.aof` です。

   .. code-block:: nginx

      appendfilename appendonly.aof

.. confval:: appendfsync mode

   .. The fsync() call tells the Operating System to actually write data on disk
      instead to wait for more data in the output buffer. Some OS will really 
      flush data on disk, some other OS will just try to do it ASAP.

   ``fsync()`` を呼び出すと、オペレーティングシステムに対して、出力バッファにデータが貯まるのを待つのではなく、データをディスクに書き出すように指示することができます。OSによっては実際にデータをディスクに書き出したり、なるべく速く書き出すようにしたりします。

   .. Redis supports three different modes:

   Redisは次の3つのモードをサポートしています。

   .. no: don't fsync, just let the OS flush the data when it wants. Faster.

   ``no``
      fsyncしません。データの書き出しはOSに任せます。高速です。
   
   .. always: fsync after every write to the append only log . Slow, Safest.

   ``always``
      追記専用ログに書き込むたびにfsyncを行います。低速ですが安全です。

   .. everysec: fsync only if one second passed since the last fsync. 
      Compromise.

   ``everysec``
      最後のfsyncから1秒経過するとfsyncを行います。上の2つの中間です。

   .. The default is "everysec" that's usually the right compromise between
      speed and data safety. It's up to you to understand if you can relax 
      this to "no" that will will let the operating system flush the output 
      buffer when it wants, for better performances (but if you can live 
      with the idea of some data loss consider the default persistence mode 
      that's snapshotting), or on the contrary, use "always" that's very 
      slow but a bit safer than everysec.

   デフォルトは、速度とデータの安全性の中庸をとった、 ``everysec`` です。もし背景を理解した上で、 ``no`` を選択しても問題ない、と感じたのであれば、それを選択してもらってもかまいません。こうすると、OSが自分の好きなタイミングで書き出しを行います。しかし、もしデータ損失について、問題ないと考えているのであれば、デフォルトの永続化モードのスナップショットの使用を考えた方が良いでしょう。その反対に非常に遅くはなりますが、 ``always`` を選択すると、 ``everysec`` よりも安全になります。

   .. If unsure, use "everysec".

   自信がないのであれば、 ``everysec`` を使用してください。

   .. code-block:: nginx

      appendfsync everysec

.. confval:: no-appendfsync-on-rewrite yes/no

   .. When the AOF fsync policy is set to always or everysec, and a background
      saving process (a background save or AOF log background rewriting) is
      performing a lot of I/O against the disk, in some Linux configurations
      Redis may block too long on the fsync() call. Note that there is no fix 
      for this currently, as even performing fsync in a different thread will
      block our synchronous write(2) call.

   .. In order to mitigate this problem it's possible to use the following 
      option that will prevent fsync() from being called in the main process 
      while a BGSAVE or BGREWRITEAOF is in progress.

   .. This means that while another child is saving the durability of Redis is
      the same as "appendfsync none", that in pratical terms means that it is
      possible to lost up to 30 seconds of log in the worst scenario (with the
      default Linux settings).
 
   .. If you have latency problems turn this to "yes". Otherwise leave it as
      "no" that is the safest pick from the point of view of durability.

   .. code-block:: nginx

      no-appendfsync-on-rewrite no

.. VIRTUAL MEMORY

仮想メモリの設定
=================

.. confval:: vm-enabled yes/no

   .. Virtual Memory allows Redis to work with datasets bigger than the actual
      amount of RAM needed to hold the whole dataset in memory.
      In order to do so very used keys are taken in memory while the other keys
      are swapped into a swap file, similarly to what operating systems do
      with memory pages.

   .. To enable VM just set 'vm-enabled' to yes, and set the following three
      VM parameters accordingly to your needs.

   .. code-block:: nginx

      vm-enabled no

.. confval:: vm-swap-file path

   .. This is the path of the Redis swap file. As you can guess, swap files
      can't be shared by different Redis instances, so make sure to use a swap
      file for every redis process you are running. Redis will complain if the
      swap file is already in use.

   .. The best kind of storage for the Redis swap file (that's accessed at 
      random) is a Solid State Disk (SSD).

   .. warning::

      .. if you are using a shared hosting the default of putting
         the swap file under /tmp is not secure. Create a dir with access 
         granted only to Redis user and configure Redis to create the swap 
         file there.

   .. code-block:: nginx

      vm-swap-file /tmp/redis.swap

.. confval:: vm-max-memory num

   .. vm-max-memory configures the VM to use at max the specified amount of
       RAM. Everything that deos not fit will be swapped on disk *if* 
       possible, that is, if there is still enough contiguous space in the 
       swap file.

   .. With vm-max-memory 0 the system will swap everything it can. Not a good
      default, just specify the max amount of RAM you can in bytes, but it's
      better to leave some margin. For instance specify an amount of RAM
      that's more or less between 60 and 80% of your free RAM.

   .. code-block:: nginx

      vm-max-memory 0

.. confval:: vm-page-size num

   .. Redis swap files is split into pages. An object can be saved using 
      multiple contiguous pages, but pages can't be shared between different 
      objects. So if your page is too big, small objects swapped out on disk 
      will waste a lot of space. If you page is too small, there is less 
      space in the swap file (assuming you configured the same number of 
      total swap file pages).

   .. If you use a lot of small objects, use a page size of 64 or 32 bytes.
      If you use a lot of big objects, use a bigger page size.
      If unsure, use the default :)

   .. code-block:: nginx

      vm-page-size 32

.. confval:: vm-pages number

   .. Number of total memory pages in the swap file.
      Given that the page table (a bitmap of free/used pages) is taken in 
      memory, every 8 pages on disk will consume 1 byte of RAM.

   .. The total swap size is vm-page-size * vm-pages

   .. With the default of 32-bytes memory pages and 134217728 pages Redis will
      use a 4 GB swap file, that will use 16 MB of RAM for the page table.

   .. It's better to use the smallest acceptable value for your application,
      but the default is large in order to work in most conditions.

   .. code-block:: nginx

      vm-pages 134217728

.. confval:: vm-max-threads number

   .. Max number of VM I/O threads running at the same time.
      This threads are used to read/write data from/to swap file, since they
      also encode and decode objects from disk to memory or the reverse, a 
      bigger number of threads can help with big objects even if they can't 
      help with I/O itself as the physical device may not be able to couple 
      with many reads/writes operations at the same time.

   .. The special value of 0 turn off threaded I/O and enables the blocking
       Virtual Memory implementation.

   .. code-block:: nginx

      vm-max-threads 4

.. ADVANCED CONFIG

高度な設定
==========

.. confval:: glueoutputbuf yes/no

   .. Glue small output buffers together in order to send small replies in a
      single TCP packet. Uses a bit more CPU but most of the times it is a win
      in terms of number of queries per second. Use 'yes' if unsure.

   .. code-block:: nginx
 
      glueoutputbuf yes

.. confval:: hash-max-zipmap-entries num

.. confval:: hash-max-zipmap-value num

   .. Hashes are encoded in a special way (much more memory efficient) when they
      have at max a given numer of elements, and the biggest element does not
      exceed a given threshold. You can configure this limits with the following
      configuration directives.

   .. code-block:: nginx

      hash-max-zipmap-entries 64
      hash-max-zipmap-value 512

.. confval:: activerehashing yes/no

   .. Active rehashing uses 1 millisecond every 100 milliseconds of CPU time in
      order to help rehashing the main Redis hash table (the one mapping 
      top-level keys to values). The hash table implementation redis uses 
      (see dict.c) performs a lazy rehashing: the more operation you run into 
      an hash table that is rhashing, the more rehashing "steps" are 
      performed, so if the server is idle the rehashing is never complete and 
      some more memory is used by the hash table.
 
   .. The default is to use this millisecond 10 times every second in order to
      active rehashing the main dictionaries, freeing memory when possible.

   .. If unsure:
      use "activerehashing no" if you have hard latency requirements and it is
      not a good thing in your environment that Redis can reply form time to 
      time to queries with 2 milliseconds delay.

   .. use "activerehashing yes" if you don't have such hard requirements but
      want to free memory asap when possible.

   .. code-block:: nginx

      activerehashing yes

.. INCLUDES

インクルード
============

.. confval:: include path

   .. Include one or more other config files here.  This is useful if you
      have a standard template that goes to all redis server but also need
      to customize a few per-server settings.  Include files can include
      other files, so use this wisely.

   .. code-block:: nginx

      include /path/to/local.conf
      include /path/to/other.conf
