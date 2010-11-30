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

   計算時間: O(log(N)) Nはソート済みセット内の要素数

   .. Add the specified member having the specifeid score to the sorted set stored at key. If member is already a member of the sorted set the score is updated, and the element reinserted in the right position to ensure sorting. If key does not exist a new sorted set with the specified member as sole member is crated. If the key exists but does not hold a sorted set value an error is returned.

   スコア ``score`` を持つメンバー ``member`` をキー ``key`` に対応するセット内に追加します。もしメンバーがすでに指定されたソート済みセット内に存在する場合は、スコアが更新され正しい場所に再挿入されます。もしキーが存在しない場合は指定されたメンバだけを含む新しいソート済みセットが作られます。もしキーが存在して対応する値がソート済みセットでない場合はエラーが返ります。

   .. The score value can be the string representation of a double precision floating point number.

   スコアの値は倍精度浮動小数を表す文字列です。

   .. For an introduction to sorted sets check the Introduction to Redis data types page.

   ソート済みセットに関する紹介はこのページの先頭を参照してください。

   .. Return value

   **返り値**

     Integer replyが返ります。具体的には下記::

       1 if the new element was added
       0 if the element was already a member of the sorted set and the score was updated


.. command:: ZREM key member 

   .. versionadded:: 1.1

   計算時間: O(log(N)) with N being the number of elements in the sorted set

   .. Remove the specified member from the sorted set value stored at key. If member was not a member of the set no operation is performed. If key does not not hold a set value an error is returned.

   指定されたメンバー ``member`` をキー ``key`` に対応するソート済みセットから削除します。もしメンバーが指定されたセット内に存在しない場合は何の処理も行われません。もしキーがソート済みセットを保持していない場合、エラーが返ります。

   .. Return value

   **返り値**

     Integer replyが返ります。具体的には下記::

       1 if the new element was removed
       0 if the new element was not a member of the set


.. command:: ZINCRBY key increment member 
   
   .. versionadded:: 1.1

   計算時間: O(log(N)) Nはソート済みセットないの要素数

   .. If member already exists in the sorted set adds the increment to its score and updates the position of the element in the sorted set accordingly. If member does not already exist in the sorted set it is added with increment as score (that is, like if the previous score was virtually zero). If key does not exist a new sorted set with the specified member as sole member is crated. If the key exists but does not hold a sorted set value an error is returned.

   メンバー ``member`` がすでにキー ``key`` に対応するソート済みセット内に存在する場合、そのスコアを ``increment`` 分だけインクリメントし、ソート済みセット内の正しい位置に更新する。もしメンバーが存在しない場合は ``increment`` のスコアを持ったメンバが追加されます。（つまり、仮想的にスコア0を持ったメンバを更新したことになります）もしキーが存在しない場合は指定したメンバーだけを持った新しいソート済みセットが作成されます。もしキーは存在するけれど、対応する値がソート済みセット出ない場合はエラーが返されます。

   .. The score value can be the string representation of a double precision floating point number. It's possible to provide a negative value to perform a decrement.

   スコアは倍精度浮動小数を表す文字列です。デクリメントをするために負の値指定することも可能です。

   .. For an introduction to sorted sets check the Introduction to Redis data types page.

   ソート済みセットの紹介はページ上部を確認して下さい。

   .. Return value

   **帰り値**

     Bulk replyが返ります::

       The new score (a double precision floating point number) represented as string.

.. command:: ZRANK key member

   .. versionadded:: 1.3.4.

.. command:: ZREVRANK key member

   .. versionadded:: 1.3.4

   計算時間: O(log(N))

   .. ZRANK returns the rank of the member in the sorted set, with scores ordered from low to high. ZREVRANK returns the rank with scores ordered from high to low. When the given member does not exist in the sorted set, the special value 'nil' is returned. The returned rank (or index) of the member is 0-based for both commands.

   :com:`ZRANK` はキー ``key`` に対応するソート済みセット内のメンバ ``member`` の昇順でのランクを返します。 :com:`ZREVRANK` は降順でのランクを返します。指定されたメンバがソート済みセットの中に存在しない場合は特別な値nilが返ります。どちらのコマンドにおいても返されるランク（インデックス）はゼロから始まる値です。

   .. Return value

   **帰り値**

     Integer reply または nil bulk replyが返ります。具体的には::

       the rank of the element as an integer reply if the element exists.
       A nil bulk reply if there is no such element.


.. command:: ZRANGE key start end [WITHSCORES]

   .. versionadded:: 1.1

.. command:: ZREVRANGE key start end [WITHSCORES]

   .. versionadded:: 1.1

   計算時間: O(log(N))+O(M) （Nはソート済みセット内の要素数でMは指定された要素数）

   .. Return the specified elements of the sorted set at the specified key. The elements are considered sorted from the lowerest to the highest score when using ZRANGE, and in the reverse order when using ZREVRANGE. Start and end are zero-based indexes. 0 is the first element of the sorted set (the one with the lowerest score when using ZRANGE), 1 the next element by score and so on.

   キー ``key`` に対応するソート済みセット内での ``start`` から ``end`` で指定された要素を返します。 :com:`ZRANGE` では要素は昇順に、 :com:`ZREVRANGE` では降順に並べられます。 ``start`` と ``end`` は0から始まるインデックスです。0はソート済みセットの最初の要素で1は2番目の要素といった具合です。

   .. start and end can also be negative numbers indicating offsets from the end of the sorted set. For example -1 is the last element of the sorted set, -2 the penultimate element and so on.

   ``start`` と ``end`` には負の値を指定することも可能です。その場合はソート済みセットの末尾からのオフセットとなります。たとえば、-1はソート済みセットの末尾の要素、-2は最後から2番目の要素です。

   .. Indexes out of range will not produce an error: if start is over the end of the sorted set, or start > end, an empty list is returned. If end is over the end of the sorted set Redis will threat it just like the last element of the sorted set.

   範囲外のインデックスでもエラーは起きません。 ``start`` がソート済みセットの末尾を超えた場合、あるいは ``start`` が ``end`` よりも大きい場合は空のリストが返ります。 ``end`` が末尾のインデックスよりも大きかった場合は、末尾の要素として扱われます。

   .. It's possible to pass the WITHSCORES option to the command in order to return not only the values but also the scores of the elements. Redis will return the data as a single list composed of value1,score1,value2,score2,...,valueN,scoreN but client libraries are free to return a more appropriate data type (what we think is that the best return type for this command is a Array of two-elements Array / Tuple in order to preserve sorting).

   値だけではなくて要素のスコアを返せるように ``WITHSCORES`` オプションを与えることもできます。Redisはデータをvalue1,score1,value2,score2,...,valueN,scoreNというリストの形で返します。しかしクライアントライブラリはデータをより適切な形で返すことも可能です。（このコマンドで一番良い形なのは2要素のタプルの配列だと思います）

   .. Return value

   **帰り値**

     Multi bulk replyが返ります。具体的には指定された範囲の要素のリストが返ります。


.. command:: ZRANGEBYSCORE key min max [LIMIT offset count [WITHSCORES]]

   .. versionadded:: 1.1

   .. versionchanged:: 1.3.4

.. command:: ZCOUNT key min max

   .. 計算時間: O(log(N))+O(M) with N being the number of elements in the sorted set and M the number of elements returned by the command, so if M is constant (for instance you always ask for the first ten elements with LIMIT) you can consider it O(log(N))

   計算時間: O(log(N))+O(M) Nはソート済みセット内の要素の数、Mはコマンドによって返される要素の数です。もしMが一定ならO(log(N))となります。（たとえば ``LIMIT`` オプションを使って常に最初の要素を取ってくる場合）

   .. Return the all the elements in the sorted set at key with a score between min and max (including elements with score equal to min or max).

   キー ``key`` に対応するソート済みセット内でスコアが ``min`` 以上 ``max`` 以下のすべての要素返します。

   .. The elements having the same score are returned sorted lexicographically as ASCII strings (this follows from a property of Redis sorted sets and does not involve further computation).

   同じスコアを持っている要素はASCII文字列として数値化されてソートされた結果が返ってきます。（これはRedisソート済みセット型の特徴と一致していてこれ以上の計算はしません）

   .. Using the optional LIMIT it's possible to get only a range of the matching elements in an SQL-alike way. Note that if offset is large the commands needs to traverse the list for offset elements and this adds up to the O(M) figure.

   ``LIMIT`` オプションを使うと条件に合う要素をSQLの様に範囲を指定して取ってこれます。オフセットが大きければ、リストをトラバースする必要があるので、O(M)の計算時間がかかることを覚えておいてください。

   .. The ZCOUNT command is similar to ZRANGEBYSCORE but instead of returning the actual elements in the specified interval, it just returns the number of matching elements.

   :com:`ZCOUNT` コマンドは :com:`ZRANGEBYSCORE` に似ていますが、実際の要素を返す代わりに条件に適用する要素の数を返します。

   .. Exclusive intervals and infinity

   **排他的な条件や無限大について**

   .. min and max can be -inf and +inf, so that you are not required to know what's the greatest or smallest element in order to take, for instance, elements "up to a given value".

   ``min`` や ``max`` は -inf や +inf も使えます。これによってたとえば「ある値以上の値を持つ要素」を取ってきたい時に、どの値が最大値あるいは最小値かを知っておく必要がありません。

   .. Also while the interval is for default closed (inclusive) it's possible to specify open intervals prefixing the score with a "(" character, so for instance

   値の範囲はデフォルトでは閉じている（内包的）なものですが、"("の文字を使うことで開いた範囲をしてすることも出来ます。たとえば::

     ZRANGEBYSCORE zset (1.3 5

   .. Will return all the values with score > 1.3 and <= 5, while for instance

   これはスコアが1.3より大きく5以下のすべての要素を返します。一方でこんな例もあります::

     ZRANGEBYSCORE zset (5 (10

   .. Will return all the values with score > 5 and < 10 (5 and 10 excluded).

   これはスコアが5より大きく10より小さい要素を返します。（5と10は含まれていません）

   .. Return value

   **帰り値**

     .. ZRANGEBYSCORE returns a Multi bulk reply specifically a list of elements in the specified score range.

     :com:`ZRANGEBYSCORE` はMulti bulk replyを返します。具体的には指定された範囲内のスコアを持つ要素のリストです。

     .. ZCOUNT returns a Integer reply specifically the number of elements matching the specified score range.

     :com:`ZCOUNT` はInteger replyを返します。具体的には指定された範囲内のスコアを持つ要素数です。

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


.. command:: ZREMRANGEBYRANK key start end 

   .. versionadded:: 1.3.4

   .. Time complexity: O(log(N))+O(M) with N being the number of elements in the sorted set and M the number of elements removed by the operation

   計算時間: O(log(N))+O(M) Nはソート済みセット内の要素数、Mは操作によって削除される要素数

   .. Remove all elements in the sorted set at key with rank between start and end. Start and end are 0-based with rank 0 being the element with the lowest score. Both start and end can be negative numbers, where they indicate offsets starting at the element with the highest rank. For example: -1 is the element with the highest score, -2 the element with the second highest score and so forth.

   ソート済みセット内の ``start`` から ``end`` 内のランクのすべての要素を削除します。 ``start`` と ``end`` は0から始まるランクで0は最小のスコアを持つ要素です。 ``start``, ``end`` ともに負の値をとることもできます。その場合は高いランクからの要素からのオフセットとなります。たとえば-1は最もスコアが高い要素、-2はスコアが2番目に高いものというようになります。

   .. Return value

   **返り値**

     .. Integer reply, specifically the number of elements removed.

     Integer replyが返ります。具体的には削除された要素数です。


.. command:: ZREMRANGEBYSCORE key min max 

   .. versionadded:: 1.1

   .. Time complexity: O(log(N))+O(M) with N being the number of elements in the sorted set and M the number of elements removed by the operation

   計算時間: O(log(N))+O(M) Nはソート済みセット内の要素数、Mは操作によって取り除かれた要素数です。

   .. Remove all the elements in the sorted set at key with a score between min and max (including elements with score equal to min or max).

   ソート済みセット内の ``min`` と ``max`` の間のスコアを持つ要素を削除します。（ ``min`` と ``max`` の値は含まれます）

   .. Return value

   **返り値**

     .. Integer reply, specifically the number of elements removed.

     Integer replyが過ります。具体的には削除された要素数です。


.. command:: ZCARD key 

   .. versionadded:: 1.1

   計算時間: O(1)

   .. Return the sorted set cardinality (number of elements). If the key does not exist 0 is returned, like for empty sorted sets.

   キー ``key`` に対応するソート済みセットの濃度（要素数）を返します。もしキーが存在しない場合は空のセットと同様に0が返ります。

   .. Return value

   **帰り値**

     Integer replyを返す。具体的には::

       the cardinality (number of elements) of the set as an integer.


.. command:: ZSCORE key element

   .. versionadded:: 1.1

   計算時間: O(1)

   .. Return the score of the specified element of the sorted set at key. If the specified element does not exist in the sorted set, or the key does not exist at all, a special 'nil' value is returned.

   キー ``key`` に対応するソート済みセット内で指定した要素 ``element`` のスコアを返します。もし指定した要素が存在しない、あるいはキー自体が存在しない場合は特別な値nilが返ります。

   .. Return value

   **帰り値**

     Bulk replyが返ります::

       the score (a double precision floating point number) represented as string.


.. command:: ZUNIONSTORE dstkey N k1 ... kN [WEIGHTS w1 ... wN] [AGGREGATE SUM|MIN|MAX]

   .. versionadded:: 1.3.12

.. command:: ZINTERSTORE dstkey N k1 ... kN [WEIGHTS w1 ... wN] [AGGREGATE SUM|MIN|MAX]

   .. versionadded:: 1.3.12

   .. 計算時間: O(N) + O(M log(M)) with N being the sum of the sizes of the input sorted sets, and M being the number of elements in the resulting sorted set

   計算時間: O(N) + O(M log(M)) Nは入力のソート済みセットのサイズの合計で、Mは返すソート済みセットの要素数。

   .. Creates a union or intersection of N sorted sets given by keys k1 through kN, and stores it at dstkey. It is mandatory to provide the number of input keys N, before passing the input keys and the other (optional) arguments.

   キー ``k1`` から ``kN`` で指定されたN個のソート済みセットの結合あるいは共通部分を作り ``dstkey`` に保存します。最初の入力するソート済みセットの数 ``N`` の指定は必須です。

   .. As the terms imply, the ZINTERSTORE command requires an element to be present in each of the given inputs to be inserted in the result. The ZUNIONSTORE command inserts all elements across all inputs.

   言葉が示すように、 :com:`ZINTERSTORE` コマンドは一致する要素が結果のソート済みセット内に挿入されていく形になります。 :com:`ZUNIONSTORE` では指定されたソート済みセット内のすべての要素が挿入されます。

   .. Using the WEIGHTS option, it is possible to add weight to each input sorted set. This means that the score of each element in the sorted set is first multiplied by this weight before being passed to the aggregation. When this option is not given, all weights default to 1.

   ``WEIGHTS`` オプションを使うことで、それぞれの入力用ソート済みセットに重みをつけることができます。これはつまり、ソート済みセットのすべての要素はまず重みとして与えられた数との積とされてからアグリゲーションされます。もしオプションが与えられなければ、すべての重みはデフォルトでは1です。

   .. With the AGGREGATE option, it's possible to specify how the results of the union or intersection are aggregated. This option defaults to SUM, where the score of an element is summed across the inputs where it exists. When this option is set to be either MIN or MAX, the resulting set will contain the minimum or maximum score of an element across the inputs where it exists.

   ``AGGREGATED`` オプションを使うと、どのように結合あるいは共通部分がアグリゲートされるかを指定することができます。デフォルトのオプションは ``SUM`` で、これは要素のスコアが合計されます。 ``MIN`` や ``MAX`` の場合は結果のセットにはそれぞれの入力のソート済みセット内の最小値、あるいは最大値の要素が含まれます。

   .. note::

      ``SUM`` オプションの部分があやしい

   .. Return value

   **帰り値**

     Integer replyが返ります。具体的にはキー ``dstkey`` に対応するソート済みセット内の要素数です。


