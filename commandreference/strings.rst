.. -*- coding: utf-8 -*-;

.. Redis String Type

===============
 Redis文字列型
===============

.. Strings are the most basic Redis kind of values. Redis Strings are binary safe, this means a Redis string can contain any kind of data, for instance a JPEG image or a serialized Ruby object, and so forth.

文字列型はRedisで扱う型の中で最も基本的なものです。Redis文字列型はバイナリセーフです。つまりRedis文字列型はどんな種類のデータも保持できるということです。たとえばJPEGイメージやシリアライズされたRubyオブジェクトなども持つことができます。

.. A String value can be at max 1 Gigabyte in length.

文字列は最大1GBまで扱うことが出来ます。

.. Strings are treated as integer values by the INCR commands family, in this respect the value of an intger is limited to a singed 64 bit value.

文字列型は :com:`INCR` コマンド群からは整数値として扱われます。この点において、整数値は符号付き64bit値に制限されます。

.. Note that the single elements contained in Redis Lists, Sets and Sorted Sets, are Redis Strings.

Redisリスト型、Redisセット型、Redisソート済みセット型、Redisハッシュ表型で保持される各要素はRedis文字列型であることを覚えておいてください。

.. Implementation details

============
 実装の詳細
============

.. Strings are implemented using a dynamic strings library called sds.c (simple dynamic strings). This library caches the current length of the string, so to obtain the length of a Redis string is an O(1) operation (but currently there is no such STRLEN command. It will likely be added later).

Redis文字列型は ``sds.c`` (simple dynamic strings) という動的文字列ライブラリを用いて実装されています。このライブラリは文字列のある時点での長さをキャッシュするので、Redis文字列型の長さの取得はO(1)の操作となっています。（現在 :com:`STRLEN` コマンドはないですが、そのうち実装されると思います）

.. Redis strings are incapsualted into Redis Objects. Redis Objects use a reference counting memory management system, so a single Redis String can be shared in different places of the dataset. This means that if you happen to use the same strings many times (especially if you have object sharing turned on in the configuration file) Redis will try to use the same string object instead to allocate one new every time.

Redis文字列はRedisオブジェクト内にカプセル化されています。Redisオブジェクトは参照カウントのメモり管理システムを持っているので、１つのRedisストリングは異なるデータセット内で共有されても大丈夫です。つまり、同じ文字列をたくさん使いたい場合には、Redisは同じ文字列を毎回作成してアロケートするのではなく、１つの文字列を使い回そうとします。（設定ファイル内でオブジェクトの共有の項目をオンにしている場合です）

.. Starting from version 1.1 Redis is also able to encode in a special way strings that are actually just numbers. Instead to save the string as an array of characters Redis will save the integer value in order to use less memory. With many datasets this can reduce the memory usage of about 30% compared to Redis 1.0.

バージョン1.1からRedisでは文字列を特別な方法でエンコードして数値のみの形にすることができるようになりました。メモリ使用量を減らすために文字列を文字の配列として保存する代わりに、Redisは整数値を保存しています。これによって、Redis 1.0と比較してメモリ使用量を30%減らすことができました。
