.. -*- coding: utf-8 -*-;

.. Quick Start

.. _quick_start:

=============================
クイックスタート
=============================

.. This quickstart is a five minutes howto on how to get started with Redis. For more information on Redis check Redis Documentation Index.

このクイックスタートを読めば5分でRedisの使い始め方がわかります。さらにRedisを知りたい方はRedisのドキュメントの見出しを確認してください。

.. Obtain the latest version

最新版の取得
==================

.. The latest stable source distribution of Redis can be obtained at this location as a tarball.

Redisの最新安定版のソースは下記のリンクでtarball形式で配布しています::

  $ wget http://redis.googlecode.com/files/redis-1.02.tar.gz

.. The unstable source code, with more features but not ready for production, can be downloaded using git:

開発版のソースはgithubにあります。開発版は機能は増えていますが、あくまで製品段階ではありません::

  $ git clone git://github.com/antirez/redis.git

.. Compile

コンパイル
=================

.. Redis can be compiled in most POSIX systems. To compile Redis just untar the tar.gz, enter the directly and type 'make'.

RedisはほとんどのPOSIXシステムでコンパイルできます。Redisをコンパイルするには、tar.gzを展開してそのディレクトリに入り ``make`` と入力するだけでいいのです::

  $ tar xvzf redis-1.02.tar.gz
  $ cd redis-1.02
  $ make

.. In order to test if the Redis server is working well in your computer make sure to run make test and check that all the tests are passed.

Redisサーバがきちんと動作しているかを確認するには、 ``make test`` を走らせてすべてのテストをパスするかどうかで判断できます。

.. Run the server

サーバの起動
============

.. Redis can run just fine without a configuration file (when executed without a config file a standard configuration is used). To run Redis just type the following command:

Redisは設定ファイルなしで起動してもよきに計らってくれます。（設定ファイルなしで起動した場合、標準の設定で動作します）Redisを起動は下記のコマンドを入力すればいいだけです::

  $ ./redis-server

.. With the default configuration Redis will log to the standard output so you can check what happens. Later, you can change the default settings.

デフォルトの設定ではRedisは標準出力にログを吐くので、いまなにが起きているのかをその場で確認することができます。あとで標準の設定を変更することもできます。

.. Play with the built in client

組み込みクライアントで遊ぶ
==========================

.. Redis ships with a command line client that is automatically compiled when you ran make and it is called redis-cli

Redisにはコマンドラインクライアントも付いてきます。このクライアントは ``make`` を走らせてコンパイルしたときに自動的にRedisサーバと一緒に生成されます。このクライアントは ``redis-cli`` といいます。

.. For instance to set a key and read back the value use the following:

たとえばキーをセットして、その後キーに対応する値を読み込みたいときは次のようにします::

  $ ./redis-cli set mykey somevalue
  OK
  $ ./redis-cli get mykey
  somevalue

.. What about adding elements to a list:

要素をリストに追加する場合はこのようにします::

  $ ./redis-cli lpush mylist firstvalue
  OK
  $ ./redis-cli lpush mylist secondvalue
  OK
  $ ./redis-cli lpush mylist thirdvalue
  OK
  $ ./redis-cli lrange mylist 0 -1
  1. thirdvalue
  2. secondvalue
  3. firstvalue
  $ ./redis-cli rpop mylist
  firstvalue
  $ ./redis-cli lrange mylist 0 -1
  1. thirdvalue
  2. secondvalue


.. Further reading

さらに知りたい方に
==================

.. * What to play more with Redis? Read Fifteen minutes introduction to Redis data types.
.. * Check all the Features
.. * Read the full list of available commands in the Command Reference.
.. * Start using Redis from your favorite language.
.. * Take a look at some Programming Examples.

* もっとRedisで遊びたいって？Redisのデータ型に関する15分イントロを読んでください
* すべての機能を確認してください
* コマンドリファレンスにある使用可能な全てのコマンドを見て下さい
* あなたの好きなプログラミング言語からRedisを使ってみてください
* 既存のプログラミングの例を眺めてみてください
