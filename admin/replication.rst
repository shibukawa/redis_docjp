.. -*- coding: utf-8 -*-;

.. Redis Replication Howto

.. _replication:

==========================
レプリケーションの設定方法
==========================

.. General Information

一般的な情報
-----------------

.. Redis replication is a very simple to use and configure master-slave replication that allows slave Redis servers to be exact copies of master servers. The following are some very important facts about Redis replication:

Redisのマスタースレーブのレプリケーションの利用と設定はとても簡単です。マスターにスレーブからの接続許可を出すだけで利用できます。以下は、レプリケーションに関するいくつか重要な情報があります。

.. * A master can have multiple slaves.

* マスタは、複数のスレーブを持つことができます。

.. * Slaves are able to accept other slaves connections, so instead to connect a number of slaves against the same master it is also possible to connect some of the slaves to other slaves in a graph-alike structure.

* スレーブはさらに複数のスレーブを持つことが出来ます。

.. Redis replication is non-blocking on the master side, this means that the master will continue to serve queries while one or more slaves are performing the first synchronization. Instead replication is blocking on the slave side: while the slave is performing the first synchronization it can't reply to queries.

* Redisレプリケーションは、マスター側では非同期で動作します。これにより、複数のスレーブからのリクエストがあった場合にも、マスターの動作は継続的に行われます。代わりに、最初の同期を実行している間にレプリケーションは、スレーブ側でブロックされているいます。スレーブがクエリに返信することはできません

.. * Replications can be used both for scalability, in order to have multiple slaves for read-only queries (for example heavy SORT operations can be launched against slaves), or simply for data redundancy.

* 読み込み専用のスレーブを複数使用することでスケーラビリティを確保することが出来ます。また、冗長性も確保されます。

.. * It is possible to use replication to avoid the saving process on the master side: just configure your master redis.conf in order to avoid saving at all (just comment al the "save" directives), then connect a slave configured to save from time to time.



.. How Redis replication works

どのようにRedisはレプリケーションしているのか？
-----------------------------------------------

.. In order to start the replication, or after the connection closes in order resynchronize with the master, the slave connects to the master and issues the SYNC command.

レプリケーションを開始するか、または切断後にマスターが再連動するように設定されたとき、スレーブは、マスターにSYNCコマンドを発行します。

.. The master starts a background saving, and at the same time starts to collect all the new commands received that had the effect to modify the dataset. When the background saving completed the master starts the transfer of the database file to the slave, that saves it on disk, and then load it in memory. At this point the master starts to send all the accumulated commands, and all the new commands received from clients that had the effect of a dataset modification, to the slave, as a stream of commands, in the same format of the Redis protocol itself.

マスターでは、バックグランドで保存が行われると同時に、次のコマンドの受付が始まります。変更されたデータセットを保存すると同時に各スレーブへのシンクとメモリーへのロードが行われます。

.. You can try it yourself via telnet. Connect to the Redis port while the server is doing some work and issue the SYNC command. You'll see a bulk transfer and then every command received by the master will be re-issued in the telnet session.

TelnetでRedisの動作をご自身で確かめることが出来ます。実行中のReidsサーバへ接続を行ないSYNCコマンドを発行します。その後RedisサーバへBulk転送を行うとコマンド毎にtelnetセッション側でも確認することが出来ます。


.. Slaves are able to automatically reconnect when the master <-> slave link goes down for some reason. If the master receives multiple concurrent slave synchronization requests it performs a single background saving in order to serve all them.

スレーブは、何らかの理由で切断されたとしても、自動的に再接続を行えます。マスターに複数のスレーブからのSYNCリクエストが来た場合でも、すべてのリクエストにバックグランドで順番に応えます。


コンフィギュレーション
-----------------------------

.. To configure replication is trivial: just add the following line to the slave configuration file:

レプリケーションを構成するには、単にスレーブのコンフィギュレーションファイルに次の行を追加するだけで簡単に追加出来ます：

.. code-block:: nginx 

  slaveof 192.168.1.1 6379

.. Of course you need to replace 192.168.1.1 6379 with your master ip address (or hostname) and port.

上記設定内のIPアドレス（またはホスト名）とポートをあなたの使用しているマスターサーバの物に置き換える必要があります。

