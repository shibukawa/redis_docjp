.. -*- coding: utf-8 -*-;

======================
 全データ型対応の操作
======================

.. command:: EXISTS key
   
   計算時間: O(1)

   .. Test if the specified key exists. The command returns "0" if the key exists, otherwise "1" is returned. Note that even keys set with an empty string as value will return "1".
   
   指定されたキー ``key`` が存在するか確認します。存在する場合は"0"が返ります。存在しない場合は"1"が返ります。キーに対応する値が空文字列でも"1"が返ることに注意してください。
   
   .. Return value
   
   **返り値**

     .. Integer reply, specifically:

     Integer reply（整数値）。具体的には下記::

       1 if the key exists.
       0 if the key does not exist.



.. command:: DEL key1 key2 ... keyN

   計算時間: O(1)

   .. Remove the specified keys. If a given key does not exist no operation is performed for this key. The command returns the number of keys removed.
   
   指定された複数のキー ``keyN`` を削除します。キーが存在しない場合は何の操作も行われません。返り値は削除されたキーの数となります。
   
   .. Return value

   **返り値**

     .. Integer reply, specifically:

     Integer reply（整数値）。具体的には下記::
   
       an integer greater than 0 if one or more keys were removed
       0 if none of the specified key existed


.. command:: TYPE key

   計算時間: O(1)

   .. Return the type of the value stored at key in form of a string. The type can be one of "none", "string", "list", "set". "none" is returned if the key does not exist.
   
   キー ``key`` で格納されている値の型を文字列型で返します。型は "none", "string", "list", "set"のいずれかです。 "none"はキーが存在しない場合に返ります。

   .. note:: "sortedset"はないのか？要確認。

   .. Return value
   
   **返り値**

     .. Status code reply, specifically:

     Status code reply（ステータスコード）。具体的には下記::

      "none" if the key does not exist
      "string" if the key contains a String value
      "list" if the key contains a List value
      "set" if the key contains a Set value
      "zset" if the key contains a Sorted Set value
      "hash" if the key contains a Hash value
   
   .. See also

   **参照**
   
     .. Redis Data Types
     
     Redisデータ型

     .. note:: あとで各データ型へのリンクを貼る


.. command:: KEYS pattern
   .. (with n being the number of keys in the DB, and assuming keys and pattern of limited length)

   計算時間: O(N) （nはデータベース内のキーの数。キーとパターンの数は制限されていると想定している。）

   .. Returns all the keys matching the glob-style pattern as space separated strings. For example if you have in the database the keys "foo" and "foobar" the command "KEYS foo*" will return "foo foobar".

   glob形式のパターン ``pattern`` にマッチするすべてのキーを空白区切りの文字列で返します。例えばデータベース内に"foo"と"foobar"というキーがある場合は ``KEYS foo*`` というコマンドで"foo foobar"という文字列が返ります。

   .. Note that while the time complexity for this operation is O(n) the constant times are pretty low. For example Redis running on an entry level laptop can scan a 1 million keys database in 40 milliseconds. Still it's better to consider this one of the slow commands that may ruin the DB performance if not used with care.

   この操作は計算時間O(n)となっているが、定数時間は非常に小さいものとなっています。たとえばRedisはエントリーモデルのノートPCで100万キーを持つデータベースを40ミリ秒で読み込みます。もちろんこのコマンドは注意深く使わないとデータベース性能を落としてしまうということを意識するにこしたことはありません。

   .. In other words this command is intended only for debugging and special operations like creating a script to change the DB schema. Don't use it in your normal code. Use Redis Sets in order to group together a subset of objects.

   言い換えると、このコマンドはデバッグやデータベースのスキーマの変更を行うなどの特別な操作を除いて使うべきではありません。通常のコードでは使わないでください。オブジェクトのサブセットをくっつけたい場合はRedisセット型を使ってください。

   .. Glob style patterns examples:

   glob形式のパターンの例です::

      h?llo will match hello hallo hhllo
      h*llo will match hllo heeeello
      h[ae]llo will match hello and hallo, but not hillo
      Use \ to escape special chars if you want to match them verbatim.
   
   .. Return value
   
   **返り値**
   
      .. Multi bulk reply

      Multi bulk replyが返る


.. command:: RANDOMKEY

   計算時間: O(1)

   .. Return a randomly selected key from the currently selected DB.

   現在選択してされているデータベースからランダムでキーをひとつ選択して返します。

   .. Return value
   
   **返り値**

   .. Singe line reply, specifically the randomly selected key or an empty string is the database is empty.
   
   Single line reply（単一行）が返ります。具体的にはランダムに選択されたキーまたはデータベースが空のときは空文字列が返ります。


.. command:: RENAME oldkey newkey

   計算時間: O(1)

   .. Atomically renames the key oldkey to newkey. If the source and destination name are the same an error is returned. If newkey already exists it is overwritten.

   自動的にキー ``oldkey`` を ``newkey`` にリネームします。もし古いキーと新しいキーの名前が一緒だった場合はエラーが返ります。 ``newkey`` が存在する場合は上書きされます。

   .. Return value

   **返り値**

     .. Status code repy

     Status code reply（ステータスコード）が返ります。


.. command:: RENAMENX oldkey newkey

   計算時間: O(1)

   .. Rename oldkey into newkey but fails if the destination key newkey already exists.

   .. Return value
   
   **返り値**

     .. Integer reply, specifically:

     Integer reply（整数値）が返ります。具体的には下記::

       1 if the key was renamed
       0 if the target key already exist

.. command:: DBSIZE

   .. Return the number of keys in the currently selected database.

   現在選択されているデータベースのキーの数を返します。
   
   .. Return value
   
   **返り値**

     .. Integer reply

     Integer reply（整数値）


.. command:: EXPIRE key seconds
.. command:: EXPIREAT key unixtime (Redis >= 1.1)
.. command:: PERSIST key
   計算時間: O(1)

   .. Set a timeout on the specified key. After the timeout the key will be automatically deleted by the server. A key with an associated timeout is said to be volatile in Redis terminology.

   指定したキー ``key`` のタイムアウト時間 ``seconds`` を設定する。タイムアウト時間が過ぎたらキーはサーバによって自動的に削除されます。タイムアウト時間が設定されたキーはRedis用語では"volatile"（揮発性がある）と呼ばれます。

   .. Voltile keys are stored on disk like the other keys, the timeout is persistent too like all the other aspects of the dataset. Saving a dataset containing expires and stopping the server does not stop the flow of time as Redis stores on disk the time when the key will no longer be available as Unix time, and not the remaining seconds.

   揮発性のキーは他のキーのようにディスクに書き込まれます。タイムアウト時間は他のデータセットの性質と同様に永続的なものです。揮発性のキーを持っているデータセットを保存してからサーバを停止しても、Redis内の時間経過は止まりません。Redisはディスクに保存する際にそのキーがいつ無効になるかを残り時間ではなくUNIX時間で記録しているのでこれが実現できるのです。

   .. EXPIREAT works exctly like EXPIRE but instead to get the number of seconds representing the Time To Live of the key as a second argument (that is a relative way of specifing the TTL), it takes an absolute one in the form of a UNIX timestamp (Number of seconds elapsed since 1 Gen 1970).

   :com:`EXPIREAT` は :com:`EXPIRE` と同様に動作しますが、 :com:`TTL` で取得できるような残り秒数ではなく、UNIX時間の形で絶対時刻を有効期限を指定します。

   .. EXPIREAT was introduced in order to implement the Append Only File persistence mode so that EXPIRE commands are automatically translated into EXPIREAT commands for the append only file. Of course EXPIREAT can also used by programmers that need a way to simply specify that a given key should expire at a given time in the future.

   :com:`EXPIREAT` はAppend Only File（追記専用ファイル）の永続モードの実装のために作成されました。これによって、追記専用ファイルの場合は :com:`EXPIRE` コマンドは自動的に :com:`EXPIREAT` コマンドに変換されます。もちろん :com:`EXPIREAT` はプログラマが単純に指定したキーを将来指定しあ時刻に無効にさせる、というような用途で使うことができます。

   .. Since Redis 2.1.3 you can update the value of the timeout of a key already having an expire set. It is also possible to undo the expire at all turning the key into a normal key using the PERSIST command.

   Redis 2.1.3からすでにタイムアウト時間を設定したキーに対して、タイムアウト時間を更新することが出来るようになりました。またタイムアウト時間を設定したキー全てに対して、 :com:`PERSIST` コマンドを使ってタイムアウトを無効にすることも出来るようになりました。

   .. How the expire is removed from a key

   どのようにキーからタイムアウトが削除されるか

     .. When the key is set to a new value using the SET command, or when a key is destroied via DEL, the timeout is removed from the key.

     :com:`SET` を使ってキーに新しい値が紐付けれたとき、あるいはキーが :com:`DEL` コマンドで削除されたときにタイムアウトが削除されます。

   .. Restrictions with write operations against volatile keys

   揮発性のキーに対する書き込み制限

     .. IMPORTANT: Since Redis 2.1.3 or greater, there are no restrictions about the operations you can perform against volatile keys, however older versions of Redis, including the current stable version 2.0.0, has the following limitations:

     .. warning:: Redis 2.1.3以上では揮発性のキーに対する書き込み制限は一切ありません。しかし現在の安定版2.0.0を含むそれ以前のバージョンでは次のような制限があります。

     .. Write operations like LPUSH, LSET and every other command that has the effect of modifying the value stored at a volatile key have a special semantic: basically a volatile key is destroyed when it is target of a write operation. See for example the following usage pattern:

     揮発性のキーに対応する値に対して修正を行うような :com:`LPUSH`, :com:`LSET` などの操作に対しては特別なセマンティクスがあります。基本的に揮発性のキーは書き込みの対象となった場合は破壊されます。以下の例を見て下さい::

       % ./redis-cli lpush mylist foobar /Users/antirez/hack/redis
       OK
       % ./redis-cli lpush mylist hello  /Users/antirez/hack/redis
       OK
       % ./redis-cli expire mylist 10000 /Users/antirez/hack/redis
       1
       % ./redis-cli lpush mylist newelement
       OK
       % ./redis-cli lrange mylist 0 -1  /Users/antirez/hack/redis
       1. newelement
       

.. command:: TTL key

   .. The TTL command returns the remaining time to live in seconds of a key that has an EXPIRE set. This introspection capability allows a Redis client to check how many seconds a given key will continue to be part of the dataset. If the Key does not exists or does not have an associated expire, -1 is returned.

   :com:`TTL` コマンドは :com:`EXPIRE` が設定されたキー ``key`` の存命時間を秒で返す。このコマンドで確認できることによって、Redisクライアントが与えられたキーがあとどれくらいデータセットの一部であるか確認することができます。もしキーが存在しない、あるいは :com:`EXPIRE` が設定されていない場合は"-1"が返ります。

   .. Return value

   **返り値**

     Integer reply（整数値）が返ります


.. command:: SELECT index

   .. Select the DB with having the specified zero-based numeric index. For default every new client connection is automatically selected to DB 0.

   ゼロから始まる数値 ``index`` インデックス付けされたデータベースを選択します。デフォルトの設定では新しいクライアント自動的にDB 0に接続されます。
   
   .. Return value

   **返り値**

     Status code reply（ステータスコード）が返ります。


.. command:: MOVE key dbindex

   .. Move the specified key from the currently selected DB to the specified destination DB. Note that this command returns 1 only if the key was successfully moved, and 0 if the target key was already there or if the source key was not found at all, so it is possible to use MOVE as a locking primitive.

   指定したキー ``key`` を現在選択されているデータベースから指定したインデックス ``index`` のデータベースに移します。無事移動できた場合のみ"1"を返し、対象のキーがすでに指定したデータベースに存在する、または対象のキーが見つからない場合は"0"を返します。この性質から :com:`MOVE` をロックのために使うこともできます。

   .. Return value
   
   **返り値**

     Integer reply（整数値）が返ります。具体的には下記::

       1 if the key was moved
       0 if the key was not moved because already present on the target DB or was not found in the current DB.


.. command:: FLUSHDB

   .. Delete all the keys of the currently selected DB. This command never fails.

   現在選択されているデータベースからすべてのキーを削除します。このコマンドは決して失敗しません。

   .. Return value

   **返り値**

     Status code reply（ステータスコード）が返ります。


.. command:: FLUSHALL

   .. Delete all the keys of all the existing databases, not just the currently selected one. This command never fails.

   現在選択されているものだけでなく、存在するすべてのデータベースからすべてのキーを削除します。このコマンドは決して失敗しません。

   .. Return value
   
   **返り値**

     Status code reply（ステータスコード）が返ります。


.. command:: WATCH key1 key2 ... keyN (Redis >= 2.1.0)
.. command:: UNWATCH
.. command:: MULTI
.. command:: COMMAND_1 ...
.. command:: COMMAND_2 ...
.. command:: COMMAND_N ...
.. command:: EXEC
.. command:: DISCARD

   .. MULTI, EXEC, DISCARD and WATCH commands are the foundation of Redis Transactions. A Redis Transaction allows the execution of a group of Redis commands in a single step, with two important guarantees:

   :com:`MULTI`, :com:`EXEC`, :com:`DISCARD`, :com:`WATCH` コマンドはRedisトランザクションの基礎です。Redisトランザクションでは単一ステップでひとまとめのRedisコマンドを実行出来るようにしてあります。このトランザクションでは２つのことが保証されています:

   .. All the commands in a transaction are serialized and executed sequentially. It can never happen that a request issued by another client is served in the middle of the execution of a Redis transaction. This guarantees that the commands are executed as a single atomic operation.

   トランザクション中のすべてのコマンドはシリアライズ化され、順番に実行されます。他のクライアントからのリクエストがRedisトランザクションの実行中に行われることは決してありません。このことによって一連のコマンドは単一のアトミックな操作として扱われることが保証されます。

   .. Either all of the commands or none are processed. The EXEC command triggers the execution of all the commands in the transaction, so if a client loses the connection to the server in the context of a transaction before calling the MULTI command none of the operations are performed, instead if the EXEC command is called, all the operations are performed. An exception to this rule is when the Append Only File is enabled: every command that is part of a Redis transaction will log in the AOF as long as the operation is completed, so if the Redis server crashes or is killed by the system administrator in some hard way it is possible that only a partial number of operations are registered.

   すべてのコマンドが実行されるか全く実行されないかのどちらかとなります。 :com:`EXEC` コマンドはトランザクション中のすべてのコマンドの実行のトリガーとなります。なので、もしクライアントが :com:`MULTI` を呼び出す前にサーバへの接続を失った場合は、操作はひとつも実行されませんが、 :com:`EXEC` を呼べばすべての操作が実行されます。このルールの例外としてAppend Only File（追記専用ファイル、以下AOF）が有効になっている場合があります。この場合、Redisトランザクションに関するコマンドは操作が完了するまではAOFにログを録ります。したがってもしRedisサーバがクラッシュする、もしくはシステムアドミニストレータによってkillされたとき、トランザクションの操作の中から部分的に実行された分が登録される、ということが起きえます。

   .. Since Redis 2.1.0, it's also possible to add a further guarantee to the above two, in the form of optimistic locking of a set of keys in a way very similar to a CAS (check and set) operation. This is documented later in this manual page.

   Redis 2.1.0から、上記の２項目に加えてさらにCAS（check and set）操作に似た方法でキーの束を楽観的ロックすることが可能になりました。これについては本文のあとの方で説明します。

   .. Usage

   **使い方**


A Redis transaction is entered using the MULTI command. The command always replies with OK. At this point the user can issue multiple commands. Instead of executing these commands, Redis will "queue" them. All the commands are executed once EXEC is called.

Calling DISCARD instead will flush the transaction queue and will exit the transaction.

The following is an example using the Ruby client:

?> r.multi
=> "OK"
>> r.incr "foo"
=> "QUEUED"
>> r.incr "bar"
=> "QUEUED"
>> r.incr "bar"
=> "QUEUED"
>> r.exec
=> [1, 1, 2]
As it is possible to see from the session above, MULTI returns an "array" of replies, where every element is the reply of a single command in the transaction, in the same order the commands were queued.

When a Redis connection is in the context of a MULTI request, all the commands will reply with a simple string "QUEUED" if they are correct from the point of view of the syntax and arity (number of arguments) of the commaand. Some commands are still allowed to fail during execution time.

This is more clear on the protocol level; In the following example one command will fail when executed even if the syntax is right:

Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
MULTI
+OK
SET a 3 
abc
+QUEUED
LPOP a
+QUEUED
EXEC
*2
+OK
-ERR Operation against a key holding the wrong kind of value
MULTI returned a two elements bulk reply where one is an +OK code and one is a -ERR reply. It's up to the client lib to find a sensible way to provide the error to the user.

IMPORTANT: even when a command will raise an error, all the other commands in the queue will be processed. Redis will NOT stop the processing of commands once an error is found.
Another example, again using the write protocol with telnet, shows how syntax errors are reported ASAP instead:

MULTI
+OK
INCR a b c
-ERR wrong number of arguments for 'incr' command
This time due to the syntax error the "bad" INCR command is not queued at all.

The DISCARD command
DISCARD can be used in order to abort a transaction. No command will be executed, and the state of the client is again the normal one, outside of a transaction. Example using the Ruby client:

?> r.set("foo",1)
=> true
>> r.multi
=> "OK"
>> r.incr("foo")
=> "QUEUED"
>> r.discard
=> "OK"
>> r.get("foo")
=> "1"
Check and Set (CAS) transactions using WATCH
WATCH is used in order to provide a CAS (Check and Set) behavior to Redis Transactions.

WATCHed keys are monitored in order to detect changes against this keys. If at least a watched key will be modified before the EXEC call, the whole transaction will abort, and EXEC will return a nil object (A Null Multi Bulk reply) to notify that the transaction failed.

For example imagine we have the need to atomically increment the value of a key by 1 (I know we have INCR, let's suppose we don't have it).

The first try may be the following:

val = GET mykey
val = val + 1
SET mykey $val
This will work reliably only if we have a single client performing the operation in a given time. If multiple clients will try to increment the key about at the same time there will be a race condition. For instance client A and B will read the old value, for instance, 10. The value will be incremented to 11 by both the clients, and finally SET as the value of the key. So the final value will be "11" instead of "12".

Thanks to WATCH we are able to model the problem very well:

WATCH mykey
val = GET mykey
val = val + 1
MULTI
SET mykey $val
EXEC
Using the above code, if there are race conditions and another client modified the result of val in the time between our call to WATCH and our call to EXEC, the transaction will fail.

We'll have just to re-iterate the operation hoping this time we'll not get a new race. This form of locking is called optimistic locking and is a very powerful form of locking as in many problems there are multiple clients accessing a much bigger number of keys, so it's very unlikely that there are collisions: usually operations don't need to be performed multiple times.

WATCH explained
So what is WATCH really about? It is a command that will make the EXEC conditional: we are asking Redis to perform the transaction only if no other client modified any of the WATCHed keys. Otherwise the transaction is not entered at all. (Note that if you WATCH a volatile key and Redis expires the key after you WATCHed it, EXEC will still work. More.)

WATCH can be called multiple times. Simply all the WATCH calls will have the effects to watch for changes starting from the call, up to the moment EXEC is called.

When EXEC is called, either if it will fail or succeed, all keys are UNWATCHed. Also when a client connection is closed, everything gets UNWATCHed.

It is also possible to use the UNWATCH command (without arguments) in order to flush all the watched keys. Sometimes this is useful as we optimistically lock a few keys, since possibly we need to perform a transaction to alter those keys, but after reading the current content of the keys we don't want to proceed. When this happens we just call UNWATCH so that the connection can already be used freely for new transactions.

WATCH used to implement ZPOP
A good example to illustrate how WATCH can be used to create new atomic operations otherwise not supported by Redis is to implement ZPOP, that is a command that pops the element with the lower score from a sorted set in an atomic way. This is the simplest implementation:

WATCH zset
ele = ZRANGE zset 0 0
MULTI
ZREM zset ele
EXEC
If EXEC fails (returns a nil value) we just re-iterate the operation.

   .. Return value

   **戻り値**

     Multi bulk replyを返します。具体的には下記::

       The result of a MULTI/EXEC command is a multi bulk reply where every element is the return value of every command in the atomic transaction.

If a MULTI/EXEC transaction is aborted because of WATCH detected modified keys, a Null Multi Bulk reply is returned.
