.. -*- coding: utf-8 -*-;

======================
 全データ型対応の操作
======================

.. command:: EXISTS key

   計算時間: O(1)

   .. Test if the specified key exists. The command returns "0" if the key exists, otherwise "1" is returned. Note that even keys set with an empty string as value will return "1".

   指定されたキー ``key`` が存在するか確認します。存在する場合は"1"が返ります。存在しない場合は"0"が返ります。キーに対応する値が空文字列でも"1"が返ることに注意してください。

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

.. command:: EXPIREAT key unixtime
   .. versionadded:: 1.1

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

   **どのようにキーからタイムアウトが削除されるか**

     .. When the key is set to a new value using the SET command, or when a key is destroied via DEL, the timeout is removed from the key.

     :com:`SET` を使ってキーに新しい値が紐付けれたとき、あるいはキーが :com:`DEL` コマンドで削除されたときにタイムアウトが削除されます。

   .. Restrictions with write operations against volatile keys

   **揮発性のキーに対する書き込み制限**

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


.. command:: WATCH key1 key2 ... keyN

   .. versionadded:: 2.1.0

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

     .. A Redis transaction is entered using the MULTI command. The command always replies with OK. At this point the user can issue multiple commands. Instead of executing these commands, Redis will "queue" them. All the commands are executed once EXEC is called.

     Redisのトランザクションは :com:`MULTI` コマンドを使って登録します。コマンドはつねにOKを返します。このときユーザは複数のコマンドを発行できます。これらのコマンドを実行する代わりに、Redisではキューにためます。キュー内のコマンドは :com:`EXEC` が呼ばれたタイミングで実行されます。


     .. Calling DISCARD instead will flush the transaction queue and will exit the transaction.

     :com:`DISCARD` を呼ぶとトランザクションキューをフラッシュして、トランザクションから出ます。

     .. The following is an example using the Ruby client:

     Rubyクライアントのでの例です::

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

     .. As it is possible to see from the session above, MULTI returns an "array" of replies, where every element is the reply of a single command in the transaction, in the same order the commands were queued.

     この例でわかるように、 :com:`MULTI` はトランザクション中の各コマンドの返り値を要素に持った配列を返します。要素の並び順はコマンドの並び順に一致します。

     .. When a Redis connection is in the context of a MULTI request, all the commands will reply with a simple string "QUEUED" if they are correct from the point of view of the syntax and arity (number of arguments) of the commaand. Some commands are still allowed to fail during execution time.

     Redisへ接続している間に :com:`MULTI` が呼びだされたとき、すべてのコマンドが文法上も引数も正しく呼びだされたときは文字列 "QUEUED" を返します。実行時にうまく動作しなくてもかまいません。

     .. This is more clear on the protocol level; In the following example one command will fail when executed even if the syntax is right

     プロトコルレベルではより明確に見て取れます。次の例は文法上正しいですが実行時にコマンドが失敗する例です::

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

     .. MULTI returned a two elements bulk reply where one is an +OK code and one is a -ERR reply. It's up to the client lib to find a sensible way to provide the error to the user.

     :com:`MULTI` は要素が2つのBulk replyを返してきました。そのうち一つは"+OK"でもう一つは"-ERR"です。ユーザにエラーを提供する方法はクライアントライブラリ次第です。

     .. even when a command will raise an error, all the other commands in the queue will be processed. Redis will NOT stop the processing of commands once an error is found.
     .. Another example, again using the write protocol with telnet, shows how syntax errors are reported ASAP instead

     .. warning::
        コマンドがエラーをあげたときですら、キューに入っているそれ以外のコマンドは処理されます。Redisはエラーが得られたとしてもプロセスを **止めません** 。
        他の例では再度telnetを用いて書き込みプロトコルを使っていますが、文法エラーができるだけ早く報告されるように設定しています::

       MULTI
       +OK
       INCR a b c
       -ERR wrong number of arguments for 'incr' command

     .. This time due to the syntax error the "bad" INCR command is not queued at all.

     この場合は、文法エラーによって"bad"な :com:`INCR` コマンドはキューに入りませんでした。


   .. The DISCARD command

   **DISCARDコマンド**

     .. DISCARD can be used in order to abort a transaction. No command will be executed, and the state of the client is again the normal one, outside of a transaction. Example using the Ruby client:

     :com:`DISCARD` はトランザクションを中止するために用いられます。それ以降のコマンドは実行されません。そしてクライアントの状態がトランザクション外では再度通常となります。Rubyクライアントの例を挙げます::

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

   .. Check and Set (CAS) transactions using WATCH

   **確認とWATCHを用いたセット(CAS)トランザクション**

     .. WATCH is used in order to provide a CAS (Check and Set) behavior to Redis Transactions.

     :com:`WATCH` はRedisトランザクションにCAS (Check and Set)ビヘイビアを提供するために用います。

     .. WATCHed keys are monitored in order to detect changes against this keys. If at least a watched key will be modified before the EXEC call, the whole transaction will abort, and EXEC will return a nil object (A Null Multi Bulk reply) to notify that the transaction failed.

     :com:`WATCH` されたキーは変更を検知するために監視されています。もし :com:`EXEC` を呼ぶ前にこれらのキーが修正された場合、すべてのトランザクションは中止され、 :com:`EXEC` はトランザクションが失敗したことを通知するためにnilオブジェクトを返します。（Null Multi Bulk replyが返ります）

     .. For example imagine we have the need to atomically increment the value of a key by 1 (I know we have INCR, let's suppose we don't have it).

     たとえばキーを自動的に1増やさないといけないという状況を考えてみましょう。（ :com:`INCR` コマンドがあることは承知ですが、いまは忘れておきましょう）

     .. The first try may be the following

     まずはこんな例を考えてみましょう::

       val = GET mykey
       val = val + 1
       SET mykey $val

     .. This will work reliably only if we have a single client performing the operation in a given time. If multiple clients will try to increment the key about at the same time there will be a race condition. For instance client A and B will read the old value, for instance, 10. The value will be incremented to 11 by both the clients, and finally SET as the value of the key. So the final value will be "11" instead of "12".

     このサンプルは1つのクライアントが限られた時間で動作する場合であれば上手く動くと思います。もし複数のクライアントが同時にキーをインクリメントしようとしたら、競合状態に陥ります。例えば、クライアントAとクライアントBが古い値、ここでは10としますが、を読んだとします。この値は両方のクライアントによってインクリメントされ11となります。そして最終的にそのキーの値として12ではなく11がセットされてしまうのです。

     .. Thanks to WATCH we are able to model the problem very well

     :com:`WATCH` コマンドのおかげでこの問題をうまく解決できます::

       WATCH mykey
       val = GET mykey
       val = val + 1
       MULTI
       SET mykey $val
       EXEC

     .. Using the above code, if there are race conditions and another client modified the result of val in the time between our call to WATCH and our call to EXEC, the transaction will fail.

     上記のコードを使うことで、もし競合状態になって他のクライアントが :com:`WATCH` と :com:`EXEC` の間に ``val`` の値を修正した場合はトランザクションは失敗します。

     .. We'll have just to re-iterate the operation hoping this time we'll not get a new race. This form of locking is called optimistic locking and is a very powerful form of locking as in many problems there are multiple clients accessing a much bigger number of keys, so it's very unlikely that there are collisions: usually operations don't need to be performed multiple times.

     この場合出来ることは、再度操作を実行して今度は競合状態にならないことを願うだけです。このような形式でのロックは楽観的ロックと呼ばれ、複数のクライアントが非常に多くのキーにアクセスするような多くの問題で非常に有力なロック形式となっています。衝突が起きる、ということはあまりありません。なので普通は操作を何度もやり直すということはありません。

   **WATCH explained**

     .. So what is WATCH really about? It is a command that will make the EXEC conditional: we are asking Redis to perform the transaction only if no other client modified any of the WATCHed keys. Otherwise the transaction is not entered at all. (Note that if you WATCH a volatile key and Redis expires the key after you WATCHed it, EXEC will still work. More.)

     では :com:`WATCH` は実際には何をするものなのでしょうか。それは :com:`EXEC` に条件をつけるコマンドと理解してください。Redisにもし他のクライアントが :com:`WATCH` したキーを修正しなかった場合のみトランザクション処理を行うという条件をつけるのです。もし修正されてしまった場合はトランザクションは実行されません。（ :com:`WATCH` で揮発性のキーを監視して、Redisが監視開始後にそのキーを無効とした場合、 :com:`EXEC` は動作することに注意してください）

     .. WATCH can be called multiple times. Simply all the WATCH calls will have the effects to watch for changes starting from the call, up to the moment EXEC is called.

     :com:`WATCH` は複数回呼ぶことが出来ます。すべての :com:`WATCH` の呼出しにおいて、それぞれの呼び出し時から :com:`EXEC` の呼び出し時まで監視は有効になっています。

     .. When EXEC is called, either if it will fail or succeed, all keys are UNWATCHed. Also when a client connection is closed, everything gets UNWATCHed.

     :com:`EXEC` が呼び出されたとき、成功したかどうかにかかわらず、すべてのキーは :com:`UNWATCH` の状態になります。クライアントの接続が閉じた時も同様です。

     .. It is also possible to use the UNWATCH command (without arguments) in order to flush all the watched keys. Sometimes this is useful as we optimistically lock a few keys, since possibly we need to perform a transaction to alter those keys, but after reading the current content of the keys we don't want to proceed. When this happens we just call UNWATCH so that the connection can already be used freely for new transactions.

     すべての監視下のキーをフラッシュするために :com:`UNWATCH` コマンドを使うこともできます（引数はありません）。たとえばいくつかのキーを楽観的ロックしたあとに、それらのキーを変更したいという理由でトランザクションをしたい時があります。しかしキーに対応する現在の値を読んだあとにはもう処理を行ないたくない、というときに :com:`UNWATCH` を使います。これでコネクションは新しいトランザクションの為に使えます。

     .. note:: このパラグラフ翻訳があやしい

   **WATCH used to implement ZPOP**

     .. A good example to illustrate how WATCH can be used to create new atomic operations otherwise not supported by Redis is to implement ZPOP, that is a command that pops the element with the lower score from a sorted set in an atomic way. This is the simplest implementation

     :com:`WATCH` コマンドを使ってアトミックな操作を作成する良い例を次に示します。それを見ることで、 :com:`WATCH` が無かったら :com:`ZPOP` が実装できなかったとわかるでしょう。 :com:`ZPOP` はソート済みセットの低いスコアの方から要素をアトミックにポップするコマンドです。これは最も単純な実装例です::

       WATCH zset
       ele = ZRANGE zset 0 0
       MULTI
       ZREM zset ele
       EXEC

    .. If EXEC fails (returns a nil value) we just re-iterate the operation.

    もし :com:`EXEC` が失敗したら（nil値を返したら）、単純に操作を再実行するだけです。

   .. Return value

   **戻り値**

     Multi bulk replyを返します。具体的には下記::

       The result of a MULTI/EXEC command is a multi bulk reply where every element is the return value of every command in the atomic transaction.

     .. If a MULTI/EXEC transaction is aborted because of WATCH detected modified keys, a Null Multi Bulk reply is returned.

     もし :com:`MULTI`/:com:`EXEC` トランザクションが :com:`WATCH` がキーが修正されたのを検知したせいで中止になった場合、Null Multi Bulk replyが返ります。


.. command:: SORT key [BY pattern] [LIMIT start count] [GET pattern] [ASC|DESC] [ALPHA] [STORE dstkey]

   .. Sort the elements contained in the List, Set, or Sorted Set value at key. By default sorting is numeric with elements being compared as double precision floating point numbers. This is the simplest form of SORT

   リスト、セット、ソート済みセット内の要素をキーに対応する値でソートします。デフォルトではソートは倍精度浮動小数の値で比較されます。次はは最も単純な形のソートです。

   .. code-block:: none

      SORT mylist

   .. Assuming mylist contains a list of numbers, the return value will be the list of numbers ordered from the smallest to the biggest number. In order to get the sorting in reverse order use DESC:

   ``mylist`` は数字のリストを保持しています。返り値は昇順に並び替えられたリストとなります。もし降順にしたい場合は ``DESC`` を使います。

   .. code-block:: none

      SORT mylist DESC

   .. The ASC option is also supported but it's the default so you don't really need it. If you want to sort lexicographically use ALPHA. Note that Redis is utf-8 aware assuming you set the right value for the LC_COLLATE environment variable.

   ``ASC`` も使えますが、デフォルトで指定されているので使う必要はありません。もし辞書順で並び替えたいときは ``ALPHA`` を使います。 RedisはUTF-8を前提にしているので、他の文字コードを使う場合は正しく ``LC_COLLATE`` を設定してください。

   .. Sort is able to limit the number of returned elements using the LIMIT option:

   ``LIMIT`` オプションを使うことで返す要素数を制限することも出来ます。

   .. code-block:: none

      SORT mylist LIMIT 0 10

   .. In the above example SORT will return only 10 elements, starting from the first one (start is zero-based). Almost all the sort options can be mixed together. For example the command:

   上の例では :com:`SORT` は最初の要素（0番目）から始めて10要素を返します。ほぼすべてのソートのオプションは一緒に使えます。たとえばこんな感じです。

   .. code-block:: none

      SORT mylist LIMIT 0 10 ALPHA DESC

   .. Will sort mylist lexicographically, in descending order, returning only the first 10 elements.

   この例では ``mylist`` は辞書順で降順にソートされ、最初の10要素を返します。

   .. Sometimes you want to sort elements using external keys as weights to compare instead to compare the actual List Sets or Sorted Set elements. For example the list mylist may contain the elements 1, 2, 3, 4, that are just unique IDs of objects stored at object_1, object_2, object_3 and object_4, while the keys weight_1, weight_2, weight_3 and weight_4 can contain weights we want to use to sort our list of objects identifiers. We can use the following command:

   時にリスト、セット、ソート済みセット内の要素を直接比較するのではなく、外部キーを重みとしてソートしたい時があります。たとえばリスト ``mylist`` が要素 1,2,3,4 を持っていて、object_1, object_2, object_3, object_4 に保存されているオブジェクトのユニークIDになっています。一方でweight_1, weight_2, weight_3, weight_4は重みを保存していて、その重みを使ってIDをソートしたいとします。この場合は次のコマンドを使います。

   .. **Sorting by external keys**

   **外部キーでソートする**

   .. code-block:: none

      SORT mylist BY weight_*

   .. the BY option takes a pattern (weight_* in our example) that is used in order to generate the key names of the weights used for sorting. Weight key names are obtained substituting the first occurrence of * with the actual value of the elements on the list (1,2,3,4 in our example).

   ``BY`` オプションは重みを保存しているキー名を生成するためにパターンを受け付けることができます（今回はweight_*です）重みのキー名は最初に現れるアスタリスクをリスト内の実際に値に置き換えることで得られます。（この例では1,2,3,4です）

   .. Our previous example will return just the sorted IDs. Often it is needed to get the actual objects sorted (object_1, ..., object_4 in the example). We can do it with the following command:

   前の例ではソートされたIDを返すだけでした。よく実際のオブジェクト（たとえばobject_1, ..., object4）をソートする必要があります。この場合は次のコマンドで出来ます。

   .. code-block:: none

      SORT mylist BY weight_* GET object_*

   .. **Retrieving external keys**

   **外部キーを取得する**

   .. Note that GET can be used multiple times in order to get more keys for every element of the original List, Set or Sorted Set sorted.

   元々のリスト、セット、ソート済みセットからさらにキーを取得するために ``GET`` オプションを複数回使うことが出来ます。

   .. Since Redis >= 1.1 it's possible to also GET the list elements itself using the special # pattern:

   Redis 1.1からリスト要素自身を ``#`` を使うことで取得できるようになりました。

   .. code-block:: none

      SORT mylist BY weight_* GET object_* GET #

   .. **Storing the result of a SORT operation**

   **SORTの結果を保存する**

   .. By default SORT returns the sorted elements as its return value. Using the STORE option instead to return the elements SORT will store this elements as a Redis List in the specified key. An example:

   デフォルトでは :com:`SORT` は返り値としてソートされた要素を返します。 :com:`STORE` オプションを使うことで要素を返す代わりに、 :com:`SORT` はこの要素をRedisリスト型として指定したキーの保存します。このような形です:

   .. code-block:: none

      SORT mylist BY weight_* STORE resultkey

   .. An interesting pattern using SORT ... STORE consists in associating an EXPIRE timeout to the resulting key so that in applications where the result of a sort operation can be cached for some time other clients will use the cached list instead to call SORT for every request. When the key will timeout an updated version of the cache can be created using SORT ... STORE again.

   ``SORT ... STORE`` を用いた興味深いパターンとして、 :com:`EXPIRE` のタイムアウトを結果のキーに関連付けて使う方法があります。こうすることでしばらくの間ソートの結果がキャッシュされたアプリケーション内でクライアントはリクエストごとに ``SORT`` を発行する代わりにキャッシュされたリストを参照することができます。キーがタイムアウトした場合は再度 ``SORT ... STORE`` を用いることで更新されたソート結果を使うことが出来ます。

   .. Note that implementing this pattern it is important to avoid that multiple clients will try to rebuild the cached version of the cache at the same time, so some form of locking should be implemented (for instance using SETNX).

   このパターンを実装するときには複数のクライアントがソート結果のキャッシュを同時に作成しないように気をつけなければいけません。したがって何らかのロックを使わなければいけないでしょう。（たとえば :com:`SETNX` を使うなど）

   .. **Not Sorting at all**

   **全くソートしない**

   .. code-block::

      SORT mylist BY nosort

   .. also the BY option can take a "nosort" specifier. This is useful if you want to retrieve a external key (using GET, read below) but you don't want the sorting overhead.

   ``BY`` オプションは "nosort" 識別子を取ることもできます。これは外部キーを取得したいけれど、ソートのオーバーヘッドは避けたい時に便利です。

   .. **SORT and Hashes: BY and GET by hash field**

   **ソートとハッシュ：ハッシュフィールドによるBYとGET**

   .. It's possible to use BY and GET options against Hash fields using the following syntax

   ``BY`` と ``GET`` オプションをハッシュフィールドに対して使うことも可能です。以下はその例です:

   .. code-block:: none

      SORT mylist BY weight_*->fieldname
      SORT mylist GET object_*->fieldname


   .. The two chars string -> is used in order to signal the name of the Hash field. The key is substituted as documented above with sort BY and GET against normal keys, and the Hash stored at the resulting key is accessed in order to retrieve the specified field.

   2文字の文字列 ``->`` はハッシュフィールドを指し示すのに使います。キーが ``BY`` と ``GET`` によって前述のとおりに通常のキーに置き換えられて、特定のフィールドを取得するためにキーが指定されているハッシュがアクセスされます。

   .. note::

      いい翻訳が難しい

   .. Return value

   **返り値**

     Multi bulk replyが返ります。具体的にはソートされたリストです。
