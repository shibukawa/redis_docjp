
.. Request/Response protocols and RTT
.. ====================================

=======================================================
リクエスト/レスポンス プロトコルと往復遅延時間
=======================================================

.. Redis is a TCP server using the client-server model and what is called a Request/Response protocol.

Redisは、典型的なTCPを使ったクライアント/サーバモデルです。リクエスト/レスポンスプロトコルと呼ばれます。

.. This means that usually a request is accomplished with the following steps:

いくつかのステップでリクエストが成り立っています。

.. * The client sends a query to the server, and reads from the socket, usually in a blocking way, for the server response.
.. * The server processes the command and sends the response back to the server.

* クライントは、クエリーを送る。　ソケットを読む、普段はブロックすること無しに、サーバからのレスポンス 
* サーバープロセスは、コマンドを受け取りそしてサーバにレスポンスを返します

.. So for instance a four commands sequence is something like this:

インスタンスは、4つのコマンドシーケンスを送ると以下のように動作します。

* Client: INCR X
* Server: 1
* Client: INCR X
* Server: 2
* Client: INCR X
* Server: 3
* Client: INCR X
* Server: 4

.. Clients and Servers are connected via a networking link. Such a link can be very fast (a loopback interface) or very slow (a connection established over the internet with many hops between the two hosts). Whatever the network latency is, there is a time for the packets to travel from the client to the server, and back from the server to the client to carry the reply.

クライアントとサーバはネットワーク越しに接続されます。ループバックの高速な接続でもインターネットを介した低速なネットワークでもどちらでもOKです。ネットワークのレイテンシとは、クライアントがパケットを送信してからサーバまでに届き、そして、サーバが応答してからクライアントに到達するまでの時間のことです。

.. This time is called RTT (Round Trip Time). It is very easy to see how this can affect the performances when a client needs to perform many requests in a row (for instance adding many elements to the same list, or populating a database with many keys). For instance if the RTT time is 250 milliseconds (in the case of a very slow link over the internet), even if the server is able to process 100k requests per second, we'll be able to process at max four requests per second.

この時間はRTT(Round Trip Time: 往復遅延時間)と呼ばれます。この値は、パフォーマンスに多大な影響を及ぼします。例えばRTTが250msかかる場合(この例はインターネット経由でのとても遅いパターンです)は、秒間100kリクエストが可能なサーバーでも秒間4リクエストが上限となります。

.. If the interface used is a loopback interface, the RTT is much shorter (for instance my host reports 0,044 milliseconds pinging 127.0.0.1), but it is still a lot if you need to perform many writes in a row.

もしルークバックインターフェースが使用可能ならば、RTTは大幅に短縮が可能です（私の例だと0.044ms pinging 127.0.0.1)しかしもし大量に書き込みたい場合は、これほど早くは有りません。

.. Fortunately there is a way to improve this use cases.

幸いなことに、これらを改善する方法があります。

.. Redis Pipelining

.. _pipelining:

パイプライニング
================

.. A Request/Response server can be implemented so that it is able to process new requests even if the client didn't already read the old responses. This way it is possible to send multiple commands to the server without waiting for the replies at all, and finally read the replies in a single step.

リクエスト/レスポンスサーバーは、クライアントが過去のレスポンスを読み取る前にあtらしいリクエストを処理できる状態にあります。このやり方では、複数のコマンドをサーバーの応答を待たずに一括で送信しその後ひとつづつ受信処理を行ないます。

.. This is called pipelining, and is a technique widely in use since many decades. For instance many POP3 protocol implementations already supported this feature, dramatically speeding up the process of downloading new emails from the server.

これをパイプライニング(pipelining)パイプライニングと呼ばれ数十年前から利用されています。例えば多くのPOP3プロトコル実装ではサーバから新しいメールをダウンロードするプロセスを大幅にスピードアップさせる為、この機能をサポートしています。
。

.. Redis supports pipelining since the very early days, so whatever version you are running, you can use pipelining with Redis. This is an example using the raw netcat utility:

Redisでは、早い段階からパイプライニングをサポートしています(多分もちろんあなたがご使用のバージョンでも）あなたもパイプライニングが利用できます。以下の例では、netcatユーティリティーになります。

.. code-block:: nginx 

  $ (echo -en "PING\r\nPING\r\nPING\r\n"; sleep 1) | nc localhost 6379
  +PONG
  +PONG
  +PONG

.. This time we are not paying the cost of RTT for every call, but just one time for the three commands.

今回は、RTTのコストを払っていません。一度に3つのコマンドを発行しています。

.. To be very explicit, with pipelining the order of operations of our very first example will be the following:

次の例はとてもわかりやすいパイプライニングの例です。

* Client: INCR X
* Client: INCR X
* Client: INCR X
* Client: INCR X
* Server: 1
* Server: 2
* Server: 3
* Server: 4

.. important::

  パイプライニングを使用してクライアントからコマンドが送信されるとサーバは応答に強制的にメモリー使ったキューを利用します。もし超大量ののコマンドを送った場合は、それ相応(10kのコマンドを送ったとして約4倍)のメモリーが必要になります。

.. IMPORTANT NOTE: while the client sends commands using pipelining, the server will be forced to queue the replies, using memory. So if you need to send many many commands with pipelining it's better to send this commands up to a given reasonable number, for instance 10k commands, read the replies, and send again other 10k commands and so forth. The speed will be nearly the same, but the additional memory used will be at max the amount needed to queue the replies for this 10k commands.

.. Some benchmark
.. ===================

ベンチマーク
====================

.. In the following benchmark we'll use the Redis Ruby client, supporting pipelining, to test the speed improvement due to pipelining:

Redis 各種クライアントを用いたベンチマークサンプルです。パイプライニングをサポートしています。ベンチマークでは、パイプライニングの有り無しで計測を行っています。

Ruby Sample
-------------

.. literalinclude:: benchmark.rb
     :language: ruby
     :encoding: utf-8
     :linenos:

Running the above simple script will provide this figures in my Mac OS X system, running over the loopback interface, where pipelining will provide the smallest improvement as the RTT is already pretty low:

.. code-block:: nginx

  without pipelining 1.185238 seconds
  with pipelining    0.250783 seconds


Python Sample
--------------

.. literalinclude:: benchmark.py
     :language: python
     :encoding: utf-8
     :linenos:


このサンプルは、MBP(i7 4GB OSX10.6.4)上でRedis-Server2.0.2,Python2.6.1上で計測されたものです。ネットワークはループバックインターフェース経由で接続されているのでRTTはプリティーLowです。
  
.. code-block:: nginx

  without pipeline 0.824854135513
     with pipeline 0.197869062424

.. As you can see using pipelining we improved the transfer by a factor of five.

ご覧のとおり、パイプラインを使用したほうが4倍以上高速化されています。




.. Pipelining VS other multi-commands
.. ====================================

パイプライニング vs その他マルチコマンド
========================================================

.. Often we get requests about adding new commands performing multiple operations in a single pass. For instance there is no command to add multiple elements in a set. You need calling many times SADD.

シングルパスで複数のオペレーションを行ないたい場合に使える便利コマンドは特に用意されていません。多くの場合あなたは大量の:com:`SADD` コマンドを発行する必要があります。

.. With pipelining you can have performances near to an MSADD command, but at the same time we'll avoid bloating the Redis command set with too many commands. An additional advantage is that the version written using just SADD will be ready for a distributed environment (for instance Redis Cluster, that is in the process of being developed) just dropping the pipelining code.

一方パイプライニングを使用すると、:com:`MADD` コマンドを使用した時と同じだけのグッドパフォーマンスを期待できます。しかし、redisは大量のコマンドを受け取ることになります。

