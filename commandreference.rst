.. -*- coding: utf-8 -*-;

.. Redis Command Reference¶

===========================
 Redisコマンドリファレンス
===========================

.. Every command name links to a specific wiki page describing the behavior of the command.

すべてのコマンド名にあるリンクは各コマンドごとの紹介ページとなっています。

.. Categorized Command List

カテゴリ別コマンドリスト
========================

.. Connection handling

接続処理
--------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - QUIT
     - --
     - 接続を閉じる
   * - AUTH
     - password
     - 有効な場合、簡単なパスワード認証が行われます

.. Commands operating on all value types

全データ型対応の操作
--------------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - EXISTS
     - key
     - キー ``key`` が存在するか確認します
   * - DEL
     - key
     - キー ``key`` を削除します
   * - TYPE
     - key
     - あるキー ``key`` で格納されている値の型を返す
   * - KEYS
     - pattern
     - 与えられたパターン ``pattern`` にマッチするすべてのキーを返す
   * - RANDOMKEY
     - --
     - return a random key from the key space
   * - RENAME
     - oldname newname
     - 古いキー ``oldname`` を新しいキー ``newname`` にリネームする。もし新しいキーがすでに存在する場合、上書きする。
   * - RENAMENX
     - oldname newname
     - 古いキー ``oldname`` を新しいキー ``newname`` にリネームする。新しいキーが存在しない場合のみ有効。
   * - DBSIZE
     - --
     - その時点でのデータベース内におけるキーの数を返す
   * - EXPIRE
     - key seconds
     - キー ``key`` の有効期限を ``seconds`` 秒に設定する
   * - PERSIST
     - key
     - キー ``key`` の有効期限を破棄する
   * - TTL
     - key
     - キー ``key`` の存命時間を取得する
   * - SELECT
     - index
     - 与えられたインデックス ``index`` のデータベースを選択する
   * - MOVE
     - key dbindex
     - あるキー ``key`` を現在のデータベースから ``dbindex`` のDBへ移す
   * - FLUSHDB
     - --
     - 現在選択されているデータベースのすべてのキーを削除する
   * - FLUSHALL
     - --
     - すべてのデータベースからすべてのキーを削除する

.. Commands operating on string values

文字列型の操作
--------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - SET	
     - key value
     - 文字列 ``value`` にキー ``key`` をセットする
   * - GET
     - key
     - あるキー ``key`` に対応する文字列を返す
   * - GETSET
     - key value
     - あるキー ``key`` に文字列 ``value`` をセットして、そのキーに紐づいていた古い文字列を返す
   * - MGET
     - key1 key2 ... keyN
     - Multi-get, 与えた複数のキー ``keyN`` に対応する文字列を返す
   * - SETNX
     - key value
     - そのキー ``key`` が存在しない場合、文字列 ``value`` にキーをセットする
   * - SETEX
     - key time value
     - Set+Expireの合わせ技
   * - MSET
     - key1 value1 key2 value2 ... keyN valueN
     - 単一アトミック操作で複数のキー ``keyN`` と文字列 ``valueN`` のペアをセットする
   * - MSETNX
     - key1 value1 key2 value2 ... keyN valueN
     - 単一アトミック操作で複数のキー ``keyN`` と文字烈 ``valueN`` のペアをセットする。ただし与えられたキーのすべてが存在しない場合のみ有効。
   * - INCR
     - key
     - キー ``key`` に対応する整数値をインクリメントする
   * - INCRBY
     - key integer
     - キー ``key`` に対応する整数値を ``integer`` だけインクリメントする
   * - DECR
     - key
     - キー ``key`` に対応する整数値ををデクリメントする
   * - DECRBY
     - key integer
     - キー ``key`` に対応する整数値を ``integer`` だけデクリメントする
   * - APPEND
     - key value
     - キー ``key`` に対応する文字列に ``value`` の文字列を追加する
   * - SUBSTR
     - key start end
     - キー ``key`` に対応する文字列の ``start`` から ``end`` の部分文字列を返す
   
.. Commands operating on lists

リストの操作
------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - RPUSH
     - key value
     - キー ``key`` に対応するリストの末尾に要素 ``value`` を追加する
   * - LPUSH
     - key value
     - キー ``key`` に対応するリストの先頭に要素 ``value`` を追加する
   * - LLEN
     - key
     - キー ``key`` に対応するリストの長さを返す
   * - LRANGE
     - key start end
     - キー ``key`` に対応するリストから ``start`` 番目から ``end`` 番目までの部分リストを返す
   * - LTRIM
     - key start end
     - キー ``key`` に対応するリストを ``start`` 番目から ``end`` 番目の部分リストに変更する
   * - LINDEX
     - key index
     - キー ``key`` に対応するリストの ``index`` 番目の要素を返す
   * - LSET
     - key index value
     - キー ``key`` に対応するリストの ``index`` 番目の要素を新しい値 ``value`` に変更する
   * - LREM
     - key count value
     - 最初の ``count`` 個だけ ``value`` にマッチする要素を ``key`` に対応するリストから削除する。 ``count`` が負数の場合は最後から ``count`` 個だけ削除する。
   * - LPOP
     - key
     - キー ``key`` に対応するリストの先頭の要素を返してリストから削除する
   * - RPOP
     - key
     - キー ``key`` に対応するリストの末尾の要素を返してリストから削除する
   * - BLPOP
     - key1 key2 ... keyN timeout
     - 複数のキー ``keyN`` に対応するリストを　``LPOP`` から ``timeout`` 秒ブロックする
   * - BRPOP
     - key1 key2 ... keyN timeout
     - 複数のキー ``keyN`` に対応するリストを　``POP`` から ``timeout`` 秒ブロックする
   * - RPOPLPUSH
     - srckey dstkey
     - キー ``srckey`` のリストの末尾の要素を返してそのリストから削除し、キー ``dstkey`` に対応するリストの先頭にその値を追加する。
   

.. Commands operating on sets

セットの操作
------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - SADD
     - key member
     - キー ``key`` に対応するセットにメンバ ``member`` を追加する
   * - SREM
     - key member
     - キー ``key`` に対応するセットからメンバ ``member`` を削除する
   * - SPOP
     - key
     - キー ``key`` に対応するセットからランダムに一つ選んだ要素を返し、セットから削除する
   * - SMOVE
     - srckey dstkey member
     - キー ``srckey`` に対応するセットからキー ``dstkey`` に対応するセットにメンバ ``member`` を移動する
   * - SCARD
     - key
     - キー ``key`` に対応するセットの要素数（濃度）を返します
   * - SISMEMBER
     - key member
     - キー ``key`` に対応するセットの中にメンバ ``member`` があるか確認します
   * - SINTER
     - key1 key2 ... keyN
     - 複数のキー ``keyN`` に対応するセットの共通セットを返します
   * - SINTERSTORE
     - dstkey key1 key2 ... keyN
     - Compute the intersection between the Sets stored at key1, key2, ..., keyN, and store the resulting Set at dstkey
   * - SUNION
     - key1 key2 ... keyN
     - Return the union between the Sets stored at key1, key2, ..., keyN
   * - SUNIONSTORE
     - dstkey key1 key2 ... keyN
     - Compute the union between the Sets stored at key1, key2, ..., keyN, and store the resulting Set at dstkey
   * - SDIFF
     - key1 key2 ... keyN
     - Return the difference between the Set stored at key1 and all the Sets key2, ..., keyN
   * - SDIFFSTORE
     - dstkey key1 key2 ... keyN
     - Compute the difference between the Set key1 and all the Sets key2, ..., keyN, and store the resulting Set at dstkey
   * - SMEMBERS
     - key
     - Return all the members of the Set value at key
   * - SRANDMEMBER
     - key
     - Return a random member of the Set value at key
   

.. Commands operating on sorted zsets (sorted sets)

ソート済みセットの操作
----------------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - ZADD
     - key score member
     - Add the specified member to the Sorted Set value at key or update the score if it already exist
   * - ZREM
     - key member
     - Remove the specified member from the Sorted Set value at key
   * - ZINCRBY
     - key increment member
     - If the member already exists increment its score by increment, otherwise add the member setting increment as score
   * - ZRANK
     - key member
     - Return the rank (or index) or member in the sorted set at key, with scores being ordered from low to high
   * - ZREVRANK
     - key member
     - Return the rank (or index) or member in the sorted set at key, with scores being ordered from high to low
   * - ZRANGE
     - key start end
     - Return a range of elements from the sorted set at key
   * - ZREVRANGE
     - key start end
     - Return a range of elements from the sorted set at key, exactly like ZRANGE, but the sorted set is ordered in traversed in reverse order, from the greatest to the smallest score
   * - ZRANGEBYSCORE
     - key min max
     - Return all the elements with score >= min and score <= max (a range query) from the sorted set
   * - ZCOUNT
     - key min max
     - Return the number of elements with score >= min and score <= max in the sorted set
   * - ZCARD
     - key
     - Return the cardinality (number of elements) of the sorted set at key
   * - ZSCORE
     - key element
     - Return the score associated with the specified element of the sorted set at key
   * - ZREMRANGEBYRANK
     - key min max
     - Remove all the elements with rank >= min and rank <= max from the sorted set
   * - ZREMRANGEBYSCORE
     - key min max
     - Remove all the elements with score >= min and score <= max from the sorted set
   * - ZUNIONSTORE / ZINTERSTORE
     - dstkey N key1 ... keyN WEIGHTS w1 ... wN AGGREGATE SUM|MIN|MAX
     - Perform a union or intersection over a number of sorted sets with optional weight and aggregate
   

.. Commands operating on hashes

ハッシュの操作
--------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - HSET
     - key field value
     - Set the hash field to the specified value. Creates the hash if needed.
   * - HGET
     - key field
     - Retrieve the value of the specified hash field.
   * - HMGET
     - key field1 ... fieldN
     - Get the hash values associated to the specified fields.
   * - HMSET
     - key field1 value1 ... fieldN valueN
     - Set the hash fields to their respective values.
   * - HINCRBY
     - key field integer
     - Increment the integer value of the hash at key on field with integer.
   * - HEXISTS
     - key field
     - Test for existence of a specified field in a hash
   * - HDEL
     - key field
     - Remove the specified field from a hash
   * - HLEN
     - key
     - Return the number of items in a hash.
   * - HKEYS
     - key
     - Return all the fields in a hash.
   * - HVALS
     - key
     - Return all the values in a hash.
   * - HGETALL
     - key
     - Return all the fields and associated values in a hash.
   

.. Sorting

ソート
------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - SORT
     - key BY pattern LIMIT start end GET pattern ASC|DESC ALPHA
     - Sort a Set or a List accordingly to the specified parameters
   

.. Transactions

トランザクション
----------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - MULTI/EXEC/DISCARD/WATCH/UNWATCH
     - --
     - Redis atomic transactions
   

.. Publish/Subscribe

パブリッシュ／サブスクライブ
----------------------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - SUBSCRIBE/UNSUBSCRIBE/PUBLISH
     - --
     - Redis Public/Subscribe messaging paradigm implementation
   
.. Persistence control commands

永続化処理コマンド
------------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - SAVE
     - --
     - Synchronously save the DB on disk
   * - BGSAVE
     - --
     - Asynchronously save the DB on disk
   * - LASTSAVE
     - --
     - Return the UNIX time stamp of the last successfully saving of the dataset on disk
   * - SHUTDOWN
     - --
     - Synchronously save the DB on disk, then shutdown the server
   * - BGREWRITEAOF
     - --
     - Rewrite the append only file in background when it gets too big
   

.. Remote server control commands

リモートサーバ制御コマンド
--------------------------

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - INFO
     - --
     - Provide information and statistics about the server
   * - MONITOR
     - --
     - Dump all the received requests in real time
   * - SLAVEOF
     - --
     - Change the replication settings
   * - CONFIG
     - --
     - Configure a Redis server at runtime
