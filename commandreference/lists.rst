.. -*- coding: utf-8 -*-;

.. Redis List Type

.. index::
   pair: データ型; リスト型 

.. _lists:

========
リスト型
========

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

.. command:: RPUSH key string
.. command:: LPUSH key string

   計算時間: O(1)

   .. Add the string value to the head (LPUSH) or tail (RPUSH) of the list stored at key. If the key does not exist an empty list is created just before the append operation. If the key exists but is not a List an error is returned.

   文字列型の値 ``string`` をキー ``key`` にひもづいているリストの先頭（ :com:`LPUSH` ）または末尾（ :com:`RPUSH` ）に加えます。もしキーが存在しない場合は空のリストが作成された後に、前述の操作が行われます。キーが存在するけれど値がリスト型でなかった場合はエラーが返ります。

   .. Return value

   **返り値**

   .. Integer reply, specifically, the number of elements inside the list after the push operation.

   Integer replyが返ります。具体的には操作後のリストの要素数です。


.. command:: LLEN key

   計算時間: O(1)

   Return the length of the list stored at the specified key. If the key does not exist zero is returned (the same behaviour as for empty lists). If the value stored at key is not a list an error is returned.

   .. Return value

   **返り値**

     Integer replyが返ります。具体的には下記::

       The length of the list.


.. command:: LRANGE key start end

   計算時間: O(start+n) （nは範囲の長さ、startは開始位置のオフセット）

   .. Return the specified elements of the list stored at the specified key. Start and end are zero-based indexes. 0 is the first element of the list (the list head), 1 the next element and so on.

   キー ``key`` に対応するリスト内の指定された位置の要素を返します。 ``start`` と ``end`` はゼロから始まるインデックスです。0はリストの先頭の要素を指します。1は2番目の要素、といった具合です。

   .. For example LRANGE foobar 0 2 will return the first three elements of the list.

   例えば ``LRANGE foobar 0 2`` と下場合にはリストの最初の3要素を返します。

   .. start and end can also be negative numbers indicating offsets from the end of the list. For example -1 is the last element of the list, -2 the penultimate element and so on.

   ``start`` と ``end`` は負の整数とすることもできます。その場合はリストの末尾から数えたオフセットになります。例えば、-1はリストの末尾、-2は最後から2番目といった感じです。

   .. **Consistency with range functions in various programming languages**

   **多くのプログラミング言語におけるrange関数との一貫性**

   .. Note that if you have a list of numbers from 0 to 100, LRANGE 0 10 will return 11 elements, that is, rightmost item is included. This may or may not be consistent with behavior of range-related functions in your programming language of choice (think Ruby's Range.new, Array#slice or Python's range() function).

   0から100の数を持つリストを考えてください。この場合 ``LRANGE 0 10`` は11個の要素を返します。つまり最も右の要素が含まれるわけです。これはあなたがいま使っているプログラミング言語のrange関数、あるいはそれに類する関数（たとえばRubyの ``Range.new``, ``Array#slice`` またはPythonの ``range()`` 関数）の動作と一致するかもしれないし、一致しないかもしれません。このことは注意してください。

   .. LRANGE behavior is consistent with one of Tcl.

   :com:`LRANGE` の動作はtclのそれと一致します。

   .. **Out-of-range indexes**

   **範囲外のインデックス**
   
   .. Indexes out of range will not produce an error: if start is over the end of the list, or start > end, an empty list is returned. If end is over the end of the list Redis will threat it just like the last element of the list.

   範囲外のインデックスはエラーの原因とはなりません。もし ``start`` がリストの末尾を超えた値、あるいは ``start`` が ``end`` よりも大きい場合は空リストが返ります。もし ``end`` がリストの末尾を超えていた場合はRedisはその値をリストの末尾に勝手に置き換えます。

   .. Return value

   **返り値**

   Multi bulk replyが返ります。具体的には与えられた範囲内の要素数です。


.. command:: LTRIM key start end

   計算時間: O(n) （nはリストの長さから範囲の長さを引いたものです）

   .. Trim an existing list so that it will contain only the specified range of elements specified. Start and end are zero-based indexes. 0 is the first element of the list (the list head), 1 the next element and so on.

   既存のリストを指定された範囲の要素を持つリストになるようにトリムします。 ``start`` と ``end`` は0から始まるインデックスです。0はリストの先頭を指し、1は2番目を指すという具合です。

   .. For example LTRIM foobar 0 2 will modify the list stored at foobar key so that only the first three elements of the list will remain.

   たとえば、 ``LTRIM foobar 0 2`` は ``foobar`` というキーに対応するリストを最初の3つの要素しか持たないリストに変更します。

   .. start and end can also be negative numbers indicating offsets from the end of the list. For example -1 is the last element of the list, -2 the penultimate element and so on.

   ``start`` と ``end`` は負の整数にすることも可能です。この場合はリストの末尾からのオフセットとなります。たとえば、-1はリストの末尾、-2は最後から2番目、といった具合です。


   .. Indexes out of range will not produce an error: if start is over the end of the list, or start > end, an empty list is left as value. If end over the end of the list Redis will threat it just like the last element of the list.

   範囲外のインデックスを指定してもエラーにはなりません。もし ``start`` がリストの末尾を超えた値、あるいは ``start`` が ``end`` よりも大きな値になったとしても、空リストが返るだけです。もし ``end`` がリストの末尾を超えた場合はRedisはそれを勝手にリストの末尾として解釈します。

   .. Hint: the obvious use of LTRIM is together with LPUSH/RPUSH. For example:

   ヒント: :com:`LTRIM` を :com:`LPUSH`/:com:`RPUSH` と一緒に用いるというのはよくあるイディオムです::
   
     LPUSH mylist <someelement>
     LTRIM mylist 0 99

   .. The above two commands will push elements in the list taking care that the list will not grow without limits. This is very useful when using Redis to store logs for example. It is important to note that when used in this way LTRIM is an O(1) operation because in the average case just one element is removed from the tail of the list.

   いま例示した2つのコマンドは要素をあるリストに追加するものですが、そのリストが際限なしに大きくならないような操作をしています。この例は例えばRedisでログを残す場合に非常に有効です。:com:`LTRIM` がこのような用法で用いられた場合には計算時間はO(1)になることに注目してください。その理由は一般的にはリストの末尾の要素だけが削除されるだけだからです。

   .. Return value

   **返り値**

     Status code replyが返ります。

.. command:: LINDEX key index

   計算時間: O(n) （nはリストの長さ）

   .. Return the specified element of the list stored at the specified key. 0 is the first element, 1 the second and so on. Negative indexes are supported, for example -1 is the last element, -2 the penultimate and so on.

   キー ``key`` に対応するリスト内の指定されたインデックス ``index`` が指す要素を返します。0はリストの先頭、1は2番目の要素、といった具合です。負のインデックスも指定可能です。たとえば-1はリストの末尾、-2は最後から2番目、と続きます。

   .. If the value stored at key is not of list type an error is returned. If the index is out of range a 'nil' reply is returned.

   もしキー ``key`` に対応する値がリスト型でない場合、エラーが返ります。もしインデックスが範囲外だった場合、 "nil" が返ります。

   .. Note that even if the average time complexity is O(n) asking for the first or the last element of the list is O(1).

   たとえ平均計算時間がO(n)だとしても、先頭もしくは末尾の要素の場合にはO(1)で取得可能であることに気をつけてください。

   .. Return value

   **返り値**

     Bulk replyが返ります。具体的には参照された要素が返ります。


.. command:: LSET key index value

   計算時間: O(N) （Nはリストの長さ）

   .. Set the list element at index (see LINDEX for information about the index argument) with the new value. Out of range indexes will generate an error. Note that setting the first or last elements of the list is O(1).
   
   キー ``key`` に対応するリスト内の指定されたインデックス ``index`` の要素を値を新しい値 ``value`` にします。（引数 ``index`` に関しては :com:`LINDEX` を見て下さい）範囲外のインデックスを指定した場合はエラーが起きます。リストの先頭および末尾の要素に値をセットする場合はO(1)です。

   .. Similarly to other list commands accepting indexes, the index can be negative to access elements starting from the end of the list. So -1 is the last element, -2 is the penultimate, and so forth.

   インデックスを指定する他のリスト操作系のコマンドと同様に、負のインデックスを指定した場合はリストの末尾からの値となります。-1の場合はリストの末尾、-2ならその前、となります。

   .. Return value

   **戻り値**

     Status code replyが返ります。


.. command:: LREM key count value

   計算時間: O(N) （Nはリストの長さ）

   .. Remove the first count occurrences of the value element from the list. If count is zero all the elements are removed. If count is negative elements are removed from tail to head, instead to go from head to tail that is the normal behaviour. So for example LREM with count -2 and hello as value to remove against the list (a,b,c,hello,x,hello,hello) will lave the list (a,b,c,hello,x). The number of removed elements is returned as an integer, see below for more information about the returned value. Note that non existing keys are considered like empty lists by LREM, so LREM against non existing keys will always return 0.

   キー ``key`` 対応するリスト内で値が ``value`` に等しいの最初の ``count`` 要素を削除します。もし ``count`` がゼロだった場合は該当するすべての要素が削除されます。もし ``count`` が負だった場合には、通常とは逆に要素はリストの末尾から先頭に向かって削除されます。例えば ``key`` に対応するリストが ``(a,b,c,hello,x,hello,hello)`` だったとして ``LREM key -2 hello`` を呼び出した場合には ``(a,b,c,hello,x)`` が残ります。削除された要素数が整数値として返ります。返り値に関する詳細は後述します。存在しないキーの場合はLREMは空リストに対して操作をした、と判断しますのでそういう場合は常に0が返ります。

   .. Return value
   
   **戻り値**

     Integer replyが返ります。具体的には::

       The number of removed elements if the operation succeeded


.. command:: LPOP key

.. command:: RPOP key
   
   計算時間: O(1)

   .. Atomically return and remove the first (LPOP) or last (RPOP) element of the list. For example if the list contains the elements "a","b","c" LPOP will return "a" and the list will become "b","c".

   キー ``key`` に対応するリストに対してアトミックに先頭 ( :com:`LPOP` )または末尾 ( :com:`RPOP` )の要素を返し、削除します。例えば "a","b","c"を含むリストに対して操作を行った場合は ``LPOP`` は"a"を返し、リストは"b","c"となります。

   .. If the key does not exist or the list is already empty the special value 'nil' is returned.

   もしキーが存在しない場合、あるいはリストがすでに空だった場合は特別な値 'nil' が返ります。

   .. Return value

   **返り値**

     Bulk replyが返ります。


.. command:: BLPOP key1 key2 ... keyN timeout 

   .. versionadded:: 1.3.1

.. command:: BRPOP key1 key2 ... keyN timeout 

   .. versionadded:: 1.3.1

   計算時間: O(1)

   .. BLPOP (and BRPOP) is a blocking list pop primitive. You can see this commands as blocking versions of LPOP and RPOP able to block if the specified keys don't exist or contain empty lists.

   :com:`BLPOP` （と :com:`BRPOP` ）はブロッキングなポップのプリミティブです。言い換えれば、 :com:`LPOP` と :com:`RPOP` のブロッキング版で、指定されたキーが存在しない場合や対応するリストが空でも使うことができるものだとも言えます。

   .. The following is a description of the exact semantic. We describe BLPOP but the two commands are identical, the only difference is that BLPOP pops the element from the left (head) of the list, and BRPOP pops from the right (tail).

   これより実際のセマンティクスについての説明をします。 :com:`BLPOP` についての説明しか書きませんが、 :com:`BRPOP` はただ先頭から操作するか末尾から操作するかの違いなので、基本的には同じです。

   .. Non blocking behavior

   **ノンブロッキングな動作**

   .. When BLPOP is called, if at least one of the specified keys contain a non empty list, an element is popped from the head of the list and returned to the caller together with the name of the key (BLPOP returns a two elements array, the first element is the key, the second the popped value).

   :com:`BLPOP` が呼び出されたとき、指定したキーのもし少なくとも一つが空でないリストを持っていた場合、そのリストの先頭の要素がポップされて、ポップされたリストに紐づいたキーとともに呼び出し元に返されます。（ :com:`BLPOP` は2つの要素の配列で、最初の要素はキー、2番目の要素はポップされた値となります）

   .. Keys are scanned from left to right, so for instance if you issue BLPOP list1 list2 list3 0 against a dataset where list1 does not exist but list2 and list3 contain non empty lists, BLPOP guarantees to return an element from the list stored at list2 (since it is the first non empty list starting from the left).

   キーは左から右にスキャンされます。たとえばlist1は存在しない、list2とlist3は空でないリストという状況だった場合には、 ``BLPOP list1 list2 list3 0`` を呼びだすと、list2から要素を取り出して返すことは保証されます。（なぜなら左から数えていってlist2が最初の空でないリストだからです）

   .. Blocking behavior

   **ブロッキングな動作**

   .. If none of the specified keys exist or contain non empty lists, BLPOP blocks until some other client performs a LPUSH or an RPUSH operation against one of the lists.

   指定したキーのどれもが存在しないあるいは空リストの場合には、 :com:`BLPOP` は他のクライアントが指定したリストのどれかに :com:`LPUSH` あるいは :com:`RPUSH` しない限りブロックします。

   .. Once new data is present on one of the lists, the client finally returns with the name of the key unblocking it and the popped value.

   リストのうちどれか一つにでも新しいデータが投入されれば、クライアントはようやくそのリストとひもづいているキーとポップされた値を返します。

   .. When blocking, if a non-zero timeout is specified, the client will unblock returning a nil special value if the specified amount of seconds passed without a push operation against at least one of the specified keys.

   ブロックしているときは、もしゼロでないタイムアウトが指定されていれば、クライアントはタイムアウトまでの間に少なくとも1つのリストにプッシュ操作がされなかった場合に、特別な値"nil"を返してブロックをやめます。

   .. The timeout argument is interpreted as an integer value. A timeout of zero means instead to block forever.

   タイムアウト用の引数 ``timeout`` は整数値として解釈されます。タイムアウト時間が0だった場合には制限なくブロックするようになります。

   .. Multiple clients blocking for the same keys

   **複数のクライアントによる同キーに対してのブロッキング**

   .. Multiple clients can block for the same key. They are put into a queue, so the first to be served will be the one that started to wait earlier, in a first-blpopping first-served fashion.

   複数のクライアントが同一キーに対してブロックすることが可能です。リクエストはキューに貯められるので、最初にそのキーに対して操作を行うことができるのは早くキューに並んだ順となります。

   blocking POP inside a MULTI/EXEC transaction

   **MULTI/EXECトランザクション内でのブロッキングなPOP**

   .. BLPOP and BRPOP can be used with pipelining (sending multiple commands and reading the replies in batch), but it does not make sense to use BLPOP or BRPOP inside a MULTI/EXEC block (a Redis transaction).

   :com:`BLPOP` と :com:`BRPOP` はパイプライン（１回のバッチで複数のコマンドを送信して、複数の返信を読み込む）に使えまが、 :com:`BLPOP` または :com:`BRPOP` を :com:`MULTI` / :com:`EXEC` ブロック（Redisトランザクション）内で使うのはあまり意味がありません。

   .. The behavior of BLPOP inside MULTI/EXEC when the list is empty is to return a multi-bulk nil reply, exactly what happens when the timeout is reached. If you like science fiction, think at it like if inside MULTI/EXEC the time will flow at infinite speed :)

   操作対象のリストが空の時に :com:`BLPOP` は :com:`MULTI` / :com:`EXEC` 内では風数のBulk nil replyを返す仕様になっています。まさにタイムアウトになった時に起きることと一緒です。もしSFが好きならば、 :com:`MULTI` / :com:`EXEC` の中では時間は無限の速さで流れていると考えてください。

   .. Return value

   **返り値**

   .. BLPOP returns a two-elements array via a multi bulk reply in order to return both the unblocking key and the popped value.

   :com:`BLPOP` はmulti bulk replyを経由してブロックしているキーとポップされた値のペアからなる配列を返します。

   .. When a non-zero timeout is specified, and the BLPOP operation timed out, the return value is a nil multi bulk reply. Most client values will return false or nil accordingly to the programming language used.

   もしタイムアウトにゼロでない値が指定されて、 :com:`BLPOP` の操作がタイムアウトしたときに、返り値はnil multi bulk replyとなります。たいていのクライアントでは使っているプログラミング言語に応じて ``false`` か ``nil`` を返すことになると思います。


.. command:: RPOPLPUSH srckey dstkey

   .. versionadded:: 1.1

   計算時間: O(1)

   .. Atomically return and remove the last (tail) element of the srckey list, and push the element as the first (head) element of the dstkey list. For example if the source list contains the elements "a","b","c" and the destination list contains the elements "foo","bar" after an RPOPLPUSH command the content of the two lists will be "a","b" and "c","foo","bar".

   キー ``srckey`` に対応するリストでアトミックに末尾の要素を削除して、その要素を ``dstkey`` に対応するリストの先頭にプッシュします。たとえば、ソースのリストが"a","b","c"でターゲットのリストが"foo","bar"だった場合に :com:`RPOPLPUSH` コマンドを実行すると２つのリストはそれぞれ "a","b" と "c","foo","bar"

   .. If the key does not exist or the list is already empty the special value 'nil' is returned. If the srckey and dstkey are the same the operation is equivalent to removing the last element from the list and pusing it as first element of the list, so it's a "list rotation" command.

   もしキーが存在しないまたはリストがすでに空だった場合には特別な値"nil"が返されます。もし ``srckey`` と ``dstkey`` が同じだった場合は、そのリストの末尾の要素を取り除いて、先頭に持ってくる操作となります。これは「リストローテーション」コマンドですね。

   .. Programming patterns: safe queues

   **プログラミングパターン： セーフキュー**

   .. Redis lists are often used as queues in order to exchange messages between different programs. A program can add a message performing an LPUSH operation against a Redis list (we call this program a Producer), while another program (that we call Consumer) can process the messages performing an RPOP command in order to start reading the messages from the oldest.

   Redisのリストはよく複数のプログラム缶でのメッセージキューとして用いられます。あるプログラム（プロデューサ）が :com:`LPUSH` によってRedisリストにメッセージを追加して、他のプログラム（コンシューマ）が :com:`RPOP` コマンドを使って古い順からメッセージを読み取るという処理を行ないます。

   .. Unfortunately if a Consumer crashes just after an RPOP operation the message gets lost. RPOPLPUSH solves this problem since the returned message is added to another "backup" list. The Consumer can later remove the message from the backup list using the LREM command when the message was correctly processed.

   もし残念なことにコンシューマが :com:`RPOP` の後にクラッシュしてしまった場合、メッセージはなくなってしまいます。 :com:`RPOPLPUSH` ならこの問題を解決できます。その理由は返されたメッセージは他の"バックアップ"リストに追加されるからです。コンシューマはメッセージがきちんと処理されたあとに :com:`LREM` コマンドを使ってバックアップリストから該当するメッセージを削除できます。

   .. Another process, called Helper, can monitor the "backup" list to check for timed out entries to repush against the main queue.

   ヘルパーと呼ばれる他のプロセスが"バックアップ"リストを監視してメインキューにタイムアウトした要素を再度プッシュすることもできます。

   .. Programming patterns: server-side O(N) list traversal

   **プログラミングパターン： サーバサイド O(N) リストトラバーサル***

   .. Using RPOPLPUSH with the same source and destination key a process can visit all the elements of an N-elements List in O(N) without to transfer the full list from the server to the client in a single LRANGE operation. Note that a process can traverse the list even while other processes are actively RPUSHing against the list, and still no element will be skipped.

   :com:`RPOPLPUSH` のソースとターゲットに同じキーを指定すると、N要素を持つリスト内のすべての要素をなめるとき、 :com:`LRANGE` の操作をするためにサーバからクライアントにO(N)でできます。ここで、そのリストを他のプロセスが :com:`RPUSH` している最中でさえも、すべての要素を漏らすことなくトラバースできることを知っておいてください。

   .. Return value
   
   **返り値**

     Bulk replyが返ります。


.. command:: SORT key [BY pattern] [LIMIT start count] [GET pattern] [ASC|DESC] [ALPHA] [STORE dstkey]

   Sort the elements contained in the List, Set, or Sorted Set value at key. By default sorting is numeric with elements being compared as double precision floating point numbers. This is the simplest form of SORT

   .. code-block:: none

      SORT mylist

   Assuming mylist contains a list of numbers, the return value will be the list of numbers ordered from the smallest to the biggest number. In order to get the sorting in reverse order use DESC:

   .. code-block:: none

      SORT mylist DESC

   The ASC option is also supported but it's the default so you don't really need it. If you want to sort lexicographically use ALPHA. Note that Redis is utf-8 aware assuming you set the right value for the LC_COLLATE environment variable.

   Sort is able to limit the number of returned elements using the LIMIT option:

   .. code-block:: none

      SORT mylist LIMIT 0 10

   In the above example SORT will return only 10 elements, starting from the first one (start is zero-based). Almost all the sort options can be mixed together. For example the command:

   .. code-block:: none

      SORT mylist LIMIT 0 10 ALPHA DESC

   Will sort mylist lexicographically, in descending order, returning only the first 10 elements.

   Sometimes you want to sort elements using external keys as weights to compare instead to compare the actual List Sets or Sorted Set elements. For example the list mylist may contain the elements 1, 2, 3, 4, that are just unique IDs of objects stored at object_1, object_2, object_3 and object_4, while the keys weight_1, weight_2, weight_3 and weight_4 can contain weights we want to use to sort our list of objects identifiers. We can use the following command:

   **Sorting by external keys**

   .. code-block:: none

      SORT mylist BY weight_*

   the **BY** option takes a pattern (weight_* in our example) that is used in order to generate the key names of the weights used for sorting. Weight key names are obtained substituting the first occurrence of * with the actual value of the elements on the list (1,2,3,4 in our example).

   Our previous example will return just the sorted IDs. Often it is needed to get the actual objects sorted (object_1, ..., object_4 in the example). We can do it with the following command:

   **Not Sorting at all**

   .. code-block:: none

      SORT mylist BY nosort

   also the BY option can take a "nosort" specifier. This is useful if you want to retrieve a external key (using GET, read below) but you don't want the sorting overhead.

   **Retrieving external keys**

   .. code-block:: none

      SORT mylist BY weight_* GET object_*

   Note that GET can be used multiple times in order to get more keys for every element of the original List, Set or Sorted Set sorted.

   Since Redis >= 1.1 it's possible to also GET the list elements itself using the special # pattern:

   .. code-block:: none

      SORT mylist BY weight_* GET object_* GET #

   **Storing the result of a SORT operation**

   By default SORT returns the sorted elements as its return value. Using the STORE option instead to return the elements SORT will store this elements as a Redis List in the specified key. An example:

   .. code-block:: none

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

     Multi bulk replyが返ります。具体的にはソートされたリストです。
