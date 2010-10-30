.. -*- coding: utf-8 -*-;

.. Redis List Type

===============
 Redisリスト型
===============

.. Redis Lists are lists of Redis Strings, sorted by insertion order. It's possible to add elements to a Redis List pushing new elements on the head (on the left) or on the tail (on the right) of the list.

Redisリスト型はRedis文字列型のリストになっています。Redisリストには新しい要素をリストの先頭（左側）または末尾（右側）に追加することが可能です。

.. The LPUSH command inserts a new elmenet on head, while RPUSH inserts a new element on tail. A new list is created when one of this operations is performed against an empty key.

:com:`LPUSH` コマンドでは新しい要素をリストの先頭に追加して、 :com:`RPUSH` では新しい要素を末尾に追加します。対応するリストを持たないキーに対してこの操作が行われた場合は、新しいリストが作成されます。

.. For instance if perform the following operations:
たとえば次のような操作をした場合は結果は次のようになります::

   LPUSH mylist a   # now the list is "a"
   LPUSH mylist b   # now the list is "b","a"
   RPUSH mylist c   # now the list is "b","a","c" (RPUSH was used this time)

.. The resulting list stored at mylist will contain the elements "b","a","c".

最終的に上のサンプルでは ``mylist`` は要素 "b","a","c" を保持しています。

.. The max length of a list is 2^32-1 elements (4294967295, more than 4 billion of elements per list).

Redisリストの要素数の最大値は 2^32-1（4294967295, 1リストあたり4億以上）です。

.. Implementation details

実装の詳細
==========

.. Redis Lists are implemented as doubly liked lists. A few commands benefit from the fact the lists are doubly linked in order to reach the needed element starting from the nearest extreme (head or tail). LRANGE and LINDEX are examples of such commands.

Redisリストは双方向リストで実装されています。両端（先頭または末尾）から必要な要素にアクセスするために双方向リストで実装されていることによって、いくつかのコマンドではその恩恵を受けています。 :com:`LRANGE` や :com:`LINDEX` といったコマンドがその例です。

.. The use of linked lists also guarantees that regardless of the length of the list pushing and popping are O(1) operations.

双方向リストを使うことによって、リスト長にかかわらずプッシュやポップがO(1)の操作になることが保証されています。

.. Redis Lists cache length information so LLEN is O(1) as well.

Redisリスト型はリスト長の情報をキャッシュするので :com:`LLEN` は同様にO(1)の操作になります。
