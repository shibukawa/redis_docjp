.. -*- coding: utf-8 -*-;

.. Redis Set Type

===============
 Redisセット型
===============

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
