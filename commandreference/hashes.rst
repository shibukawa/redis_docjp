.. -*- coding: utf-8 -*-;

.. Redis Hash Type

===================
 Redisハッシュ表型
===================

.. Redis Hashes are unordered maps of Redis Strings between fields and values. It is possible to add, remove, test for existence of fields in O(1) amortized time. It is also possible to enumerate all the keys, values, or both, in O(N) (where N is the number of fields inside the hash).

Redisハッシュ表型は順番がないRedis文字列型のフィールドと値のマップです。フィールドの追加、削除、確認をならしてO(1)で行うことができます。すべてのキー、値、またはその両方を一覧するのはO(N)で行うことができます。（Nはハッシュ表内のフィールドの数です）

.. Redis Hashes are interesting because they are very well suited to represent objects. For instance web applications users can be represented by a Redis Hash containing fields such username, encrpypted_password, lastlogin, and so forth.

Redisハッシュ表型は面白い作りになっています。どのような点が面白いかというと、オブジェクトを表現するのにとても適した形になっているところです。例えば、ウェブアプリケーションユーザはたとえばユーザ名、暗号化されたパスワード、最終ログイン時刻などのフィールドを持ったRedisハッシュ表で表現されます。

.. Another very important property of Redis Hashes is that they use very little memory for hashes composed of a small number of fields (configurable, check redis.conf for details), compared to storing every field as a top level Redis key. This is obtained using a different specialized representation for small hashes. See the implementation details paragraph below for more information.

他のとても重要な機能として、少ないフィールド数で構築されたRedisハッシュ表は非常にメモリを使う量が少なく、すべてのフィールドをRedisキーの最上位レベルに刷るのと比べると一目瞭然です。（この値は設定可能です。詳細はredis.confを参考にしてください）

.. Commands operating on hashes try to make a good use of the return value in order to signal the application about previous existence of fields. For instance the HSET command will return 1 if the field set was not already present in the hash, otherwise will return 0 (and the user knows this was just an update operation).

Redisハッシュ表はアプリケーションが以前あるフィールドが存在したかどうか警告するために便利な値を返すようにつくられています。たとえば :cmd:`HSET` コマンドはフィールドがすでにハッシュ表の中にあった場合は ``1`` を、それ以外の場合は ``0``　を返すようにしています。（そしてユーザはこれは単に更新操作であることを知っている）

.. The max number of fields in a set is 2^32-1 (4294967295, more than 4 billion of members per hash).

ハッシュ表が持てる最大数は 2^32 - 1 （4294967295, 1ハッシュ表あたり4億）です。

.. Implementation details

実装の詳細
==========

.. The obvious internal representation of hashes is indeed an hash table, as the name of the data structure itself suggests. Still the drawback of this representation is that there is a lot of space overhead for hash table metadata.

Because one of the most interesting uses of Hashes is object encoding, and objects are often composed of a few fields each, Redis uses a different internal representation for small hashes (for Redis to consider a hash small, this must be composed a limited number of fields, and each field and value can't exceed a given number of bytes. All this is user-configurable).

Small hashes are thus encoded using a data structure called zipmap (is not something you can find in a CS book, the name is a Redis invention), that is a very memory efficient data structure to represent string to string maps, at the cost of being O(N) instead of O(1) for most operations. Since the constant times of this data structure are very small, and the zipmaps are converted into real hash tables once they are big enough, the amortized time of Redis hashes is still O(1), and in the practice small zipmaps are not slower than small hash tables because they are designed for good cache locality and fast access.

The result is that small hashes are both memory efficient and fast, while bigger hashes are fast but not as memory efficient than small hashes.
