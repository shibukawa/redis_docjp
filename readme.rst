.. README  

======
README
======

.. Introduction

イントロダクション
==================

.. Redis is an extremely fast and powerful key-value store database and 
   server implemented in ANSI C. Redis offers many different ways to do 
   one straightforward thing: store a value ("antirez") to a key ("redis"). 
   While the format of keys must always be simple strings, the power is with 
   the values, which support the following data types:

RedisはANSI Cで実装された、究極に速く、パワフルなキー・バリュー・ストア型のデータベース＆サーバです。Redisは、1つのシンプルな事に対して、さまざまな方法を提供しています。 ``"redis"`` というキーに対して、 ``"antirez"`` という値を格納することができます。キーのフォーマットは常にシンプルな文字列ですが、値として、次のような様々なデータ型を持つことができるように、パワフルな実装になっています。

.. Strings
   Lists
   Sets
   Sorted Sets (zsets)
   Hashes

* :ref:`strings`
* :ref:`lists`
* :ref:`sets`
* :ref:`sortedsets` (zsets)
* :ref:`hashes`

.. Each value type has an associated list of commands which can operate 
   on them, and the The Redis Command Reference contains an up to date 
   list of these commands, organized primarily by data type. The Redis 
   source also includes a Redis command line interface which allows you 
   to interact directly with the server, and is the means by which this 
   introduction will provide examples. Once you walk through the Redis Quick 
   Start Guide to get your instance of Redis running, you can follow along.

それぞれの値の型を操作するための、専用のコマンドがあります。これらのコマンドの最新のリストは :ref:`redis_command_referenece` に、データ型ごとに分類されて掲載されています。また、Redisのソースには :ref:`command_line_interface` が含まれており、サーバと直接対話することができ、このイントロダクションで提供しているサンプルを動かしてみることができます。 :ref:`quick_start` のガイドに従うと、動作しているRedisインスタンスの設定が行えるため、これからの説明の通りに動かすことができるようになります。

.. One of the most powerful aspects of Redis is the wide range of commands 
   which are optimized to work with specific data value types and executed 
   as atomic server-side operations. The List type is a great example - 
   Redis implements O(1) operations such as LPUSH or RPUSH, which have 
   accompanying LPOP and RPOP methods:

Redisの強力なパワーの1つが、データ型ごとに最適化された、幅広いコマンドです。コマンドの実行は、サーバーサイドでアトミックに行われます。 :ref:`lists` の例を紹介すると、RedisはO(1)で処理が完了する、リスト操作のコマンドの :com:`LPUSH` 、 :com:`RPUSH` と、関連コマンドの :com:`LPOP` 、 :com:`RPOP` メソッドを実装しています。

.. code-block:: none

   redis> lpush programming_languages C
   (integer) 1
   redis> lpush programming_languages Ruby
   (integer) 2
   redis> lpush programming_languages Python
   (integer) 3
   redis> rpop programming_languages
   "C"
   redis> lpop programming_languages
   "Python"

.. More complex operations are available for each data type as well. 
   Continuing with lists, you can get a range of elements with 
   LRANGE (O(start+n)) or trim the list with LTRIM (O(n)):

それぞれのデータ型に対するより複雑な操作も提供されています。再びリストの例を挙げると、 指定した範囲の要素を取得する :com:`LRANGE` (O(start+n))や、リストをトリムする :com:`LTRIM` (O(N)) があります。

.. code-block:: none

   redis> lpush cities NYC
   (integer) 1
   redis> lpush cities SF
   (integer) 2
   redis> lpush cities Tokyo
   (integer) 3
   redis> lpush cities London
   (integer) 4
   redis> lpush cities Paris
   (integer) 5
   redis> lrange cities 0 2
   1. "Paris"
   2. "London"
   3. "Tokyo"
   redis> ltrim cities 0 1
   OK
   redis> lpop cities
   "Paris"
   redis> lpop cities
   "London"

.. You can also add and remove elements from a set, and perform 
   intersections, unions, and differences.

:ref:`sets` に対しては、要素の追加と削除、セット同士の積、和、差の演算が行えます。

.. Redis can also be looked at as a data structures server. A Redis user 
   is virtually provided with an interface to Abstract Data Types, saving 
   them from the responsibility of implementing concrete data structures 
   and algorithms -- indeed both algorithms and data structures in Redis 
   are properly chosen in order to obtain the best performance.

Redisは、データ構造サーバとしてみることができます。Redisユーザには、仮想的に `抽象データ型 <http://ja.wikipedia.org/wiki/%E6%8A%BD%E8%B1%A1%E3%83%87%E3%83%BC%E3%82%BF%E5%9E%8B>`_ へのインタフェースが提供されているため、具象データ構造とアルゴリズムの実装という手間から逃れることができます。実際、Redisにおいては、アルゴリズムとデータ構造というのは、もっとも良いパフォーマンスが出るように選択するだけです。

.. All data in memory, but saved on disk

全てのデータはメモリに格納されるが、ディスクにも保存される
==========================================================

.. Redis loads and mantains the whole dataset into memory, but the 
   dataset is persistent, since at the same time it is saved on disk, 
   so that when the server is restarted data can be loaded back in memory.

Redisは全てのデータセットをメモリにロードして保持しますが、同時にディスクにも書き出すため、データセットは永続化されています。そのため、サーバが再起動されても、データは前と同じようにメモリに再ロードされます。

.. There are two kinds of persistence supported: the first one is 
   called snapshotting. In this mode Redis periodically writes to 
   disk asynchronously. The dataset is loaded from the dump every 
   time the server is (re)started.

永続化は2種類サポートされています。1つ目はスナップショットと呼ばれているものです。このモードでは、Redisは定期的に非同期にディスクに書き込みにいきます。再起動時は毎回、このダンプファイルから、データセットが読み込まれます。

.. Redis can be configured to save the dataset when a certain number of 
   changes is reached and after a given number of seconds elapses. 
   For example, you can configure Redis to save after 1000 changes 
   and at most 60 seconds since the last save. You can specify any 
   combination for these numbers.

Redisは、決まった回数の変更が行われたらデータセットを保存しにいくだとか、決まった時間が経過すると保存しにいく、といった設定を行うことができます。例えば、1000回の更新後か、最後の保存から最大で60秒で保存する、というような設定をすることができます。これらの数値は自由に設定できます。

.. Because data is written asynchronously, when a system crash occurs, 
   the last few queries can get lost (that is acceptable in many 
   applications but not in all). In order to make this a non issue Redis 
   supports another, safer persistence mode, called Append Only File, 
   where every command received altering the dataset (so not a read-only 
   command, but a write command) is written on an append only file ASAP.  
   This commands are replayed when the server is restarted in order to 
   rebuild the dataset in memory.



.. Redis Append Only File supports a very handy feature: the server is 
   able to safely rebuild the append only file in background in a 
   non-blocking fashion when it gets too long. You can find more details 
   in the Append Only File HOWTO.

.. Master-Slave replication made trivial

簡単マスター/スレーブレプリケーション
=======================================

.. Whatever will be the persistence mode you'll use Redis supports 
   master-slave replications if you want to stay really safe or if you 
   need to scale to huge amounts of reads.

Redis Replication is trivial to setup. So trivial that all you need to do in order to configure a Redis server to be a slave of another one, with automatic synchronization if the link will go down and so forth, is the following config line: slaveof 192.168.1.100 6379. We provide a Replication Howto if you want to know more about this feature.

.. It's persistent but supports expires

「それは永続化されているけど、期限切れです」 
============================================

Redis can be used as a memcached on steroids because is as fast as memcached but with a number of features more. Like memcached, Redis also supports setting timeouts to keys so that this key will be automatically removed when a given amount of time passes.

.. Beyond key-value databases

キー・バリュー型データベースを超えて
====================================

All these features allow to use Redis as the sole DB for your scalable application without the need of any relational database. We wrote a simple Twitter clone in PHP + Redis to show a real world example, the link points to an article explaining the design and internals in very simple words.

.. Multiple databases support

複数データベースのサポート
==========================

Redis supports multiple databases with commands to atomically move keys from one database to the other. By default DB 0 is selected for every new connection, but using the SELECT command it is possible to select a different database. The MOVE operation can move an item from one DB to another atomically. This can be used as a base for locking free algorithms together with the 'RANDOMKEY' commands.

.. Know more about Redis!

Redisについてももっと知りたい!
==============================

To really get a feeling about what Redis is and how it works please try reading A fifteen minutes introduction to Redis data types.

To know a bit more about how Redis works internally continue reading.

.. Redis Tutorial

Redisチュートリアル
===================

(note, you can skip this section if you are only interested in "formal" doc.)

Later in this document you can find detailed information about Redis commands, the protocol specification, and so on. This kind of documentation is useful but... if you are new to Redis it is also BORING! The Redis protocol is designed so that is both pretty efficient to be parsed by computers, but simple enough to be used by humans just poking around with the 'telnet' command, so this section will show to the reader how to play a bit with Redis to get an initial feeling about it, and how it works.

To start just compile redis with 'make' and start it with './redis-server'. The server will start and log stuff on the standard output, if you want it to log more edit redis.conf, set the loglevel to debug, and restart it.

You can specify a configuration file as unique parameter:

.. code-block:: bash

   ./redis-server /etc/redis.conf

This is NOT required. The server will start even without a configuration file using a default built-in configuration.

Now let's try to set a key to a given value:

.. code-block:: bash

   $ telnet localhost 6379
   Trying 127.0.0.1...
   Connected to localhost.
   Escape character is '^]'.
   SET foo 3  
   bar
   +OK

The first line we sent to the server is "set foo 3". This means "set the key foo with the following three bytes I'll send you". The following line is the "bar" string, that is, the three bytes. So the effect is to set the key "foo" to the value "bar". Very simple!

(note that you can send commands in lowercase and it will work anyway, commands are not case sensitive)

Note that after the first and the second line we sent to the server there is a newline at the end. The server expects commands terminated by "\r\n" and sequence of bytes terminated by "\r\n". This is a minimal overhead from the point of view of both the server and client but allows us to play with Redis with the telnet command easily.

The last line of the chat between server and client is "+OK". This means our key was added without problems. Actually SET can never fail but the "+OK" sent lets us know that the server received everything and the command was actually executed.

Let's try to get the key content now:

.. code-block:: none

   GET foo
   $3
   bar

Ok that's very similar to 'set', just the other way around. We sent "get foo", the server replied with a first line that is just the $ character follwed by the number of bytes the value stored at key contained, followed by the actual bytes. Again "\r\n" are appended both to the bytes count and the actual data. In Redis slang this is called a bulk reply.

What about requesting a non existing key?

.. code-block:: none

   GET blabla
   $-1

When the key does not exist instead of the length, just the "$-1" string is sent. Since a -1 length of a bulk reply has no meaning it is used in order to specifiy a 'nil' value and distinguish it from a zero length value. Another way to check if a given key exists or not is indeed the EXISTS command:

.. code-block:: none

   EXISTS nokey
   :0
   EXISTS foo
   :1

As you can see the server replied ':0' the first time since 'nokey' does not exist, and ':1' for 'foo', a key that actually exists. Replies starting with the colon character are integer reply.

Ok... now you know the basics, read the REDIS COMMAND REFERENCE section to learn all the commands supported by Redis and the PROTOCOL SPECIFICATION section for more details about the protocol used if you plan to implement one for a language missing a decent client implementation.

.. License

ライセンス
==========

Redis is released under the BSD license. See the COPYING file for more information.

.. Credits

クレジット
==========

Redis is written and maintained by Salvatore Sanfilippo, Aka 'antirez'.