.. -*- coding: utf-8 -*-;

.. Redis Command Reference¶

===========================
 Redisコマンドリファレンス
===========================

.. Every command name links to a specific wiki page describing the behavior of the command.

すべてのコマンド名にあるリンクは各コマンドごとの紹介ページとなっています。

.. toctree::
   :hidden:

   connection

.. Categorized Command List

.. カテゴリ別コマンドリスト
.. ========================

.. Connection handling

接続処理
========

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`QUIT`
     - --
     - 接続を閉じる
   * - :com:`AUTH`
     - password
     - 有効な場合、簡単なパスワード認証が行われます

.. Commands operating on all value types

全データ型対応の操作
====================

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`EXISTS`
     - key
     - キー ``key`` が存在するか確認します
   * - :com:`DEL`
     - key
     - キー ``key`` を削除します
   * - :com:`TYPE`
     - key
     - あるキー ``key`` で格納されている値の型を返す
   * - :com:`KEYS`
     - pattern
     - 与えられたパターン ``pattern`` にマッチするすべてのキーを返す
   * - :com:`RANDOMKEY`
     - --
     - return a random key from the key space
   * - :com:`RENAME`
     - oldname newname
     - 古いキー ``oldname`` を新しいキー ``newname`` にリネームする。もし新しいキーがすでに存在する場合、上書きする。
   * - :com:`RENAMENX`
     - oldname newname
     - 古いキー ``oldname`` を新しいキー ``newname`` にリネームする。新しいキーが存在しない場合のみ有効。
   * - :com:`DBSIZE`
     - --
     - その時点でのデータベース内におけるキーの数を返す
   * - :com:`EXPIRE`
     - key seconds
     - キー ``key`` の有効期限を ``seconds`` 秒に設定する
   * - :com:`PERSIST`
     - key
     - キー ``key`` の有効期限を破棄する
   * - :com:`TTL`
     - key
     - キー ``key`` の存命時間を取得する
   * - :com:`SELECT`
     - index
     - 与えられたインデックス ``index`` のデータベースを選択する
   * - :com:`MOVE`
     - key dbindex
     - あるキー ``key`` を現在のデータベースから ``dbindex`` のDBへ移す
   * - :com:`FLUSHDB`
     - --
     - 現在選択されているデータベースのすべてのキーを削除する
   * - :com:`FLUSHALL`
     - --
     - すべてのデータベースからすべてのキーを削除する

.. Commands operating on string values

文字列型の操作
==============

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`SET`
     - key value
     - 文字列 ``value`` にキー ``key`` をセットする
   * - :com:`GET`
     - key
     - あるキー ``key`` に対応する文字列を返す
   * - :com:`GETSET`
     - key value
     - あるキー ``key`` に文字列 ``value`` をセットして、そのキーに紐づいていた古い文字列を返す
   * - :com:`MGET`
     - key1 key2 ... keyN
     - Multi-get, 与えた複数のキー ``keyN`` に対応する文字列を返す
   * - :com:`SETNX`
     - key value
     - そのキー ``key`` が存在しない場合、文字列 ``value`` にキーをセットする
   * - :com:`SETEX`
     - key time value
     - Set+Expireの合わせ技
   * - :com:`MSET`
     - key1 value1 key2 value2 ... keyN valueN
     - 単一アトミック操作で複数のキー ``keyN`` と文字列 ``valueN`` のペアをセットする
   * - :com:`MSETNX`
     - key1 value1 key2 value2 ... keyN valueN
     - 単一アトミック操作で複数のキー ``keyN`` と文字烈 ``valueN`` のペアをセットする。ただし与えられたキーのすべてが存在しない場合のみ有効。
   * - :com:`INCR`
     - key
     - キー ``key`` に対応する整数値をインクリメントする
   * - :com:`INCRBY`
     - key integer
     - キー ``key`` に対応する整数値を ``integer`` だけインクリメントする
   * - :com:`DECR`
     - key
     - キー ``key`` に対応する整数値ををデクリメントする
   * - :com:`DECRBY`
     - key integer
     - キー ``key`` に対応する整数値を ``integer`` だけデクリメントする
   * - :com:`APPEND`
     - key value
     - キー ``key`` に対応する文字列に ``value`` の文字列を追加する
   * - :com:`SUBSTR`
     - key start end
     - キー ``key`` に対応する文字列の ``start`` から ``end`` の部分文字列を返す
   
.. Commands operating on lists

リストの操作
============

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`RPUSH`
     - key value
     - キー ``key`` に対応するリストの末尾に要素 ``value`` を追加する
   * - :com:`LPUSH`
     - key value
     - キー ``key`` に対応するリストの先頭に要素 ``value`` を追加する
   * - :com:`LLEN`
     - key
     - キー ``key`` に対応するリストの長さを返す
   * - :com:`LRANGE`
     - key start end
     - キー ``key`` に対応するリストから ``start`` 番目から ``end`` 番目までの部分リストを返す
   * - :com:`LTRIM`
     - key start end
     - キー ``key`` に対応するリストを ``start`` 番目から ``end`` 番目の部分リストに変更する
   * - :com:`LINDEX`
     - key index
     - キー ``key`` に対応するリストの ``index`` 番目の要素を返す
   * - :com:`LSET`
     - key index value
     - キー ``key`` に対応するリストの ``index`` 番目の要素を新しい値 ``value`` に変更する
   * - :com:`LREM`
     - key count value
     - 最初の ``count`` 個だけ ``value`` にマッチする要素を ``key`` に対応するリストから削除する。 ``count`` が負数の場合は最後から ``count`` 個だけ削除する。
   * - :com:`LPOP`
     - key
     - キー ``key`` に対応するリストの先頭の要素を返してリストから削除する
   * - :com:`RPOP`
     - key
     - キー ``key`` に対応するリストの末尾の要素を返してリストから削除する
   * - :com:`BLPOP`
     - key1 key2 ... keyN timeout
     - 複数のキー ``keyN`` に対応するリストを　``LPOP`` から ``timeout`` 秒ブロックする
   * - :com:`BRPOP`
     - key1 key2 ... keyN timeout
     - 複数のキー ``keyN`` に対応するリストを　``POP`` から ``timeout`` 秒ブロックする
   * - :com:`RPOPLPUSH`
     - srckey dstkey
     - キー ``srckey`` のリストの末尾の要素を返してそのリストから削除し、キー ``dstkey`` に対応するリストの先頭にその値を追加する。
   

.. Commands operating on sets

セットの操作
============

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`SADD`
     - key member
     - キー ``key`` に対応するセットにメンバ ``member`` を追加する
   * - :com:`SREM`
     - key member
     - キー ``key`` に対応するセットからメンバ ``member`` を削除する
   * - :com:`SPOP`
     - key
     - キー ``key`` に対応するセットからランダムに一つ選んだ要素を返し、セットから削除する
   * - :com:`SMOVE`
     - srckey dstkey member
     - キー ``srckey`` に対応するセットからキー ``dstkey`` に対応するセットにメンバ ``member`` を移動する
   * - :com:`SCARD`
     - key
     - キー ``key`` に対応するセットの要素数（濃度）を返します
   * - :com:`SISMEMBER`
     - key member
     - キー ``key`` に対応するセットの中にメンバ ``member`` があるか確認します
   * - :com:`SINTER`
     - key1 key2 ... keyN
     - 複数のキー ``keyN`` に対応する複数のセットの共通セットを返します
   * - :com:`SINTERSTORE`
     - dstkey key1 key2 ... keyN
     - 複数のキー ``keyN`` に対応する複数のセットの共通セットを作成し、その結果をキー ``dstkey`` に紐付ける
   * - :com:`SUNION`
     - key1 key2 ... keyN
     - 複数のキー ``keyN`` に対応する複数のセットの結合を返す
   * - :com:`SUNIONSTORE`
     - dstkey key1 key2 ... keyN
     - 複数のキー ``keyN`` に対応する複数のセットの結合を作成し、その結果をキー ``dstkey`` に紐付ける
   * - :com:`SDIFF`
     - key1 key2 ... keyN
     - 複数のキー ``keyN`` に対応する複数のセットの差分を返す
   * - :com:`SDIFFSTORE`
     - dstkey key1 key2 ... keyN
     - 複数のキー ``kenN`` に対応する複数のセットの差分を作成し、その結果をキー ``dstkey`` に紐付ける
   * - :com:`SMEMBERS`
     - key
     - キー ``key`` に対応するセットのすべてのメンバを返す
   * - :com:`SRANDMEMBER`
     - key
     - キー ``key`` に対応するセットの中からランダムに一つのメンバを選んで返す
   

.. Commands operating on sorted zsets (sorted sets)

ソート済みセットの操作
======================

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`ZADD`
     - key score member
     - キー ``key`` に対応するソート済みセットにメンバ ``member`` を追加する。 ``member`` が存在する場合はそのスコアを ``score`` に上書きする。
   * - :com:`ZREM`
     - key member
     - キー ``key`` に対応するソート済みセットからメンバ ``member`` を削除する
   * - :com:`ZINCRBY`
     - key increment member
     - もしキー ``key`` に対応するソート済みセットにメンバ ``member`` が存在する場合はスコアを値 ``increment`` だけインクリメントする。無ければ ``increment`` のスコアを持つメンバを追加する。
   * - :com:`ZRANK`
     - key member
     - キー ``key`` に対応するソート済みセット内にメンバ ``member`` が存在する場合はその順位（インデックス）を、存在しない場合は ``member`` を返す。メンバはスコアの昇順に並べるものとする。
   * - :com:`ZREVRANK`
     - key member
     - キー ``key`` に対応するソート済みセット内のメンバ ``member`` の順位（インデックス）を返す。メンバはスコアの降順に並べるものとする。
   * - :com:`ZRANGE`
     - key start end
     - キー ``key`` に対応するセットをメンバのスコアの昇順でソートした場合の、 ``start`` 番目から ``end`` 番目のメンバで作られたソート済みセットを返す。
   * - :com:`ZREVRANGE`
     - key start end
     - キー ``key`` に対応するセットをメンバのスコアの降順でソートした場合の、 ``start`` 番目から ``end`` 番目のメンバで作られたソート済みセットを返す。
   * - :com:`ZRANGEBYSCORE`
     - key min max
     - キー ``key`` に対応するソート済みセットの中からスコアが ``min`` 以上 ``max`` 以下の要素で作られたソート済みセットを返す
   * - :com:`ZCOUNT`
     - key min max
     - キー ``key`` に対応するソート済みセットの中でスコアが ``min`` 以上 ``max`` 以下の要素の数を返す
   * - :com:`ZCARD`
     - key
     - キー ``key`` に対応するソート済みセットのメンバ数（濃度）を返す
   * - :com:`ZSCORE`
     - key element
     - キー ``key`` に対応するソート済みセットの特定の要素のスコアを返す
   * - :com:`ZREMRANGEBYRANK`
     - key min max
     - キー ``key`` に対応するソート済みセットから ``min`` 以上 ``max`` 以下の順位のメンバをすべて削除する
   * - :com:`ZREMRANGEBYSCORE`
     - key min max
     - キー ``key`` に対応するソート済みセットから ``min`` 以上 ``max`` 以下のスコアを持つメンバをすべて削除する
   * - :com:`ZUNIONSTORE` / :com:`ZINTERSTORE`
     - dstkey N key1 ... keyN WEIGHTS w1 ... wN AGGREGATE SUM|MIN|MAX
     - 複数のキー ``keyN`` に対応する複数のソート済みセットの結合または共通セットを、重みとアグリゲーションに関するオプションを元に作成し、結果をキー ``dstkey`` に紐付ける
   

.. Commands operating on hashes

ハッシュ表の操作
================

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`HSET`
     - key field value
     - キー ``key`` に対応するハッシュ表にフィールド ``field`` に値 ``value`` のセットする。必要であれば作成する。
   * - :com:`HGET`
     - key field
     - キー ``key`` に対応するハッシュ表でフィールド ``field`` に紐づいている値を取得する
   * - :com:`HMGET`
     - key field1 ... fieldN
     - キー ``key`` に対応するハッシュ表から複数のフィールド ``fieldN`` に紐づいている複数のハッシュ値を取得する
   * - :com:`HMSET`
     - key field1 value1 ... fieldN valueN
     - キー ``key`` に対応するハッシュ表に複数のフィールド ``fieldN`` と値 ``valueN`` のペアをセットする
   * - :com:`HINCRBY`
     - key field integer
     - キー ``key`` に対応するハッシュ表のフィールド ``field`` に対応する値を ``integer`` だけインクリメントする
   * - :com:`HEXISTS`
     - key field
     - キー ``key`` に対応するハッシュ表にフィールド ``field`` が存在するか確認する
   * - :com:`HDEL`
     - key field
     - キー ``key`` に対応するハッシュ表からフィールド ``field`` を削除する
   * - :com:`HLEN`
     - key
     - キー ``key`` に対応するハッシュ表の要素数を返す
   * - :com:`HKEYS`
     - key
     - キー ``key`` に対応するハッシュ表のすべてのフィールドを返す
   * - :com:`HVALS`
     - key
     - キー ``key`` に対応するハッシュ表のすべての値を返す
   * - :com:`HGETALL`
     - key
     - キー ``key`` に対応するハッシュ表のすべてのフィールドと値のペアを返す
   

.. Sorting

ソート
======

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`SORT`
     - key BY pattern LIMIT start end GET pattern ASC|DESC ALPHA
     - セットまたはリストを与えられたパラメータに基づきソートする
   

.. Transactions

トランザクション
================

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`MULTI`/:com:`EXEC`/:com:`DISCARD`/:com:`WATCH`/:com:`UNWATCH`
     - --
     - Redisアトミックトランザクション
   

.. Publish/Subscribe

パブリッシュ／サブスクライブ
============================

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`SUBSCRIBE`/:com:`UNSUBSCRIBE`/:com:`PUBLISH`
     - --
     - Redisパブリッシュ／サブスクライブ メッセージング・パラダイムの実装
   
.. Persistence control commands

永続化処理コマンド
==================

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`SAVE`
     - --
     - 同期的にデータベースをディスクに保存する
   * - :com:`BGSAVE`
     - --
     - 非同期的にデータベースをディスクに保存する
   * - :com:`LASTSAVE`
     - --
     - 最後にデータベースをディスク上に保存したUNIX時間を返す
   * - :com:`SHUTDOWN`
     - --
     - 同期的にデータベースをディスク上に保存し、サーバを落とす
   * - :com:`BGREWRITEAOF`
     - --
     - 追記専用ファイルが大きくなりすぎたときはバックグラウンドで再書き込みする
   

.. Remote server control commands

リモートサーバ制御コマンド
==========================

.. list-table::
   :header-rows: 1

   * - **コマンド**
     - **パラメータ**
     - **内容**
   * - :com:`INFO`
     - --
     - サーバ情報やサーバの統計情報を提供する
   * - :com:`MONITOR`
     - --
     - 受信したリクエストをリアルタイムですべてダンプする
   * - :com:`SLAVEOF`
     - --
     - レプリケーションの設定を変更する
   * - :com:`CONFIG`
     - --
     - 起動中にRedisサーバの設定を行う
