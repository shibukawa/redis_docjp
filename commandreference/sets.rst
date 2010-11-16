.. -*- coding: utf-8 -*-;

.. Redis Set Type

.. index::
   pair: データ型; セット型 

.. _sets:

========
セット型
========

.. Redis Sets are unordered collections of Redis Strings. It's possible to add, remove, and test for existence of members in O(1).

Redisセット型はRedis文字列型の順不同の集合です。Redisセット型ではメンバの追加、削除、確認をすべてO(1)で行うことができます。

.. Redis Sets have the desirable property of not allowing repeated members. Adding the same element multiple times will result in a set having a single copy of this element. Practically speaking this means that adding an members does not require a "check if exists then add" operation.

Redisセットはメンバの重複を許可しないという価値のある性質を持っています。同じ要素を何度も追加しても結果としてセット内にはその要素は単一のコピーしか持ち合わせません。事実上、このことはメンバを追加する際に「そのメンバが存在するか確認した後に追加する」という操作を必要としない、ということを意味します。

.. Commands operating on sets try to make a good use of the return value in order to signal the application about previous existence of members. For instance the SADD command will return 1 if the element added was not already a member of the set, otherwise will return 0.

セットを操作するコマンドはアプリケーションにメンバが存在したことを警告するのに便利な値を返すようになっています。たとえば :com:`SADD` コマンドはもし要素がまだセットのメンバでなかったら ``1`` を返し、そうでなかったら ``0`` を返すようになっています。

.. The max number of members in a set is 2^32-1 (4294967295, more than 4 billion of members per set).

セットの要素数の最大値は 2^32-1（4294967295, 1セットあたり4億以上のメンバ）です。

.. Redis Sets support a wide range of operations, like union, intersection, difference. Intersection is optimized in order to perform the smallest number of lookups. For instance if you try to intersect a 10000 members set with a 2 members set Redis will iterate the 2 members set testing for members existence in the other set, performing 2 lookups instead of 10000.

Redisセットは幅広い操作をサポートしています。たとえば結合、共通部分、差異の取得などです。共通部分の取得は参照回数が最小限になるように最適化されています。たとえば10000要素あるセットと2要素のセットの共通部分を取得しようとした場合、Redisは2要素を持つセットをイタレートしてもう一方のセットにそれぞれの要素が存在するかの確認をします。10000要素の参照ではなく2要素のみの参照で済むわけです。

.. Implementation details

実装の詳細
==========

.. Redis Sets are implemented using hash tables, so adding, removing and testing for members is O(1) in the average. The hash table will automatically resize when new elements are added or removed into a Set.

Redisセットはハッシュ表を使って実装されていまので、メンバの追加、削除、確認といった操作は平均でO(1)となります。ハッシュ表は新しい要素が追加または削除されたときに自動的にリサイズします。

.. The hash table resizing is a blocking operation performed synchronously so working with huge sets (consisting of many millions of elements) care should be taken when mass-inserting a very big amount of elements in a Set while other clients are querying Redis at high speed.

ハッシュ表のリサイズは同期的に行われるブロッキング操作です。ですので、（数百万要素を持っているような）巨大なセットを扱う場合は、他のクライアントがRedisに対して高速にクエリを投げているときに大量の要素を挿入するようなことはしないように気をつけるべきです。

.. It is possible that in the near future Redis will switch to skip lists (already used in sorted sets) in order to avoid such a problem.

このような問題を回避するために、近いうちにスキップリストによる実装に変更する予定です。（ソート済みセットではすでにそうなっています）


セット型のコマンド
==================

.. command:: SADD key member
   
   計算時間: O(1)

   .. Add the specified member to the set value stored at key. If member is already a member of the set no operation is performed. If key does not exist a new set with the specified member as sole member is created. If the key exists but does not hold a set value an error is returned.

   指定されたメンバ ``member`` を

   .. Return value

   **返り値**

     Integer reply, specifically:

       1 if the new element was added
       0 if the element was already a member of the set


.. command:: SREM key member

   計算時間 O(1)

   .. Remove the specified member from the set value stored at key. If member was not a member of the set no operation is performed. If key does not hold a set value an error is returned.

   指定したメンバー ``member`` をキー ``key`` に対応するセットから取り除きます。もし ``member`` がセットのメンバ出なかった場合は何も実行されません。もし ``key`` に対応する値がセット型でなかった場合はエラーが返ります。

   .. Return value

   **帰り値**

   .. Integer reply, specifically

     Integer replyが返ります。具体的には下記::

       1 if the new element was removed
       0 if the new element was not a member of the set


.. command:: SPOP key
   
   計算時間 O(1)

   .. Remove a random element from a Set returning it as return value. If the Set is empty or the key does not exist, a nil object is returned.

   キー ``key`` に対応するセットからランダムで１要素を選んで削除し、それを返り値として返します。もしセットが空だった、あるいは ``key`` が存在しなかった場合はnilオブジェクトが返ります。

   .. The SRANDMEMBER command does a similar work but the returned element is not removed from the Set.

   :com:`SRANDMEMBER` コマンドは似た動作をしますが、返される要素はセットから取り除かれません。

   .. Return value

   **返り値**

     Bulk replyが返ります。


.. command:: SMOVE srckey dstkey member¶

   計算時間 O(1)

   .. Move the specifided member from the set at srckey to the set at dstkey. This operation is atomic, in every given moment the element will appear to be in the source or destination set for accessing clients.

   指定されたメンバー ``member`` をキー ``srckey`` に対応するセットから ``dstkey`` に対応するセットに移します。この操作はアトミックで、アクセスしているクライアントからはどんな要素も移動元か異動先のセット内に確認できます。

   .. If the source set does not exist or does not contain the specified element no operation is performed and zero is returned, otherwise the element is removed from the source set and added to the destination set. On success one is returned, even if the element was already present in the destination set.

   もし移動元のセットが存在しない、あるいは指定した要素を含んでいなかった場合は何も操作は行われず、ゼロが返ります。そうでない場合は要素は移動元のセットから削除され、異動先のセットに追加されます。成功した場合は、移動した要素が返り値として返されます。これは異動先にその要素がすでにあった場合でも同様です。

   .. An error is raised if the source or destination keys contain a non Set value.

   もし異動元あるいは異動先に対応するキーがセット型でない値を保持していたらエラーが返ります。

   .. Return value
   
   **返り値**

     Integer replyが返ります。具体的には下記::

       1 if the element was moved
       0 if the element was not found on the first set and no operation was performed


.. command:: SCARD key

   計算時間 O(1)

   .. Return the set cardinality (number of elements). If the key does not exist 0 is returned, like for empty sets.

   セットの濃度（要素の数）を返します。もしキーが存在しない場合は空のセットと同様に0が返ります。

   .. Return value

   **返り値**

     .. Integer reply, specifically:

     Integer replyが返ります。具体的には::

       the cardinality (number of elements) of the set as an integer.


.. command:: SISMEMBER key member

   計算時間 O(1)

   .. Return 1 if member is a member of the set stored at key, otherwise 0 is returned.

   もしメンバー ``member`` がキー ``key`` に対応するセットに含まれていたら1が返り、無かった場合は0が返ります。

   .. Return value

   **返り値**

     .. Integer reply, specifically:

     Integer replyが返ります。具体的には下記::

       1 if the element is a member of the set
       0 if the element is not a member of the set OR if the key does not exist


.. command:: SINTER key1 key2 ... keyN

   .. Time complexity O(N*M) worst case where N is the cardinality of the smallest set and M the number of sets

   計算時間 O(N*M) 最悪の場合のN*MではNは最小のセットの濃度でMはセット数です。

   .. Return the members of a set resulting from the intersection of all the sets hold at the specified keys. Like in LRANGE the result is sent to the client as a multi-bulk reply (see the protocol specification for more information). If just a single key is specified, then this command produces the same result as SMEMBERS. Actually SMEMBERS is just syntax sugar for SINTERSECT.

   指定された各キー ``keyN`` すべての共通の要素からなるセットのメンバーを返します。 :com:`LRANGE` のように結果はmulti bulk replyの形でクライアントに返されます。（より深い情報は仕様を参照のこと）キーが一つだけ指定された場合は :com:`SMEMBERS` と同じ結果が返ります。実際には :com:`SMEMBER` は :com:`SINTERSECT` の糖衣構文に過ぎません。

   .. Non existing keys are considered like empty sets, so if one of the keys is missing an empty set is returned (since the intersection with an empty set always is an empty set).

   存在しないキーに関しては空のセットと同様に扱われます。したがって、もし指定したキーのうち1つが存在しなかった場合は空のセットが返ります。（空のセットとの共通部分は常に空です）

   .. Return value
   
   **返り値**

     .. Multi bulk reply, specifically the list of common elements.

     Multi bulk replyが返ります。具体的には共通の要素のリストです。


.. command:: SINTERSTORE dstkey key1 key2 ... keyN

   .. Time complexity O(N*M) worst case where N is the cardinality of the smallest set and M the number of sets

   計算時間 O(N*M) 最悪の場合のN*MではNは最小のセットの濃度でMはセット数です。

   .. This commnad works exactly like SINTER but instead of being returned the resulting set is sotred as dstkey.

   このコマンドは :com:`SINTER` とまさに同様に動作しますが、結果のセットを返す代わりにキー ``dstkey`` に結果を保存します。

   .. Return value

   **返り値**

     Status code replyが返ります。


.. command:: SUNION key1 key2 ... keyN

   .. Time complexity O(N) where N is the total number of elements in all the provided sets

   計算時間 O(N): Nは指定されたキーに対応するセット中の要素数の合計

   .. Return the members of a set resulting from the union of all the sets hold at the specified keys. Like in LRANGE the result is sent to the client as a multi-bulk reply (see the protocol specification for more information). If just a single key is specified, then this command produces the same result as SMEMBERS.

   指定したキー ``keyN`` に対応するすべてのセットの結合からなるセット内の要素を返します。 :com:`LRANGE` のようにクライアントに返される結果はmulti-bulk replyになります。（詳細は仕様を参照のこと）キーが1つだけ指定された場合は :com:`SMEMBERS` と同じ結果となります。

   .. Non existing keys are considered like empty sets.

   存在しないキーの場合は空のセットが返ります。

   .. Return value

   **返り値**

     .. Multi bulk reply, specifically the list of common elements.

     Multi bulk replyが返ります。具体的には結合後のセット内の要素のリストです。

     .. note::

        原文では「共通の要素」(common elements)となっているが間違いだと思われる。


.. command:: SUNIONSTORE dstkey key1 key2 ... keyN

   .. Time complexity O(N) where N is the total number of elements in all the provided sets

   計算時間 O(N): Nは指定されたキーに対応するセット中の要素数の合計

   .. This command works exactly like SUNION but instead of being returned the resulting set is stored as dstkey. Any existing value in dstkey will be over-written.

   このコマンドは :com:`SUNION` とほぼ同じような動作をしますが、結果のセットが返されるのではなく、 ``dstkey`` で指定されたセットに保存されます。 ``dstkey`` に対応するセットは上書きされます。

   .. Return value

   **返り値**

     Status code replyが返ります。


.. command:: SDIFF key1 key2 ... keyN

   .. Time complexity O(N) with N being the total number of elements of all the sets

   計算時間 O(N): Nは指定されたキーに対応するセット中の要素数の合計

   .. Return the members of a set resulting from the difference between the first set provided and all the successive sets. Example:

   最初のキー ``key1`` に対応するセットとそれ以降のキー ``keyN`` に対応するセットの差分からなるセットの要素を返します。例えば::

     key1 = x,a,b,c
     key2 = c
     key3 = a,d
     SDIFF key1,key2,key3 => x,b

   .. Non existing keys are considered like empty sets.

   存在しないキーは空のセットとして扱われます。

   .. Return value

   **返り値**

     .. Multi bulk reply, specifically the list of common elements.

     Multi bulk replyが返ります。具体的には差分のセットの要素からなるリストです。

     .. note::

        原文では「共通の要素」(common elements)となっているが間違いだと思われる。


.. command:: SDIFFSTORE dstkey key1 key2 ... keyN

   .. Time complexity O(N) where N is the total number of elements in all the provided sets

   計算時間 O(N): Nは指定されたキーに対応するセット中の要素数の合計

   .. This command works exactly like SDIFF but instead of being returned the resulting set is stored in dstkey.

   このコマンドは :com:`SDIFF` とほぼ同様に動作しますが、結果のセットを返す代わりに ``dstkey`` に対応するセットに保存します。

   .. Return value

   **返り値**

     Status code replyを返します。


.. command:: SMEMBERS key

   .. Time complexity O(N)

   計算時間 O(N)

   .. Return all the members (elements) of the set value stored at key. This is just syntax glue for SINTER.

   キー ``key`` に対応するセット内のすべてのメンバ（要素）を返します。これは :com:`SINTER` の糖衣構文にすぎません。

   .. Return value

   **返り値**

     Multi bulk replyが返ります。


.. command:: SRANDMEMBER key

   計算時間: O(1)

   .. Return a random element from a Set, without removing the element. If the Set is empty or the key does not exist, a nil object is returned.

   キー ``key`` に対応するセットからランダムに１つの要素を返します。もし指定されたセットが空、またはキーが存在しなかった場合はnilオブジェクトが返ります。

   .. The SPOP command does a similar work but the returned element is popped (removed) from the Set.

   :com:`SPOP` コマンドは似た動作をしますが、 :com:`SPOP` の場合は要素がセットからポップされ（削除され）ます。
   
   .. Return value

   **返り値**

     Bulk replyが返ります。


