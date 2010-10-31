.. Features (DRAFT)

===========
Redisの機能
===========

.. Checking Redis for the first time? Here your will find the most 
   important features, and pointers to a lot more information.

Redisを見るのは始めてでしょうか？ここでは、重要な機能と、多くの情報へのリンクが書かれています。

.. Speed

スピード
========

.. Redis is written in ANSI C, and loads the whole dataset in memory, 
   so it is wicked fast! Up to 110,000 SETs/second, 81,000 GETs/second 
   can be achieved in an entry level Linux box. Read more about Redis Speed.

RedisはANSI Cで書かれていて、すべてのデータセットをメモリ内に読み込むため、危険なほどのスピードで動作します！エントリーレベルのLinuxマシンで、110,000 SET/秒、81,000 GET/秒を達成することができます。これについては、 :ref:`speed` を参照してください。

.. Also Redis supports Pipelining of commands and getting and setting 
   múltiple values in a single command to speed up communication with the 
   client libraries.

また、Redisはコマンドの :ref:`pipelining` をサポートしているため、複数の値を1つのコマンドで取得したり設定できるため、クライアントライブラリとの通信をスピードアップすることができます。

.. Persistence

永続化
======

.. While all the data lives in memory, changes are asynchronously saved 
   on disk using flexible policies based on elapsed time and/or number 
   of updates since last save.

すべてのデータがメモリ上にあり、変更は非同期でディスク上に書き込まれます。書き込むタイミングについては、最後に保存してからの経過時間および、アップデートの回数、もしくはその両方など、柔軟にポリシーを設定することができます。

.. If you can't afford losing some data, starting on version 1.1 
   (currently in beta but you can download it from the Git repository) 
   Redis supports an append-only file persistence mode. Check more on 
   Persistence, or read the AppendOnlyFileHowto for more information.

もし、データが失われることが許容できないのであれば、追記専用ファイル永続化モードもサポートしています。詳細については、 :ref:`persistence` か、 :ref:`append_only_file_howto` を参照してください。

.. Support for Data Structures

データ構造のサポート
====================

.. Values in Redis can be Strings as in a conventional key-value store, 
   but also Lists, Sets, and SortedSets (to be support in version 1.1). 
   This data types allow pushing/poping elements, or adding/removing them, 
   also perform server side union, intersection, difference between sets, 
   and so forth depending on the types. Redis supports different kind of 
   sorting abilities for Sets and Lists.

Redisの値としては、伝統的なキー・バリュー・ストアと同様、 :ref:`strings` をサポートしていますが、これ以外にも、 :ref:`lists` 、 :ref:`sets` 、 :ref:`sortedsets` 、 :ref:`hashes` も使えます。このデータ型に対しては、要素のpush/pop、add/remove、またはサーバサイドでのセット間の和、積、差など、型によって様々な操作をサポートしています。Redisは :ref:`sets` と :ref:`lists` に対して、異なる種類のソート機能をサポートしています。

.. You can think in Redis as a Data Structures Server, that allows you to 
   model non trivial problems. Read Data Types to learn more about the way 
   Redis handle Strings, and the Commands supported by Lists, Sets and 
   SortedSets

Redisを、 **データ構造サーバ** と考えると、重要な問題のモデル化に使用することもできます。Redisにおける :ref:`strings` の取り扱い方、 :ref:`lists` 、 :ref:`sets` 、 :ref:`sortedsets` をサポートするコマンドについて詳しく知るためには、 :ref:`datatypes` の説明を参照してください。

.. Atomic Operations

アトミックな操作
================

.. Redis operations working on the different Data Types are atomic, so 
   setting or increasing a key, adding and removing elements from a set, 
   increasing a counter will all be accomplished safely.

Redisは、データ型ごとの操作は **アトミック** に動作します。そのため、キーの増加、セットに対する要素のadd/remove、カウンターの増加などの操作は、すべて安全に完了します。

.. Variety of Supported Languages

さまざまな言語のサポート
========================

.. Ruby, Python, Twisted Python, PHP, Erlang, Tcl, Perl, Lua, Java, Scala, 
   Clojure, choose your poison. Check the list of Supported Languages 
   for all the details.

Ruby、Python、Twisted Python、PHP、Erlang、Tcl、Perl、Lua、Java、Scala、Clojureなどから好きな言語を選べます。すべての詳細については、 :ref:`supported_languages` のリストをチェックしてください。

.. If your favorite language is not supported yet, you can write your own 
   client library, as the Protocol is pretty simple.

もしお気に入りの言語がまだサポートされていなければ、自分でクライアントのライブラリを自分で書くこともできます。 :ref:`protocol` はとてもシンプルです。

.. Master/Slave Replication

マスター/スレーブのレプリケーション
===================================

.. Redis supports a very simple and fast Master/Slave replication. 
   Is so simple it takes only one line in the configuration file to 
   set it up, and 21 seconds for a Slave to complete the initial sync 
   of 10 MM key set in a Amazon EC2 instance.

Redisはシンプルで高速なマスター/スレーブのレプリケーションをサポートしています。設定ファイルに1行足すだけで設定が完了し、Amazon EC2のインスタンスにある、1000万のキーがあるマスターからスレーブに対して初回の同期をかけると、21秒で終わります。

.. Read more about Master/Slave Replication.

詳しくは、 :ref:`master_slave_replication` を参照してください。

.. Sharding

シャーディング
==============

.. Distributing the dataset across multiple Redis instances is easy 
   in Redis, as in any other key-value store. And this depends 
   basically on the Languages client libraries being able to do so.

Redisであれば、他のキー・バリュー・ストアのように、複数のRedisインスタンス間で簡単にデータセットを分散させておくことができます。この機能は基本的に、言語クライアントライブラリに依存しています。

.. Read more about Sharding if you want to know more about distributing 
   data and workload in Redis.

Redisのデータの分散やワーク負荷について詳しく知りたい場合は、 :ref:`sharding` を参照してください。

.. Hot Backups

ホット・バックアップ
====================

TODO

.. Simple to Install, Setup and Manage

シンプルなインストール・セットアップ・管理
==========================================

.. Installing Redis requires little more than downloading it, uncompressing 
   it and running make. Management is near zero, so you can start using 
   Redis in a matter of minutes.

Redisをインストールするには、アーカイブをダウンロードして、回答して、makeを実行するだけです。管理はほぼゼロで、ほんの数分で使用開始できます。

.. Go on and read about Redis installation, its Setup and Management.

詳しくはRedisの :ref:`installation` 、 :ref:`setup_and_management` を参照してください。

.. Portable

移植性
======

.. Redis is written in ANSI C and works in most POSIX systems like Linux, 
   BSD, Mac OS X, Solaris, and so on. Redis is reported to compile and 
   work under WIN32 if compiled with Cygwin, but there is no official 
   support for Windows currently.

RedisはANSI Cで書かれており、Linux、BSD、Mac OS X、SolarisなどのほとんどのPOSIXシステムで動作します。また、Win32上でも、Cygwinを使ってコンパイルと動作に成功したという報告もありますが、現在はWindowsは正式にはサポートしていません。

.. Liberal Licensing

自由なライセンス
================

.. Redis is free software released under the very liberal BSD license.

Redisはとても自由なBSDライセンス [#]_ の元でフリーソフトウェアとしてリリースされています。

.. rubric:: 脚注
.. [#] (訳注)正式にはNew BSD、修正BSDという宣伝条項がないライセンス

.. What's next?

次は？
======

.. Want to get started with Redis? Try the Quick Start you will be up 
   and running in just a matter of minutes.

Redisを使ってみたくなりましたか？ぜひ、たった数分間なので :ref:`quick_start` を試してみてください。

.. Check the Code Samples and find how you can use Redis with your 
   favorite programming language.

また、 :ref:`code_samples` をチェックすると、あなたのお気に入りの言語でどのようにRedisを使うことができるのかを確認することができます。

.. Compare Redis with other key-value stores, like Tokyo Cabinet or Memcached.

また、 :ref:`compares` のページでは、RedisとTokyo CabinetやMemcachedなどの他のキー・バリュー・ストアとの比較を行っています。
