.. Protocol Specification

.. _protocol:

==============
プロトコル仕様
==============

.. The Redis protocol is a compromise between the following things:

Redisのプロトコルは次のような要求を満たすものとなっています。

.. * Simple to implement.
   * Fast to parse by a computer.
   * Easy enough to parse by a human.

* 実装しやすい
* コンピュータにパースさせるのが楽
* 人間がパースするのも十分に簡単

.. Networking layer

ネットワークレイヤー
====================

.. A client connects to a Redis server creating a TCP connection to the port 6379. 
   Every Redis command or data transmitted by the client and the server is terminated 
   by "\r\n" (CRLF).

Redisのクライアントは、ポート6379でサーバに接続しに行くことでコネクションを張ります。クライアント・サーバ間でやりとりされる、すべてのRedisコマンドやデータは ``\r\n`` (CRLF)で終端されます。

.. Requests

リクエスト
==========

.. Redis accepts commands composed of different arguments. Once a command is 
   received, it is processed and a reply is sent back to the client.

Redisは複数の異なる引き数を含むコマンドを受け取ります。コマンドを受け取ると、それを処理して、クライアント側に返信を返します。

.. The new unified request protocol

新統一リクエスト・プロトコル
============================

.. The new unified protocol was introduced in Redis 1.2, but it became the 
   standard way for talking with the Redis server in Redis 2.0.

新統一リクエスト・プロトコルは、Redis 1.2から導入され、2.0からはサーバが使う標準的な方法になりました。

.. In the unified protocol all the arguments sent to the Redis server are binary safe. 
   This is the general form:

統一リクエスト・プロトコルの中では、すべての引き数はバイナリセーフな方法でサーバに送られます。一般的には次のような構成をしています。

.. *<number of arguments> CR LF
   $<number of bytes of argument 1> CR LF
   <argument data> CR LF
   ...
   $<number of bytes of argument N> CR LF
   <argument data> CR LF

.. code-block:: none

   *<引き数の数> CR LF
   $<引き数1のバイト数> CR LF
   <引き数データ> CR LF
   ...
   $<引き数Nのバイト数> CR LF
   <引き数データ> CR LF

.. See the following example:

次のようになります。

.. code-block:: none

   *3
   $3
   SET
   $5
   mykey
   $7
   myvalue

.. This is how the above command looks as a quoted string, so that it is possible to 
   see the exact value of every byte in the query:

このコマンドを文字列形式で正確に表現すると、次のようになります。

.. code-block:: none

   "*3\r\n$3\r\nSET\r\n$5\r\nmykey\r\n$7\r\nmyvalue\r\n"

.. As you will see in a moment this format is also used in Redis replies. 
   The format used for every argument "$6\r\nmydata\r\n" is called a Bulk Reply.
   While the actual unified request protocol is what Redis uses to return list of
   items, and is called a Multi Bulk Reply. It is just the sum of N different Bulk
   Replies prefixed by a *<argc>\r\n string where <argc> is the number of arguments
   (Bulk Replies) that will follow.

これは、Redisからのリプライにも使われます。引き数に ``"$6\r\nmydata\r\n"`` という形式を使ったものを、 :ref:`bulk_reply` と呼んでいます。また、リストを返すなど、実際に統一リクエスト・プロトコルが使用されているものを、 :ref:`multi_bulk_reply` と呼んでいます。これは、それぞれの引き数(バルクリプライ)の前に、引き数の数<argc>を指定するための、 :samp:`*{<argc>}\n\r` を前につけたものになります。

.. Replies

リプライ
========

.. Redis will reply to commands with different kinds of replies. 
   It is possible to check the kind of reply from the first byte sent by the server:

Redisはコマンドに対して、様々な形式のリプライを返します。最初の1バイトを見ることで、どのような種類のリプライかをチェックすることができます。

.. * With a single line reply the first byte of the reply will be "+"
   * With an error message the first byte of the reply will be "-"
   * With an integer number the first byte of the reply will be ":"
   * With bulk reply the first byte of the reply will be "$"
   * With multi-bulk reply the first byte of the reply will be "*"

* 1行リプライの場合は、最初のバイトは ``+`` で始まります。
* エラーメッセージの場合は、最初のバイトは ``-`` で始まります。
* 数字の場合は、最初のバイトは ``:`` で始まります。
* :ref:`bulk_reply` の場合は、最初のバイトは ``$`` で始まります。
* :ref:`multi_bulk_reply` の場合は、最初のバイトは ``*`` で始まります。

.. Single line reply

1行リプライ
-----------

.. A single line reply is in the form of a single line string starting 
   with "+" terminated by "\r\n". For example:

1行リプライは1行の文字列で構成されたリプライで、 ``+`` で始まり、 ``\r\n`` で終わります。

.. code-block:: none

   +OK

.. The client library should return everything after the "+", that is, the 
   string "OK" in the example.

クライアントライブラリは ``+`` の後ろの結果を返すべきです。この場合は、 ``"OK"`` になります。

.. The following commands reply with a single line reply: PING, SET, SELECT, SAVE, 
   BGSAVE, SHUTDOWN, RENAME, LPUSH, RPUSH, LSET, LTRIM

1行リプライを返すコマンド: :com:`PING`, :com:`SET`, :com:`SELECT`, :com:`SAVE`, :com:`BGSAVE`, :com:`SHUTDOWN`, :com:`RENAME`, :com:`LPUSH`, :com:`RPUSH`, :com:`LSET`, :com:`LTRIM`

.. Error reply

エラーリプライ
--------------

.. Errors are sent exactly like Single Line Replies. The only difference is that the 
   first byte is "-" instead of "+".

エラーリプライは、1行リプライと非常に良く似ていますが、 ``+`` の代わりに ``-`` が最初のバイトとして返されます。

.. Error replies are only sent when something strange happened, for instance if you 
   try to perform an operation against the wrong data type, or if the command does 
   not exist and so forth. So an exception should be raised by the library client 
   when an Error Reply is received.

エラーリプライは、異なるデータ型に対する操作を実行しようとした、存在しないコマンドを実行した場合など、何か想定外のことが発生した場合に送信されます。クライアントライブラリではエラーリプライを受け取ったら、その言語の例外処理機構を使って例外を投げるべきでしょう。

.. Integer reply

数値リプライ
------------

.. This type of reply is just a CRLF terminated string representing an integer, 
   prefixed by a ":" byte. For example ":0\r\n", or ":1000\r\n" are integer replies.

先頭の1バイトが ``:`` で始まり、CRLFで終端されている文字列の場合、このリプライは数値であるという意味になります。例えば、 ``":0\r\n"`` や、 ``":1000\r\n"`` などが数値リプライになります。

.. With commands like INCR or LASTSAVE using the integer reply to actually return a 
   value there is no special meaning for the returned integer. It is just an incremental 
   number for INCR, a UNIX time for LASTSAVE and so on.

:com:`INCR` や :com:`LASTSAVE` のようなコマンドは実際に意味のある数値を数値リプライを使って返します。 :com:`INCR` の場合はインクリメンタルした数値を、 :com:`LASTSAVE` は、UNIX時間を返します。

.. Some commands like EXISTS will return 1 for true and 0 for false.

また、 :com:`EXISTS` などのコマンドは、True/Falseの意味で、1や0の数値を返します。

.. Other commands like SADD, SREM and SETNX will return 1 if the operation was 
   actually done, 0 otherwise.

:com:`SADD` や :com:`SREM` 、 :com:`SETNX` などの他のコマンドは、操作が実際に行われた場合に1を、そうでない場合に0を返します。

.. The following commands will reply with an integer reply: SETNX, DEL, EXISTS, INCR, 
   INCRBY, DECR, DECRBY, DBSIZE, LASTSAVE, RENAMENX, MOVE, LLEN, SADD, SREM, SISMEMBER, 
   SCARD

数値リプライを返すコマンド: :com:`SETNX`, :com:`DEL`, :com:`EXISTS`, :com:`INCR`, :com:`INCRBY`, :com:`DECR`, :com:`DECRBY`, :com:`DBSIZE`, :com:`LASTSAVE`, :com:`RENAMENX`, :com:`MOVE`, :com:`LLEN`, :com:`SADD`, :com:`SREM`, :com:`SISMEMBER`, :com:`SCARD`


.. Bulk replies

.. _bulk_reply:

バルクリプライ
--------------

.. Bulk replies are used by the server in order to return a single binary safe string.

バルクリプライは、単一のバイナリセーフな文字列を返すために使用されます。

.. code-block:: none

   C: GET mykey
   S: $6
   S: foobar

.. The server sends as the first line a "$" byte followed by the number of bytes 
   of the actual reply, followed by CRLF, then the actual data bytes are sent, 
   followed by additional two bytes for the final CRLF. The exact sequence sent 
   by the server is:

サーバは最初に ``$`` + バイト数 + CRLFというデータを送信し、その後実際のデータを送付し、最後に追加でCRLFの2バイトを送信します。サーバから送られる、正確な文字列は次のようになります。

.. code-block:: none

   "$6\r\nfoobar\r\n"

.. If the requested value does not exist the bulk reply will use the special value -1 
   as data length, example:

もし、要求された値が存在しない場合には、データ超として、特別に-1が返されます。

.. code-block:: none

   C: GET nonexistingkey
   S: $-1

.. The client library API should not return an empty string, but a nil object, 
   when the requested object does not exist. For example a Ruby library should 
   return 'nil' while a C library should return NULL (or set a special flag in 
   the reply object), and so forth.

要求されたオブジェクトが存在しない場合には、クライアントライブラリは空の文字列ではなく、nilオブジェクトを返すようにしてください。例えば、RubyのライブラリはCのライブラリが ``NULL`` を返すべきところでは、 ``nil`` を返したり、リプライオブジェクトに特別なフラグを設定したりします。

.. Multi-Bulk replies

.. _multi_bulk_reply:

マルチバルクリプライ
--------------------

.. Commands like LRANGE need to return multiple values (every element of the list is a 
   value, and LRANGE needs to return more than a single element). This is accomplished 
   using multiple bulk writes, prefixed by an initial line indicating how many bulk 
   writes will follow. The first byte of a multi bulk reply is always *. Example:

:com:`LRANGE` のようなコマンドは複数の値(リストの要素もすべて値で、このコマンドは一つ以上の要素を返す)を返します。この時にはまずいくつの要素があるかを出力し、その後複数回のバルク書き出しが行われます。

.. code-block:: none

   C: LRANGE mylist 0 3
   S: *4
   S: $3
   S: foo
   S: $3
   S: bar
   S: $5
   S: Hello
   S: $5
   S: World

.. As you can see the multi bulk reply is exactly the same format used in order to send 
   commands to the Redis server unsing the unified protocol.

みていただいた通り、マルチバルクリプライは、Redisサーバが使用する、統一プロトコルでコマンドを送るのに使用しているのとまったく同じフォーマットになっています。

.. The first line the server sent is "4\r\n" in order to specify that four bulk replies
   will follow. Then every bulk write is transmitted.

サーバが送信している最初の行の ``"4\r\n"`` は、この後4回バルクリプライが送信されることを表しています。その後、回数分のバルクリプライが送信されます。

.. If the specified key does not exist, instead of the number of elements in the list 
   the special value -1 is sent as count. Example:

もし指定されたキーが存在しなかった場合には、リストの要素数ではなく、 ``-1`` を返します。

.. code-block:: none

   C: LRANGE nokey 0 1
   S: *-1

.. A client library API SHOULD return a nil object and not an empty list when this 
   happens. This makes possible to distinguish between empty list and other error 
   conditions (for instance a timeout condition in the BLPOP command).

クライアントライブラリのAPIは、この場合は空のリストを返すのではなく、nilオブジェクトを返すようにしてください。これによって、例えば :com:`BLPOP` コマンドのタイムアウトのように、本当に空のリストだった場合と、その他の状況を区別できるようになります。

.. Nil elements in Multi-Bulk replies

マルチバルクリプライ中のnil要素
-------------------------------

.. Single elements of a multi bulk reply may have -1 length, in order to signal that 
   this elements are missing and not empty strings. This can happen with the SORT 
   command when used with the GET pattern option when the specified key is missing. 
   Example of a multi bulk reply containing an empty element:

マルチバルクリプライの要素の長さとして ``-1`` が返されると、その要素は空の文字列ではないというサインになります。これは、特定のキーが見つからない :com:`GET` パターンを :com:`SORT` の中で指定しまったときに発生する可能性があります。

.. code-block:: none

   S: *3
   S: $3
   S: foo
   S: $-1
   S: $3
   S: bar

.. The second element is nul. The client library should return something like this:

このリプライでは、2番目の要素がnulです。クライアントライブラリは次のような返り値を返すようにすべきです。

.. code-block:: ruby

   ["foo",nil,"bar"]

.. Multiple commands and pipelining

複数コマンドとパイプライン
--------------------------

.. A client can use the same connection in order to issue multiple commands. 
   Pipelining is supported so multiple commands can be sent with a single write 
   operation by the client, it is not needed to read the server reply in order to 
   issue the next command. All the replies can be read at the end.

クライアントは、1回のコネクションで複数のコマンドを発行することができます。一回の書き込み操作で、複数のコマンドを送信する、 :ref:`pipelining` がサポートされています。この場合は、次のコマンドの送信をする前に、サーバからの返信を待つ必要はなくなり、終了時にすべてのリプライを受け取ります。

.. Usually Redis server and client will have a very fast link so this is not very 
   important to support this feature in a client implementation, still if an application
   needs to issue a very large number of commands in short time to use pipelining can be
   much faster.

通常は、Redisサーバとクライアントは非常に高速にリンクを貼ることができるため、クライアントライブラリでこの機能をサポートすることは重要ではありませんが、クライアントから大量のコマンドを発行する必要があるのであれば、パイプラインを使用すると高速化できます。

.. The old protocol for sending commands

古いコマンド送信プロトコル
==========================

.. Before of the Unified Request Protocol Redis used a different protocol to send 
   commands, that is still supported since it is simpler to type by hand via telnet.
   In this protocol there are two kind of commands:

統一リクエストプロトコルを使用する前は、Redisは異なるプロトコルでコマンドを送信していました。このプロトコルはまだサポートされており、telnet越しにタイプできるぐらいシンプルです。このプロトコルには2種類のコマンドがあります。

.. Inline commands: simple commands where argumnets are just space separated strings. 
   No binary safeness is possible.

:ref:`inline_commands`
   スペース区切りの文字列で引き数を渡す、シンプルなコマンドです。バイナリセーフではありません。

.. Bulk commands: bulk commands are exactly like inline commands, but the last argument
   is handled in a special way in order to allow for a binary-safe last argument.

:ref:`bulk_commands`
   バルクコマンドはインラインコマンドと似ていますが、最後の引き数をバイナリセーフで扱えるように、最後の引き数だけを特別な方法で扱います。

.. Inline Commands

.. _inline_commands:

インラインコマンド
------------------

.. The simplest way to send Redis a command is via Inline Commands. The following is an 
   example of a server/client chat using an inline command (the server chat starts with 
   S:, the client chat with C:)

Redisにコマンドを送る、もっとも簡単な方法が、このインラインコマンドです。次の例は、サーバ/クライアント間でインラインコマンドを使って通信しあっています。(サーバ側は ``S:`` 、クライアント側は ``C`` と書いています)

.. code-block:: none

   C: PING
   S: +PONG

.. The following is another example of an INLINE command returning an integer:

次の例は、数値を返す場合のインラインコマンドの例です。

.. code-block:: none

   C: EXISTS somekey
   S: :0

.. Since 'somekey' does not exist the server returned ':0'.

``somekey`` が存在していなかったため、 ``:0`` が返ってきています。

.. Note that the EXISTS command takes one argument. Arguments are separated by spaces.

:com:`EXISTS` コマンドは一つの引き数を受け取リますが、ここではスペース区切りで一緒に記述していることに注意してください。

.. Bulk commands

.. _bulk_commands:

バルクコマンド
--------------

.. Some commands when sent as inline commands require a special form in order to 
   support a binary safe last argument. This commands will use the last argument 
   for a "byte count", then the bulk data is sent (that can be binary safe since
   the server knows how many bytes to read).

いくつかのコマンドは、最後の引き数をバイナリセーフでサーバに送信するために、特別な形式を使ってコマンドを送る必要があります。このコマンドは最後の引き数にバイト数のカウントを設定し、その後、バルクデータを送信します。サーバ側は、何バイト読み込めばよいかを知っているため、安全にこのデータを利用できます。

.. See for instance the following example:

次の例がサンプルになります。

.. code-block:: none

   C: SET mykey 6
   C: foobar
   S: +OK

.. The last argument of the commnad is '6'. This specify the number of DATA bytes 
   that will follow, that is, the string "foobar". Note that even this bytes are 
   terminated by two additional bytes of CRLF.

コマンドの最後の引き数が ``'6'`` になっています。これは次に続くデータのバイト数を表しています。ここでは、次に来る ``"foobar"`` という文字列です。この文字列の後ろには CRLF の2バイトが付加されます。

.. All the bulk commands are in this exact form: instead of the last argument the number 
   of bytes that will follow is specified, followed by the bytes composing the argument 
   itself, and CRLF. In order to be more clear for the programmer this is the string 
   sent by the client in the above sample:

すべてのバルクコマンドはこの形式になっています。最後の引き数として数値が入り、この後ろに送信したいバイナリが付加され、最後にCRLFが来ます。プログラマ向けにもっとわかりやすく表現すると、上記の例は次のような文字列としてクライアントから送信されます。

.. code-block:: none

   "SET mykey 6\r\nfoobar\r\n"

.. Redis has an internal list of what command is inline and what command is bulk, so you 
   have to send this commands accordingly. It is strongly suggested to use the new 
   Unified Request Protocol instead.

Redisは内部で、どのコマンドがインラインで、どのコマンドがバルクなのか、というリストを持っています。クライアントはそれに従ってコマンドを送信する必要があります。現在では、このプロトコルの代わりに、新しい統一リクエストプロトコルを使うことを推奨します。
