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

   Time complexity O(1)

   .. Remove the specified member from the set value stored at key. If member was not a member of the set no operation is performed. If key does not hold a set value an error is returned.

   .. Return value

   **文字列型**

   Integer reply, specifically::

     1 if the new element was removed
     0 if the new element was not a member of the set


.. command:: SPOP key
   
   Time complexity O(1)

Remove a random element from a Set returning it as return value. If the Set is empty or the key does not exist, a nil object is returned.
The SRANDMEMBER command does a similar work but the returned element is not removed from the Set.
Return value
Bulk reply


.. command:: SMOVE srckey dstkey member¶

   Time complexity O(1)

Move the specifided member from the set at srckey to the set at dstkey. This operation is atomic, in every given moment the element will appear to be in the source or destination set for accessing clients.
If the source set does not exist or does not contain the specified element no operation is performed and zero is returned, otherwise the element is removed from the source set and added to the destination set. On success one is returned, even if the element was already present in the destination set.
An error is raised if the source or destination keys contain a non Set value.
Return value
Integer reply, specifically:

1 if the element was moved
0 if the element was not found on the first set and no operation was performed


.. command:: SCARD key

   Time complexity O(1)

Return the set cardinality (number of elements). If the key does not exist 0 is returned, like for empty sets.
Return value
Integer reply, specifically:

the cardinality (number of elements) of the set as an integer.


.. command:: SISMEMBER key member

   Time complexity O(1)

Return 1 if member is a member of the set stored at key, otherwise 0 is returned.
Return value
Integer reply, specifically:

1 if the element is a member of the set
0 if the element is not a member of the set OR if the key does not exist


.. command:: SINTER key1 key2 ... keyN

   Time complexity O(N*M) worst case where N is the cardinality of the smallest set and M the number of sets

Return the members of a set resulting from the intersection of all the sets hold at the specified keys. Like in LRANGE the result is sent to the client as a multi-bulk reply (see the protocol specification for more information). If just a single key is specified, then this command produces the same result as SMEMBERS. Actually SMEMBERS is just syntax sugar for SINTERSECT.
Non existing keys are considered like empty sets, so if one of the keys is missing an empty set is returned (since the intersection with an empty set always is an empty set).
Return value
Multi bulk reply, specifically the list of common elements.


.. command:: SINTERSTORE dstkey key1 key2 ... keyN
Time complexity O(N*M) worst case where N is the cardinality of the smallest set and M the number of sets

This commnad works exactly like SINTER but instead of being returned the resulting set is sotred as dstkey.
Return value
Status code reply


.. command:: SUNION key1 key2 ... keyN
Time complexity O(N) where N is the total number of elements in all the provided sets

Return the members of a set resulting from the union of all the sets hold at the specified keys. Like in LRANGE the result is sent to the client as a multi-bulk reply (see the protocol specification for more information). If just a single key is specified, then this command produces the same result as SMEMBERS.
Non existing keys are considered like empty sets.
Return value
Multi bulk reply, specifically the list of common elements.


.. command:: SUNIONSTORE dstkey key1 key2 ... keyN
Time complexity O(N) where N is the total number of elements in all the provided sets

This command works exactly like SUNION but instead of being returned the resulting set is stored as dstkey. Any existing value in dstkey will be over-written.
Return value
Status code reply


.. command:: SDIFF key1 key2 ... keyN
Time complexity O(N) with N being the total number of elements of all the sets

Return the members of a set resulting from the difference between the first set provided and all the successive sets. Example:
key1 = x,a,b,c
key2 = c
key3 = a,d
SDIFF key1,key2,key3 => x,b
Non existing keys are considered like empty sets.
Return value
Multi bulk reply, specifically the list of common elements.


.. command:: SDIFFSTORE dstkey key1 key2 ... keyN
Time complexity O(N) where N is the total number of elements in all the provided sets

This command works exactly like SDIFF but instead of being returned the resulting set is stored in dstkey.
Return value
Status code reply


.. command:: SMEMBERS key

Time complexity O(N)

Return all the members (elements) of the set value stored at key. This is just syntax glue for SINTER.
Return value
Multi bulk reply


.. command:: SRANDMEMBER key

   計算時間: O(1)

   Return a random element from a Set, without removing the element. If the Set is empty or the key does not exist, a nil object is returned.
The SPOP command does a similar work but the returned element is popped (removed) from the Set.
Return value
Bulk reply


.. command:: SORT key [BY pattern] [LIMIT start count] [GET pattern] [ASC|DESC] [ALPHA] [STORE dstkey]

   Sort the elements contained in the List, Set, or Sorted Set value at key. By default sorting is numeric with elements being compared as double precision floating point numbers. This is the simplest form of SORT::

     SORT mylist

   Assuming mylist contains a list of numbers, the return value will be the list of numbers ordered from the smallest to the biggest number. In order to get the sorting in reverse order use DESC::

     SORT mylist DESC

   The ASC option is also supported but it's the default so you don't really need it. If you want to sort lexicographically use ALPHA. Note that Redis is utf-8 aware assuming you set the right value for the LC_COLLATE environment variable.

   Sort is able to limit the number of returned elements using the LIMIT option::

     SORT mylist LIMIT 0 10

   In the above example SORT will return only 10 elements, starting from the first one (start is zero-based). Almost all the sort options can be mixed together. For example the command::

     SORT mylist LIMIT 0 10 ALPHA DESC

   Will sort mylist lexicographically, in descending order, returning only the first 10 elements.

   Sometimes you want to sort elements using external keys as weights to compare instead to compare the actual List Sets or Sorted Set elements. For example the list mylist may contain the elements 1, 2, 3, 4, that are just unique IDs of objects stored at object_1, object_2, object_3 and object_4, while the keys weight_1, weight_2, weight_3 and weight_4 can contain weights we want to use to sort our list of objects identifiers. We can use the following command:

   **Sorting by external keys**

     .. code-block:: none

        SORT mylist BY weight_*

     the BY option takes a pattern (weight_* in our example) that is used in order to generate the key names of the weights used for sorting. Weight key names are obtained substituting the first occurrence of * with the actual value of the elements on the list (1,2,3,4 in our example).

     Our previous example will return just the sorted IDs. Often it is needed to get the actual objects sorted (object_1, ..., object_4 in the example). We can do it with the following 
   
   **Not Sorting at all**

     .. code-block:: none

        SORT mylist BY nosort

     also the BY option can take a "nosort" specifier. This is useful if you want to retrieve a external key (using GET, read below) but you don't want the sorting overhead.
Retrieving external keys

     .. code-block:: none

         SORT mylist BY weight_* GET object_*

     Note that GET can be used multiple times in order to get more keys for every element of the original List, Set or Sorted Set sorted.

     Since Redis >= 1.1 it's possible to also GET the list elements itself using the special # pattern::

       SORT mylist BY weight_* GET object_* GET #

   **Storing the result of a SORT operation**

     By default SORT returns the sorted elements as its return value. Using the STORE option instead to return the elements SORT will store this elements as a Redis List in the specified key. An example::
       SORT mylist BY weight_* STORE resultkey

     An interesting pattern using SORT ... STORE consists in associating an EXPIRE timeout to the resulting key so that in applications where the result of a sort operation can be cached for some time other clients will use the cached list instead to call SORT for every request. When the key will timeout an updated version of the cache can be created using SORT ... STORE again.

     Note that implementing this pattern it is important to avoid that multiple clients will try to rebuild the cached version of the cache at the same time, so some form of locking should be implemented (for instance using SETNX).

   **SORT and Hashes: BY and GET by hash field**

     It's possible to use BY and GET options against Hash fields using the following syntax::

       SORT mylist BY weight_*->fieldname
       SORT mylist GET object_*->fieldname

     The two chars string -> is used in order to signal the name of the Hash field. The key is substituted as documented above with sort BY and GET against normal keys, and the Hash stored at the resulting key is accessed in order to retrieve the specified field.

   .. Return value

   **返り値**

     Multi bulk reply, specifically a list of sorted elements.

