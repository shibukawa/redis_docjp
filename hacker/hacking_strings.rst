.. Hacking Strings

==============
文字列のハック
==============

.. The implementation of Redis strings is contained in sds.c ( sds stands for
   Simple Dynamic Strings ).

Redisの文字列の実装は、 :file:`sds.c` の中に書かれています。sdsはSimple Dynamic Stringsの略です。

.. The C structure sdshdr declared in sds.h represents a Redis string:

:file:`sds.h` の中で宣言されている、 :c:type:`sdshdr` 構造体が、Redisの文字列を表現しています。

.. code-block:: c

   struct sdshdr {
       long len;
       long free;
       char buf[];
   };

.. The buf character array stores the actual string.

:c:data:`buf` 文字配列が、実際の文字列を格納しています。

.. The len field stores the length of buf. This makes obtaining the length of a 
   Redis string an O(1) operation.

:c:member:`len` 変数は、 :c:member:`buf` の長さを格納しています。このため、Redisの文字列の長さはO(1)の操作で取得できます。

.. The free field stores the number of additional bytes available for use.

:c:member:`free` 変数はあと、何バイトの文字列が格納できるのかを保持しています。

.. Together the len and free field can be thought of as holding the metadata of 
   the buf character array.

:c:member:`len` も :c:member:`free` も、 :c:member:`buf` のメタデータを保持していると考えることができます。

.. Creating Redis Strings

Redisの文字列の作成
===================

.. A new data type named sds is defined in sds.h to be a synonymn for a character pointer:

:c:type:`sds` という名前の新しいデータ型が、 :file:`sds.h` の中で定義されています。これは文字のポインタの別名です。

.. code-block:: c

   typedef char *sds;

.. sdsnewlen function defined in sds.c creates a new Redis String:

新しい文字列を作成する、 :c:func:`sdsnewlen` 関数が、 :file:`sds.c` の中で定義されています。

.. code-block:: c

   sds sdsnewlen(const void *init, size_t initlen) {
       struct sdshdr *sh;

       sh = zmalloc(sizeof(struct sdshdr)+initlen+1);
   #ifdef SDS_ABORT_ON_OOM
       if (sh == NULL) sdsOomAbort();
   #else
       if (sh == NULL) return NULL;
   #endif
       sh->len = initlen;
       sh->free = 0;
       if (initlen) {
           if (init) memcpy(sh->buf, init, initlen);
           else memset(sh->buf,0,initlen);
       }
       sh->buf[initlen] = '\0';
       return (char*)sh->buf;
   }

.. Remember a Redis string is a variable of type struct sdshdr. But sdsnewlen 
   returns a character pointer!!

Redisの文字列は :c:type:`sdshdr` 構造体の変数ですが、 この関数は文字のポインタを返しています。

.. That's a trick and needs some explanation.

これは一種のトリックですが、多様の説明を要するでしょう。

.. Suppose I create a Redis string using sdsnewlen like below:

次のようにRedis文字列を作ったとします。

.. code-block:: c

   sdsnewlen("redis", 5);

.. This creates a new variable of type struct sdshdr allocating memory for len 
   and free fields as well as for the buf character array.

この関数は新しい :c:type:`sdshdr` 構造体の変数を作り、 :c:member:`buf` と同じようにして、 :c:member:`len` 、 :c:member:`free` にもメモリを割り当てます。

.. sh = zmalloc(sizeof(struct sdshdr)+initlen+1); // initlen is length of init argument.

.. code-block:: c

   sh = zmalloc(sizeof(struct sdshdr)+initlen+1); // initlenはinit引き数の長さ

.. After sdsnewlen succesfully creates a Redis string the result is something like:

:c:func:`sdsnewlen` が成功すると、Redis文字列は次のように作られます。

.. code-block:: none

   -----------
   |5|0|redis|
   -----------
   ^   ^
   sh  sh->buf 

.. sdsnewlen returns sh->buf to the caller.

:c:func:`sdsnewlen` は ``sh->buf`` を呼び出し元に返します。

.. What do you do if you need to free the Redis string pointed by sh?

``sh`` が指しているRedis文字列を解放したい場合にはどうすればよいでしょうか？

.. You want the pointer sh but you only have the pointer sh->buf.

必要なポインタは ``sh`` ですが、手元にあるポインタは、 ``sh->buf`` です。

.. Can you get the pointer sh from sh->buf?

``sh->buf`` から、 ``sh`` ポインタを取得することができるでしょうか？

.. Yes. Pointer arithmetic. Notice from the above ASCII art that if you subtract 
   the size of two longs from sh->buf you get the pointer sh.

はい。ポインタ演算を使うことで求めることができます。上の図を見てお分かりの通り、 ``sh->buf`` から、 ``long`` 型2つ分のサイズを引くと ``sh`` のポインタを得ることができます。

.. The sizeof two longs happens to be the size of struct sdshdr.

2つの ``long`` の大きさは、偶然ですが、 :c:type:`sdshdr` の大きさと同じです。

.. Look at sdslen function and see this trick at work:

:c:func:`sdslen` 関数の中の、このトリックが使われているコードを見てみましょう。

.. code-block:: c

   size_t sdslen(const sds s) {
       struct sdshdr *sh = (void*) (s-(sizeof(struct sdshdr)));
       return sh->len;
   }

.. Knowing this trick you could easily go through the rest of the functions in sds.c.

このトリックを知っていると、 :func:`sds.c` の他の関数も、簡単に読むことができるでしょう。

.. The Redis string implementation is hidden behind an interface that accepts only 
   character pointers. The users of Redis strings need not care about how its 
   implemented and treat Redis strings as a character pointer.

Redis文字列の実装は、文字のポインタのみを受け取るインタフェース関数の裏に隠れています。Redis文字列を使用するだけであれば、どのように実装しているかを気にするひつようはなく、単に文字のポインタとして扱うことができます。
