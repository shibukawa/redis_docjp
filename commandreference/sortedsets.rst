.. -*- coding: utf-8 -*-;

.. Redis Sorted Set Type

=========================
 Redisソート済みセット型
=========================

.. Redis Sorted Sets are, similarly to Sets, collections of Redis Strings. The difference is that every member of a Sorted Set hash an associated score that is used in order to take this member in order.

Redisソート済みセット型はRedisセット型とよく似ていて、Redis文字列型の集合となっています。違いはソート済みセットのすべてのメンバはスコアに関連したハッシュ値を持っています。元となっているスコアを用いてメンバを順番に並べます。

.. The ZADD command is used to add a new member to a Sorted Set, specifying the score of the element. Calling ZADD against a member already present in the sorted set but using a different score will update the score for the element, moving it to the right position in order to preserve ordering.

Redisソート済みセットに新しいメンバを追加するには要素のスコアを指定して :cmd:`ZADD` コマンドを用います。すでにソート済みセット内に存在するメンバに対して異なるスコアを用いて :cmd:`ZADD` を呼ぶと、順番が正しくなるようにその要素を正しい場所に移動させます。

.. It's possible to get ranges of elements from Sorted Sets in a very similar way to what happens with Lists and the LRANGE command using the Sorted Sets ZRANGE command.

Redisソート済みセットからある範囲の要素を取得することが可能です。これはRedisリストの :cmd:`LRANGE` と同様に :cmd:`ZRANGE` コマンドを用います。

.. It's also possible to get or remove ranges of elements by score using the ZRANGEBYSCORE and ZREMRANGEBYSCORE commands.

またあるスコアの範囲で要素を取得または削除することも可能で、それには :cmd:`ZRANGEBYSCORE` や :cmd:`ZREMRANGEBYSCORE` コマンドを使います。

.. The max number of members in a sorted set is 2^32-1 (4294967295, more than 4 billion of members per set).

Redisソート済みセットの要素数の最大値は 2^32-1 （4294967295, 1つのセット辺り4億）です。


.. Note that while Sorted Sets are already ordered, it is still possible to use the SORT command against sorted sets to get the elements in a different order.

Redisソート済みセットはすでに順番に並んでいますが、異なる並び順を得るために :cmd:`SORT` コマンドが使えるということを覚えておいてください。

.. Implementation details

実装の詳細
==========

.. Redis Sets are implemented using a dual-ported data structure containing a skip list and an hash table. When an element is added a map between the element and the score is added to the hash table (so that given the element we get the score in O(1)), and a map between the score and the element is added in the skip list so that elements are taken in order.

Redisセット型はスキップリストとハッシュ表の2つのデータ構造を用いて実装されています。要素が追加されたときには要素とスコアの間のマッピングがハッシュ表に追加されます。（これによって要素を用いてスコアを取得する操作がO(1)で行われます）そしてスコアと要素の間のマッピングはスキップリストに追加され順番に並べられます。

.. Redis uses a special skip list implementation that is doubly linked so that it's possible to traverse the sorted set from tail to head if needed (Check the ZREVRANGE command).

Redisは双方向リストを使っています。特別なスキップリストの実装をしています。理由は、逆順に捜査出来るようにするためです。（ :cmd:`ZREVRANGE` コマンドを確認してください）

.. When ZADD is used in order to update the score of an element, Redis retrieve the score of the element using the hash table, so that it's fast to access the element inside the skip list (that's indexed by score) in order to update the position.

要素のスコアを更新するために :cmd:`ZADD` が使われた場合、Redisは要素のスコアをハッシュ表を用いて取得します。これによって位置を更新するために、スコアによってインデックス付けされたスキップリスト内の要素に高速アクセスすることが可能になっています。

.. Like it happens for Sets the hash table resizing is a blocking operation performed synchronously so working with huge sorted sets (consisting of many millions of elements) care should be taken when mass-inserting a very big amount of elements in a Set while other clients are querying Redis at high speed.

Redisセット型で起きていたのと同様、ハッシュ表のリサイズは同期的に行われるブロッキングな操作なので、（数百万要素を持っているような）巨大なソート済みセットを扱う場合は、他のクライアントがRedisに対して高速にクエリを投げているときに大量の要素を挿入するようなことはしないように気をつけるべきです。

.. It is possible that in the near future Redis will switch to skip lists even for the element => score map, so every Sorted Set will have two skip lists, one indexed by element and one indexed by score.

近いうちにRedisではスキップリストが要素からスコアを指すマップを持つものに切り替わでしょう。すべてのソート済みセットが2つのスキップリストを持つことになります。1つは要素でインデックス付けされたもの、もう一方はスコアでインデックス付けされたものです。
