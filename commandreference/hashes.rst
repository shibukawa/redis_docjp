.. -*- coding: utf-8 -*-;

.. Redis Hash Type

.. index::
   pair: データ型; ハッシュ型 

.. _hashes:

==========
ハッシュ型
==========

.. Redis Hashes are unordered maps of Redis Strings between fields and values. It is possible to add, remove, test for existence of fields in O(1) amortized time. It is also possible to enumerate all the keys, values, or both, in O(N) (where N is the number of fields inside the hash).

Redisハッシュ型は順番がないRedis文字列型のフィールドと値のマップです。フィールドの追加、削除、確認をならしてO(1)で行うことができます。すべてのキー、値、またはその両方を一覧するのはO(N)で行うことができます。（Nはハッシュ内のフィールドの数です）

.. Redis Hashes are interesting because they are very well suited to represent objects. For instance web applications users can be represented by a Redis Hash containing fields such username, encrpypted_password, lastlogin, and so forth.

Redisハッシュ型は面白い作りになっています。どのような点が面白いかというと、オブジェクトを表現するのにとても適した形になっているところです。例えば、ウェブアプリケーションユーザはたとえばユーザ名、暗号化されたパスワード、最終ログイン時刻などのフィールドを持ったRedisハッシュで表現されます。

.. Another very important property of Redis Hashes is that they use very little memory for hashes composed of a small number of fields (configurable, check redis.conf for details), compared to storing every field as a top level Redis key. This is obtained using a different specialized representation for small hashes. See the implementation details paragraph below for more information.

他のとても重要な機能として、少ないフィールド数で構築されたRedisハッシュは非常にメモリを使う量が少なく、すべてのフィールドをRedisキーの最上位レベルに刷るのと比べると一目瞭然です。（この値は設定可能です。詳細はredis.confを参考にしてください）

.. Commands operating on hashes try to make a good use of the return value in order to signal the application about previous existence of fields. For instance the HSET command will return 1 if the field set was not already present in the hash, otherwise will return 0 (and the user knows this was just an update operation).

Redisハッシュはアプリケーションが以前あるフィールドが存在したかどうか警告するために便利な値を返すようにつくられています。たとえば :com:`HSET` コマンドはフィールドがすでにハッシュ表の中にあった場合は ``1`` を、それ以外の場合は ``0`` を返すようにしています。（そしてユーザはこれは単に更新操作であることを知っている）

.. The max number of fields in a set is 2^32-1 (4294967295, more than 4 billion of members per hash).

ハッシュが持てる最大数は 2^32 - 1 （4294967295, 1ハッシュあたり4億以上）です。

.. Implementation details

実装の詳細
==========

.. The obvious internal representation of hashes is indeed an hash table, as the name of the data structure itself suggests. Still the drawback of this representation is that there is a lot of space overhead for hash table metadata.

.. note:: 翻訳あやしい

Redisハッシュの内部表現は事実データ構造地震の名前が示すとおりハッシュ表となっています。この実装の欠点はハッシュ表のメタデータに多くの空間的オーバーヘッドがあるということです。

.. Because one of the most interesting uses of Hashes is object encoding, and objects are often composed of a few fields each, Redis uses a different internal representation for small hashes (for Redis to consider a hash small, this must be composed a limited number of fields, and each field and value can't exceed a given number of bytes. All this is user-configurable).

Redisハッシュの面白い使い方としてオブジェクトエンコーディングがあります。オブジェクトはしばしばいくつかのフィールドにより構成されます。Redisではそれぞれにオブジェクトに異なる内部的に小さなハッシュ（以下小ハッシュ）を持っています。（Redisはハッシュを小さくするために、この小ハッシュのフィールド数には上限を設けています。各フィールドと値は設定されたバイト数以下でなければなりません。これらはすべて設定可能です。）

.. Small hashes are thus encoded using a data structure called zipmap (is not something you can find in a CS book, the name is a Redis invention), that is a very memory efficient data structure to represent string to string maps, at the cost of being O(N) instead of O(1) for most operations. Since the constant times of this data structure are very small, and the zipmaps are converted into real hash tables once they are big enough, the amortized time of Redis hashes is still O(1), and in the practice small zipmaps are not slower than small hash tables because they are designed for good cache locality and fast access.

したがって小ハッシュは **zipmap** と呼ばれるデータ構造を用いてエンコードされています。（zipmapはコンピュータサイエンス系の本を読んでも出てきません。Redis開発中に命名されました。）このデータ構造は非常にメモリを文字列を文字列に対応させるマッピングにおいてメモリを効率的に使う構造になっています。大抵の操作でO(1)ではなくO(N)になるという犠牲を払っても、メモリの低省を優先しました。
しかしこのデータ構造が普遍である時間は非常に短く、また大きくなった場合にはハッシュ表に変換されるため、Redisハッシュの操作をならすとO(1)にはなっているはずです。実際に小さなzipmapは効率的なローカルキャッシュに素早くアクセスできるため小さなハッシュ表よりも遅いということはありません。

.. The result is that small hashes are both memory efficient and fast, while bigger hashes are fast but not as memory efficient than small hashes.

結果として小ハッシュはメモリを効率的に使い、素早くアクセスでき、一方で大きなハッシュは早いけれどメモリ効率は小ハッシュよりも悪くなっています。


ハッシュ型のコマンド
====================

.. command:: HSET key field value 

   .. versionadded:: 1.3.10

   計算時間: O(1)

   .. Set the specified hash field to the specified value.

   キー ``key`` に対応するハッシュの指定されたフィールド ``field`` に値 ``value`` をセットする。

   .. If key does not exist, a new key holding a hash is created.

   キーが存在しない場合は、 ``field`` と ``value`` のハッシュを持つ新しいキーが生成される。

   .. If the field already exists, and the HSET just produced an update of the value, 0 is returned, otherwise if a new field is created 1 is returned.

   フィールドがすでに存在する場合して、 :com:`HSET` が値を更新しただけの場合は0が返ります。新しいフィールドが作成された場合は1が返ります。

   .. Return value

   **帰り値**

     Integer replyが返ります。

.. command:: HGET key field

   .. versionadded:: 1.3.10

   計算時間: O(1)

   .. If key holds a hash, retrieve the value associated to the specified field.

   もしキー ``key`` がハッシュを持っていた場合、指定したフィールド ``field`` に対応する値を取得します。

   .. If the field is not found or the key does not exist, a special 'nil' value is returned.

   もしフィールドが見つからない場合、あるはキーが見つからない場合は、nilが返ります。

   .. Return value

   **帰り値**

     Bulk replyを返します。


.. command:: HSETNX key field value

   .. versionadded:: 1.3.10

   計算時間: O(1)

   .. Set the specified hash field to the specified value, if field does not exist yet.

   キー ``key`` に対応するハッシュ内にフィールド ``field`` が存在しない場合、値 ``value`` をセットします。

   .. If key does not exist, a new key holding a hash is created.

   キーが存在しない場合は、キーに対して ``field`` と ``value`` の組を持った新しいハッシュが作成されます

   .. If the field already exists, this operation has no effect and returns 0. Otherwise, the field is set to value and the operation returns 1.

   もしフィールドがすでに存在する場合、この操作はなんの処理もせず0を返します。それ以外の場合はフィールド ``field`` に値 ``value`` をセットして1を返します。

   .. Return value

   **帰り値**

     Integer replyを返します。


.. command:: HMSET key field1 value1 ... fieldN valueN

   .. versionadded:: 1.3.10

   計算時間: O(N) （Nはフィールドの数）


   .. Set the respective fields to the respective values. HMSET replaces old values with new values.

   それぞれのフィールドにそれぞれの値をセットします。 :com:`HMSET` では古い値を新しい値で置き換えます。

   .. If key does not exist, a new key holding a hash is created.

   キーが存在しない場合は、指定したハッシュを持った新しいキーが作成されます。

   .. Return value

   **帰り値**

     Status code replyが返ります。 :com:`HMSET` は絶対に失敗しないので常に ``+OK`` が返ります。


.. command:: HMGET key field1 ... fieldN

   .. versionadded:: 1.3.10

   計算時間: O(N) （Nはフィールドの数）

   .. Retrieve the values associated to the specified fields.

   指定した複数のキー ``keyN`` に対応するハッシュ内のフィールド ``field`` に保持された値を取得します。

   .. If some of the specified fields do not exist, nil values are returned. Non existing keys are considered like empty hashes.

   もし指定したキーの内いくつかが存在しない場合、nilが返ります。存在しないキーに関しては空のハッシュと同等に扱われます。

   .. Return value

   **帰り値**

     .. Multi Bulk Reply specifically a list of all the values associated with the specified fields, in the same order of the request.

     Multi Bulk Replyが返ります。具体的には指定したそれぞれのフィールド ``fieldN`` に対する複数の値を持ったリストが返ります。値は指定したフィールドの順です。


.. command:: HINCRBY key field value

   .. versionadded:: 1.3.10

   計算時間: O(1)

   .. Increment the number stored at field in the hash at key by value. If key does not exist, a new key holding a hash is created. If field does not exist or holds a string, the value is set to 0 before applying the operation.

   キー ``key`` に対応するハッシュ内のフィールド ``field`` に保持されている値を ``value`` だけインクリメントします。キーが存在しない場合は ``filed`` と ``value`` の組を持った新しいハッシュが作成されます。もしフィールドが存在しない、あるいは文字列を持っている場合は値は0となります。

   .. The range of values supported by HINCRBY is limited to 64 bit signed integers.

   :com:`HINCRBY` で指定できる値の範囲は64bit符号付き整数の範囲内です。

   .. Examples

   **例**

     .. Since the value argument is signed you can use this command to perform both increments and decrements:

     値は符号付きなので、インクリメントにもデクリメントにも使えます。

     .. code-block:: none

        HINCRBY key field 1 (increment by one)
        HINCRBY key field -1 (decrement by one, just like the DECR command)
        HINCRBY key field -10 (decrement by 10)

   .. Return value

   **帰り値**
   
     Integer replyが返ります。インクリメント後の新しい値が返ります。


.. command:: HEXISTS key field

   .. versionadded::  1.3.10

   計算時間: O(1)

   .. Return 1 if the hash stored at key contains the specified field.

   キー ``key`` に対応するハッシュ内に指定したフィールド ``field`` があれば1を返します。

   .. Return 0 if the key is not found or the field is not present.

   もしキーあるいはフィールドが存在しない場合は0が返ります。

   .. Return value

   **帰り値**

     Integer replyが返ります。


.. command:: HDEL key field

   .. versionadded:: 1.3.10

   計算時間: O(1)

   .. Remove the specified field from an hash stored at key.

   キー ``key`` に対応するハッシュ内のフィールド ``field`` を削除します。

   .. If the field was present in the hash it is deleted and 1 is returned, otherwise 0 is returned and no operation is performed.

   もしフィールドがハッシュ内に存在する場合は、そのフィールドは削除され1が返ります。それ以外の場合は0が返り、なんの操作も行われません。

   .. Return value

   **帰り値**

     Integer replyが返ります。


.. command:: HLEN key

   .. versionadded:: 1.3.10

   計算時間: O(1)

   .. Return the number of entries (fields) contained in the hash stored at key. If the specified key does not exist, 0 is returned assuming an empty hash.

   キー ``key`` に対応するハッシュに存在するエントリ（フィールド）数を返します。もし指定したキーが存在しない場合は、空のハッシュと同様に0が返ります。

   .. Return value

   **帰り値**

     Integer replyが返ります。


.. command:: HKEYS key

   .. versionadded:: 1.3.10

.. command:: HVALS key

   .. versionadded:: 1.3.10

.. command:: HGETALL key

   .. versionadded:: 1.3.10

   計算時間: O(N), Nは要素数

   .. HKEYS returns all the fields names contained into a hash, HVALS all the associated values, while HGETALL returns both the fields and values in the form of field1, value1, field2, value2, ..., fieldN, valueN.

   :com:`HKEYS` はキー ``key`` に対応するハッシュ内のすべてのフィールド名を返します。 :com:`HVALS` はキー ``key`` に対応するハッシュ内の全ての値、 :com:`HGETALL` はフィールドと値の組み合わせを field1, value1, field2, value2, ..., fieldN, valueNの形で返します。

   .. Return value

   **帰り値**

     Multi Bulk Replyが返ります。


