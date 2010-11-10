.. -*- coding: utf-8 -*-;

.. Redis Sorted Set Type

.. index::
   pair: データ型; ソート済みセット型

.. _sortedsets:

==================
ソート済みセット型
==================

.. Redis Sorted Sets are, similarly to Sets, collections of Redis Strings. The difference is that every member of a Sorted Set hash an associated score that is used in order to take this member in order.

Redisソート済みセット型はRedisセット型とよく似ていて、Redis文字列型の集合となっています。違いはソート済みセットのすべてのメンバはスコアに関連したハッシュ値を持っています。元となっているスコアを用いてメンバを順番に並べます。

.. The ZADD command is used to add a new member to a Sorted Set, specifying the score of the element. Calling ZADD against a member already present in the sorted set but using a different score will update the score for the element, moving it to the right position in order to preserve ordering.

Redisソート済みセットに新しいメンバを追加するには要素のスコアを指定して :com:`ZADD` コマンドを用います。すでにソート済みセット内に存在するメンバに対して異なるスコアを用いて :com:`ZADD` を呼ぶと、順番が正しくなるようにその要素を正しい場所に移動させます。

.. It's possible to get ranges of elements from Sorted Sets in a very similar way to what happens with Lists and the LRANGE command using the Sorted Sets ZRANGE command.

Redisソート済みセットからある範囲の要素を取得することが可能です。これはRedisリストの :com:`LRANGE` と同様に :com:`ZRANGE` コマンドを用います。

.. It's also possible to get or remove ranges of elements by score using the ZRANGEBYSCORE and ZREMRANGEBYSCORE commands.

またあるスコアの範囲で要素を取得または削除することも可能で、それには :com:`ZRANGEBYSCORE` や :com:`ZREMRANGEBYSCORE` コマンドを使います。

.. The max number of members in a sorted set is 2^32-1 (4294967295, more than 4 billion of members per set).

Redisソート済みセットの要素数の最大値は 2^32-1 （4294967295, 1つのセット辺り4億）です。


.. Note that while Sorted Sets are already ordered, it is still possible to use the SORT command against sorted sets to get the elements in a different order.

Redisソート済みセットはすでに順番に並んでいますが、異なる並び順を得るために :com:`SORT` コマンドが使えるということを覚えておいてください。

.. Implementation details

実装の詳細
==========

.. Redis Sets are implemented using a dual-ported data structure containing a skip list and an hash table. When an element is added a map between the element and the score is added to the hash table (so that given the element we get the score in O(1)), and a map between the score and the element is added in the skip list so that elements are taken in order.

Redisセット型はスキップリストとハッシュ表の2つのデータ構造を用いて実装されています。要素が追加されたときには要素とスコアの間のマッピングがハッシュ表に追加されます。（これによって要素を用いてスコアを取得する操作がO(1)で行われます）そしてスコアと要素の間のマッピングはスキップリストに追加され順番に並べられます。

.. Redis uses a special skip list implementation that is doubly linked so that it's possible to traverse the sorted set from tail to head if needed (Check the ZREVRANGE command).

Redisは双方向リストを使っています。特別なスキップリストの実装をしています。理由は、逆順に捜査出来るようにするためです。（ :com:`ZREVRANGE` コマンドを確認してください）

.. When ZADD is used in order to update the score of an element, Redis retrieve the score of the element using the hash table, so that it's fast to access the element inside the skip list (that's indexed by score) in order to update the position.

要素のスコアを更新するために :com:`ZADD` が使われた場合、Redisは要素のスコアをハッシュ表を用いて取得します。これによって位置を更新するために、スコアによってインデックス付けされたスキップリスト内の要素に高速アクセスすることが可能になっています。

.. Like it happens for Sets the hash table resizing is a blocking operation performed synchronously so working with huge sorted sets (consisting of many millions of elements) care should be taken when mass-inserting a very big amount of elements in a Set while other clients are querying Redis at high speed.

Redisセット型で起きていたのと同様、ハッシュ表のリサイズは同期的に行われるブロッキングな操作なので、（数百万要素を持っているような）巨大なソート済みセットを扱う場合は、他のクライアントがRedisに対して高速にクエリを投げているときに大量の要素を挿入するようなことはしないように気をつけるべきです。

.. It is possible that in the near future Redis will switch to skip lists even for the element => score map, so every Sorted Set will have two skip lists, one indexed by element and one indexed by score.

近いうちにRedisではスキップリストが要素からスコアを指すマップを持つものに切り替わでしょう。すべてのソート済みセットが2つのスキップリストを持つことになります。1つは要素でインデックス付けされたもの、もう一方はスコアでインデックス付けされたものです。


ソート済みセット型のコマンド
============================


.. command:: ZADD key score member

   .. versionadded:: 1.1

   計算時間: O(log(N)) with N being the number of elements in the sorted set

Add the specified member having the specifeid score to the sorted set stored at key. If member is already a member of the sorted set the score is updated, and the element reinserted in the right position to ensure sorting. If key does not exist a new sorted set with the specified member as sole member is crated. If the key exists but does not hold a sorted set value an error is returned.
The score value can be the string representation of a double precision floating point number.
For an introduction to sorted sets check the Introduction to Redis data types page.

   .. Return value

   **返り値**

     Integer replyが返ります。具体的には下記::

       1 if the new element was added
       0 if the element was already a member of the sorted set and the score was updated


.. command:: ZREM key member 

   .. versionadded:: 1.1

   計算時間: O(log(N)) with N being the number of elements in the sorted set

   Remove the specified member from the sorted set value stored at key. If member was not a member of the set no operation is performed. If key does not not hold a set value an error is returned.

   .. Return value

   **返り値**

     Integer replyが返ります。具体的には下記::

       1 if the new element was removed
       0 if the new element was not a member of the set


.. command:: ZINCRBY key increment member 
   
   .. versionadded:: 1.1

   計算時間: O(log(N)) with N being the number of elements in the sorted set

   If member already exists in the sorted set adds the increment to its score and updates the position of the element in the sorted set accordingly. If member does not already exist in the sorted set it is added with increment as score (that is, like if the previous score was virtually zero). If key does not exist a new sorted set with the specified member as sole member is crated. If the key exists but does not hold a sorted set value an error is returned.

   The score value can be the string representation of a double precision floating point number. It's possible to provide a negative value to perform a decrement.

   For an introduction to sorted sets check the Introduction to Redis data types page.

   .. Return value

   **帰り値**

     Bulk replyが返ります::

       The new score (a double precision floating point number) represented as string.

.. command:: ZRANK key member

   .. versionadded:: 1.3.4.

.. command:: ZREVRANK key member

   .. versionadded:: 1.3.4

   計算時間: O(log(N))

   ZRANK returns the rank of the member in the sorted set, with scores ordered from low to high. ZREVRANK returns the rank with scores ordered from high to low. When the given member does not exist in the sorted set, the special value 'nil' is returned. The returned rank (or index) of the member is 0-based for both commands.

   .. Return value

   **帰り値**

     Integer reply または nil bulk replyが返ります。具体的には::

       the rank of the element as an integer reply if the element exists.
       A nil bulk reply if there is no such element.


.. command:: ZRANGE key start end [WITHSCORES]

   .. versionadded:: 1.1

.. command:: ZREVRANGE key start end [WITHSCORES]

   .. versionadded:: 1.1

   計算時間: O(log(N))+O(M) (with N being the number of elements in the sorted set and M the number of elements requested)

   Return the specified elements of the sorted set at the specified key. The elements are considered sorted from the lowerest to the highest score when using ZRANGE, and in the reverse order when using ZREVRANGE. Start and end are zero-based indexes. 0 is the first element of the sorted set (the one with the lowerest score when using ZRANGE), 1 the next element by score and so on.

   start and end can also be negative numbers indicating offsets from the end of the sorted set. For example -1 is the last element of the sorted set, -2 the penultimate element and so on.
Indexes out of range will not produce an error: if start is over the end of the sorted set, or start > end, an empty list is returned. If end is over the end of the sorted set Redis will threat it just like the last element of the sorted set.

   It's possible to pass the WITHSCORES option to the command in order to return not only the values but also the scores of the elements. Redis will return the data as a single list composed of value1,score1,value2,score2,...,valueN,scoreN but client libraries are free to return a more appropriate data type (what we think is that the best return type for this command is a Array of two-elements Array / Tuple in order to preserve sorting).

   .. Return value

   **帰り値**

     Multi bulk replyが返ります。具体的には指定された範囲の要素のリストが返ります。


.. command:: ZRANGEBYSCORE key min max [LIMIT offset count]

   .. versionadded 1.1

.. command:: ZRANGEBYSCORE key min max [LIMIT offset count] [WITHSCORES]

   .. versionadded 1.3.4

.. command:: ZCOUNT key min max

   計算時間: O(log(N))+O(M) with N being the number of elements in the sorted set and M the number of elements returned by the command, so if M is constant (for instance you always ask for the first ten elements with LIMIT) you can consider it O(log(N))

   Return the all the elements in the sorted set at key with a score between min and max (including elements with score equal to min or max).

   The elements having the same score are returned sorted lexicographically as ASCII strings (this follows from a property of Redis sorted sets and does not involve further computation).
Using the optional LIMIT it's possible to get only a range of the matching elements in an SQL-alike way. Note that if offset is large the commands needs to traverse the list for offset elements and this adds up to the O(M) figure.

   The ZCOUNT command is similar to ZRANGEBYSCORE but instead of returning the actual elements in the specified interval, it just returns the number of matching elements.
Exclusive intervals and infinity

   min and max can be -inf and +inf, so that you are not required to know what's the greatest or smallest element in order to take, for instance, elements "up to a given value".

   Also while the interval is for default closed (inclusive) it's possible to specify open intervals prefixing the score with a "(" character, so for instance::

     ZRANGEBYSCORE zset (1.3 5

   Will return all the values with score > 1.3 and <= 5, while for instance::

     ZRANGEBYSCORE zset (5 (10

   Will return all the values with score > 5 and < 10 (5 and 10 excluded).

   .. Return value

   **帰り値**

     ZRANGEBYSCORE returns a Multi bulk reply specifically a list of elements in the specified score range.

     ZCOUNT returns a Integer reply specifically the number of elements matching the specified score range.

   .. Examples

   **例**

   .. code-block:: none

      redis> zadd zset 1 foo
      (integer) 1
      redis> zadd zset 2 bar
      (integer) 1
      redis> zadd zset 3 biz
      (integer) 1
      redis> zadd zset 4 foz
      (integer) 1
      redis> zrangebyscore zset -inf +inf
      1. "foo"
      2. "bar"
      3. "biz"
      4. "foz"
      redis> zcount zset 1 2
      (integer) 2
      redis> zrangebyscore zset 1 2
      1. "foo"
      2. "bar"
      redis> zrangebyscore zset (1 2
      1. "bar"
      redis> zrangebyscore zset (1 (2
      (empty list or set)


.. command:: ZCARD key 

   .. versionadded:: 1.1

   計算時間: O(1)

   Return the sorted set cardinality (number of elements). If the key does not exist 0 is returned, like for empty sorted sets.

   .. Return value

   **帰り値**

     Integer replyを返す。具体的には::

       the cardinality (number of elements) of the set as an integer.


.. command:: ZSCORE key element

   .. versionadded:: 1.1

   計算時間: O(1)

   Return the score of the specified element of the sorted set at key. If the specified element does not exist in the sorted set, or the key does not exist at all, a special 'nil' value is returned.

   .. Return value

   **帰り値**

     Bulk replyが返ります::

       the score (a double precision floating point number) represented as string.


.. command:: ZUNIONSTORE dstkey N k1 ... kN [WEIGHTS w1 ... wN] [AGGREGATE SUM|MIN|MAX]

   .. versionadded:: 1.3.12

.. command:: ZINTERSTORE dstkey N k1 ... kN [WEIGHTS w1 ... wN] [AGGREGATE SUM|MIN|MAX]

   .. versionadded:: 1.3.12

   計算時間: O(N) + O(M log(M)) with N being the sum of the sizes of the input sorted sets, and M being the number of elements in the resulting sorted set

   Creates a union or intersection of N sorted sets given by keys k1 through kN, and stores it at dstkey. It is mandatory to provide the number of input keys N, before passing the input keys and the other (optional) arguments.

   As the terms imply, the ZINTERSTORE command requires an element to be present in each of the given inputs to be inserted in the result. The ZUNIONSTORE command inserts all elements across all inputs.

   Using the WEIGHTS option, it is possible to add weight to each input sorted set. This means that the score of each element in the sorted set is first multiplied by this weight before being passed to the aggregation. When this option is not given, all weights default to 1.

   With the AGGREGATE option, it's possible to specify how the results of the union or intersection are aggregated. This option defaults to SUM, where the score of an element is summed across the inputs where it exists. When this option is set to be either MIN or MAX, the resulting set will contain the minimum or maximum score of an element across the inputs where it exists.

   .. Return value

   **帰り値**

     Integer replyが返ります。具体的にはキー ``dstkey`` に対応するソート済みセット内の要素数です。


