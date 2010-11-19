.. -*- coding: utf-8 -*-

==============
 制御コマンド
==============

永続化処理コマンド
==================

.. command:: SAVE

   .. Save the whole dataset on disk (this means that all the databases are saved, as well as keys with an EXPIRE set (the expire is preserved). The server hangs while the saving is not completed, no connection is served in the meanwhile. An OK code is returned when the DB was fully stored in disk.

   すべてのデータセットをディスクに保存します。（つまりすべてのデータベースが保存され、 :com:`EXPIRE` がセットされたキーの有効期限も保存されます。）保存が完了するまではサーバはハングします。しばらくの間は一切接続が出来ません。データベースがすべてディスクに書き込み終わったときに ``OK`` コードが返ってきます。

   .. The background variant of this command is BGSAVE that is able to perform the saving in the background while the server continues serving other clients.

   このコマンドと同様だけれどもバックグラウンドで処理してくれるものが :com:`BGSAVE` です。こちらはサーバがクライアントに対して処理をしている間にもバックグラウンドで保存が出来ます。

   .. Return value

   **返り値**

     Status code replyが返ります。


.. command:: BGSAVE

   .. Save the DB in background. The OK code is immediately returned. Redis forks, the parent continues to server the clients, the child saves the DB on disk then exit. A client my be able to check if the operation succeeded using the LASTSAVE command.

   データベースの保存をバックグラウンドで行います。 ``OK`` コードは直ちに返って来ます。Redisはフォークし、親のプロセスはクライアントに対して処理をし続け、子のプロセスはデータベースをディスクに保存したあと死にます。クライアントから保存が無事に終わったかを :com:`LASTSAVE` コマンドを使って確認することが出来ます。

   .. Return value

   **返り値**

     Status code replyが返ります。


.. command:: BGREWRITEAOF

   .. Please for detailed information about the Redis Append Only File check the Append Only File Howto.

   Redis Append Only File(AOF)に関するより詳細な情報についてはAppend Only File Howtoを参考にしてください。

   .. BGREWRITEAOF rewrites the Append Only File in background when it gets too big. The Redis Append Only File is a Journal, so every operation modifying the dataset is logged in the Append Only File (and replayed at startup). This means that the Append Only File always grows. In order to rebuild its content the BGREWRITEAOF creates a new version of the append only file starting directly form the dataset in memory in order to guarantee the generation of the minimal number of commands needed to rebuild the database.

   :com:`BGREWRITEAOF` はAOFのサイズが大きくなりすぎたとき、バックグラウンドで再書き込みします。RedisのAOFはジャーナルなので、データセットを変更するすべての操作はAOFにログに取られます（そしてスタートアップ時に再生されます）つまりAOFは常に大きくなり続けます。AOFの中身を再構成するために、 :com:`BGREWRITEAOF` は新しいAOFを作成して、データベースを再構成するためのコマンドの数を最小限にすることを保証するために、その時点でのデータセットをメモリに直接書きこむことから始めます。

   .. The Append Only File Howto contains further details.

   AOF Howtoではより詳細な情報が書いてあります。

   .. Return value

   **返り値**

     Status code replyが返ります。

.. command:: LASTSAVE

   .. Return the UNIX TIME of the last DB save executed with success. A client may check if a BGSAVE command succeeded reading the LASTSAVE value, then issuing a BGSAVE command and checking at regular intervals every N seconds if LASTSAVE changed.

   最後にデータベースの保存が成功したUNIX時間を返します。クライアントは :com:`BGSAVE` が成功したかどうかを :com:`LASTSAVE` の値を見ることで確認することが出来ます。 :com:`BGSAVE` を呼び出したあと、N秒ごとに :com:`LASTSAVE` を呼び出して値が変わったかを確認するのです。

   .. Return value

   **返り値**

     Integer replyが返ります。具体的にはUNIXタイムスタンプです。


.. command:: SHUTDOWN

   .. Stop all the clients, save the DB, then quit the server. This commands makes sure that the DB is switched off without the lost of any data. This is not guaranteed if the client uses simply "SAVE" and then "QUIT" because other clients may alter the DB data between the two commands.

   すべてのクライアントを止めて、データベースを保存した後にサーバを停止します。このコマンドは確実にデータベースがその後のどんなデータ変更もなしに保存され、停止したことを保証します。これはもしクライアントが単純に :com:`SAVE` と :com:`QUIT` を呼び出した場合には保証されません。なぜなら他のクライアントがその2つのコマンドの間にデータベースを修正している可能性があるからです。

   .. Return value

   **返り値**

     .. Status code reply on error. On success nothing is returned since the server quits and the connection is closed.

     エラー発生時にはステータスコードが返ります。成功時には何も返りませんなぜならサーバが停止してコネクションが閉じられるからです。


リモートサーバ制御コマンド
==========================

.. command:: INFO

   .. The info command returns different information and statistics about the server in an format that's simple to parse by computers and easy to red by huamns.

   :com:`INFO` コマンドはサーバに関する情報と統計を表示します。パースもしやすく、可読性の高い形で表示します。

   .. Return value

   **返り値**

     Bulk replyが返ります。具体的には次のようなフォーマットです::

       edis_version:0.07
       connected_clients:1
       connected_slaves:0
       used_memory:3187
       changes_since_last_save:0
       last_save_time:1237655729
       total_connections_received:1
       total_commands_processed:1
       uptime_in_seconds:25
       uptime_in_days:0

     .. All the fields are in the form field:value

     すべてのフィールドは フィールド:値 の形で表示されます。

   **ノート**

   .. * used_memory is returned in bytes, and is the total number of bytes allocated by the program using malloc.

   * ``used_memory`` はバイト単位で表示されます。これはプログラムがmallocを使ってアロケートしたバイト数の合計を表示しています。

   .. * uptime_in_days is redundant since the uptime in seconds contains already the full uptime information, this field is only mainly present for humans.

   * ``uptime_in_days`` は主に人間が読むためだけに用意された項目です。なぜなら ``uptime`` にすでに起動時間の情報が秒で表示されているからです。

   .. * changes_since_last_save does not refer to the number of key changes, but to the number of operations that produced some kind of change in the dataset.

   * ``changes_since_last_save`` はキーの変更回数は参照しておらず、データセットに対する変更回数を参照しています。


.. command:: MONITOR

   .. MONITOR is a debugging command that outputs the whole sequence of commands received by the Redis server. is very handy in order to understand what is happening into the database. This command is used directly via telnet.

   :com:`MONITOR` はデバッグ用のコマンドで、Redisサーバが受け取ったすべてのコマンド一覧を表示します。データベース内で何が起きているかを理解するには非常に手軽な方法です。このコマンドはtelnet越しに直接使えます。

   .. code-block:: none

      % telnet 127.0.0.1 6379
      Trying 127.0.0.1...
      Connected to segnalo-local.com.
      Escape character is '^]'.
      MONITOR
      +OK
      monitor
      keys *
      dbsize
      set x 6
      foobar
      get x
      del x
      get x
      set key_x 5
      hello
      set key_y 5
      hello
      set key_z 5
      hello
      set foo_a 5
      hello

   .. The ability to see all the requests processed by the server is useful in order to spot bugs in the application both when using Redis as a database and as a distributed caching system.

   サーバ内で処理されているすべてのリクエストを見ることが出来ることでRedisをデータセットとして使うときも分散キャッシュとして使うときも、アプリケーション内のバグを探しやすくなります。

   .. In order to end a monitoring session just issue a QUIT command by hand.

   監視を辞めるには :com:`QUIT` コマンドを手で入力するだけでできます。

   .. Return value

   **返り値**

     .. Non standard return value, just dumps the received commands in an infinite flow.

     普通の返り値ではなく、受け取ったコマンドを無限にダンプするだけです。


.. command:: SLAVEOF host port

.. command:: SLAVEOF no one

   .. The SLAVEOF command can change the replication settings of a slave on the fly. If a Redis server is arleady acting as slave, the command SLAVEOF NO ONE will turn off the replicaiton turning the Redis server into a MASTER. In the proper form SLAVEOF hostname port will make the server a slave of the specific server listening at the specified hostname and port.

   :com:`SLAVEOF` コマンドはスレーブのレプリケーション設定をすぐさま変更することが出来ます。もしRedisサーバがすでにスレーブとして動いている場合は、 :com:`SLAVEOF` ``NO ONE`` によってレプリケーションをマスターに切り替えることが出来ます。 ``SLAVEOF hostname port`` という形で使えば、サーバを指定したホスト名とポートでリスニングしている特定のサーバのスレーブにすることが出来ます。

   .. If a server is already a slave of some master, SLAVEOF hostname port will stop the replication against the old server and start the synchrnonization against the new one discarding the old dataset.

   もしサーバがすでにあるマスターのスレーブだった場合には、 ``SLAVEOF hostname port`` のコマンドによって古いサーバのレプリケーションを止め、古いデータセットを捨てて、新しいサーバに対して動機を始めます。

   .. The form SLAVEOF no one will stop replication turning the server into a MASTER but will not discard the replication. So if the old master stop working it is possible to turn the slave into a master and set the application to use the new master in read/write. Later when the other Redis server will be fixed it can be configured in order to work as slave.

   もし ``SLAVEOF no one`` がレプリケーションを停止して、サーバをマスターに変更してくれますが、レプリケーションしたデータを捨てるわけではありません。もし古いマスターが停止した場合に、スレーブをマスターにして、アプリケーションが新しいマスターに対して読み書きを行うように変更することが可能です。後に他のRedisサーバが直された時にはスレーブとして設定することができます。

   .. Return value

   **返り値**

     Status code replyが返ります。


.. command:: CONFIG GET pattern 
   
   .. versionadded:: 2.0

.. command:: CONFIG SET parameter value 

   .. versionadded:: 2.0

   .. The CONFIG command is able to retrieve or alter the configuration of a running Redis server. Not all the configuration parameters are supported.

   :com:`CONFIG` コマンドは起動しているRedisサーバの設定を変更したり、取得したりすることが出来ます。すべての設定パラメータが利用出来るわけではありません。

   .. CONFIG has two sub commands, GET and SET. The GET command is used to read the configuration, while the SET command is used to alter the configuration.

   :com:`CONFIG` は2つのサブコマンドを持っています。 ``GET`` と ``SET`` です。 ``GET`` コマンドは読み込みの設定に使われます。 ``SET`` コマンドは設定を変更するために

   **CONFIG GET パターン**

     CONFIG GET returns the current configuration parameters. This sub command only accepts a single argument, that is glob style pattern. All the configuration parameters matching this parameter are reported as a list of key-value pairs. Example:

     .. code-block:: none

        $ redis-cli config get '*'
        1. "dbfilename"
        2. "dump.rdb"
        3. "requirepass"
        4. (nil)
        5. "masterauth"
        6. (nil)
        7. "maxmemory"
        8. "0\n"
        9. "appendfsync"
        10. "everysec"
        11. "save"
        12. "3600 1 300 100 60 10000"

        $ redis-cli config get 'm*'
        1. "masterauth"
        2. (nil)
        3. "maxmemory"
        4. "0\n"

     The return type of the command is a bulk reply.

   **CONFIG SET parameter value**

     CONFIG SET is used in order to reconfigure the server, setting a specific configuration parameter to a new value.

     The list of configuration parameters supported by CONFIG SET can be obtained issuing a CONFIG GET * command.

     The configuration set using CONFIG SET is immediately loaded by the Redis server that will start acting as specified starting from the next command.

     例::

       $ ./redis-cli 
       redis> set x 10
       OK
       redis> config set maxmemory 200
       OK
       redis> set y 20
       (error) ERR command not allowed when used memory > 'maxmemory'
       redis> config set maxmemory 0
       OK
       redis> set y 20
       OK

   **Parameters value format**

     The value of the configuration parameter is the same as the one of the same parameter in the Redis configuration file, with the following exceptions:

     * The save paramter is a list of space-separated integers. Every pair of integers specify the time and number of changes limit to trigger a save. For instance the command CONFIG SET save "3600 10 60 10000" will configure the server to issue a background saving of the RDB file every 3600 seconds if there are at least 10 changes in the dataset, and every 60 seconds if there are at least 10000 changes. To completely disable automatic snapshots just set the parameter as an empty string.

     * All the integer parameters representing memory are returned and accepted only using bytes as unit.

   **See Also**

     The INFO command can be used in order to read configuriaton parameters that are not available in the CONFIG command.
