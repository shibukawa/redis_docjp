.. A case study: Design and implementation of a simple Twitter 
   clone using only the Redis key-value store as database and PHP

.. _tutorial:

==============
ケーススタディ
==============

.. note::

   英語の本家のページは、 `PHPを使って説明 <http://code.google.com/p/redis/wiki/TwitterAlikeExample>`_ 説明していますが、このページではPythonと `Tornado <http://tornado.shibu.jp>`_ を使ったチュートリアルに変えてあります。

   Bitbucketの `リポジトリ <https://bitbucket.org/shibu/redis_docjp/overview>`_ に、このチュートリアルのファイル一式が含まれています。 :file:`tutorial/retwis/` フォルダを自分の作業フォルダにおいて、 :file:`retwis_start.py` に、これから説明する内容を追加で実装していってください。なお、実力に自信のある方は、PHPやRubyの参考実装だけを見ながら、 :class:`RegisterHandler` や、 :class:`FollowHandler` クラスもPythonに移植してみてください。

   また、 @yssk22 氏がnode.js版を実装してくれました。これもリポジトリの中に入っていますので、興味のある方はこちらのファイルの内容に読み替えてください。

RedisとPythonを使ったシンプルなTwitterクローンの設計と実装
==========================================================

.. In this article I'll explain the design and the implementation of a 
   simple clone of Twitter written using PHP and Redis as only database. 
   The programming community uses to look at key-value stores like special 
   databases that can't be used as drop in replacement for a relational 
   database for the development of web applications. This article will 
   try to prove the contrary.

この記事では、PythonとRedisを使って、 `Twitterのシンプルなクローン <http://retwis.antirez.com/>`_ の設計と実装を紹介していきます。プログラミングのコミュニティの中には、キー・バリュー・ストアは、ウェブアプリケーションで使うリレーショナルデータベースの代わりには使えない、特殊なデータベースである、と見ている人もいますが、この記事の中で、それは間違いである、ということを証明します。

.. Our Twitter clone, called Retwis, is structurally simple, has very 
   good performances, and can be distributed among N web servers and 
   M Redis servers with very little efforts. You can find the source 
   code here.

このTwitterクローンの名前はRetwisといいます。構造的にシンプルで、パフォーマンスも悪くありませんし、少しの手間でN台のWebサーバとM台のRedisサーバを使った分散環境を構築することもできます。ソースコードは `ここ <http://bitbucket.org/shibu/redis_docjp/src/tip/tutorial/retwis-py/>`_ で手に入ります。

.. We use PHP for the example since it can be read by everybody. The same 
   (or... much better) results can be obtained using Ruby, Python, Erlang, 
   and so on.

.. News! Retwis-rb is a port of Retwis to Ruby and Sinatra written by 
   Daniel Lucraft! With full source code included of course, the git 
   repository is linked at the end of the Retwis-RB page. The rest of 
   this article targets PHP, but Ruby programmers can also check the 
   other source code, it conceptually very similar.

.. note::

   本家サイトのPHP版のほか、 `Ruby(Sinatra)版 <http://retwisrb.danlucraft.com/>`_ もあります。

.. Key-value stores basics

キー・バリュー・ストアの基本
----------------------------

.. The essence of a key-value store is the ability to store some data, 
   called value, inside a key. This data can later be retrieved only 
   if we know the exact key used to store it. There is no way to search 
   something by value. So for example I can use the command SET to store 
   the value bar at key foo:

キー・バリュー・ストアの本質は、キーに対して、値と呼ばれるどんなデータでも格納できるという点にあります。このデータは、保存時に使用した正確なキーを知っている場合にのみ、後からアクセスができます。値の側から検索する方法はありません。例えば、 :com:`SET` コマンドを使うと、 ``bar``という値を、 ``foo`` というキーに格納することができます。

.. code-block: none

   SET foo bar

.. Redis will store our data permanently, so we can later ask for 
   "What is the value stored at key foo?" and Redis will reply with bar:

Redisはデータを永続化して保持します。後で「 ``foo`` キーに保持されている値はなんですか？」と問い合わせると、Redisは ``bar`` と返事を返します。

.. code-block:: none

   GET foo => bar

.. Other common operations provided by key-value stores are DEL used 
   to delete a given key, and the associated value, SET-if-not-exists 
   (called SETNX on Redis) that sets a key only if it does not already 
   exist, and INCR that is able to atomically increment a number stored 
   at a given key:

他に、キー・バリュー・ストアで一般的に提供されている操作が、与えられたキーと関連する値を削除する :com:`DEL` と、「もし存在していなければセットする(SET-if-not-existes)」という操作(Redisでは :com:`SETNX`)と、与えられたキーに格納された値を自動でインクリメントする :com:`INCR` です。 

.. code-block:: none

   SET foo 10
   INCR foo => 11
   INCR foo => 12
   INCR foo => 13

.. Atomic operations

アトミックな操作
----------------

.. So far it should be pretty simple, but there is something special 
   about INCR. Think about this, why to provide such an operation if 
   we can do it ourself with a bit of code? After all it is as simple as:

これまでの説明はシンプルですが、 :com:`INCR` だけは少し特殊です。これを見ると、「なぜ、自分でも簡単に行えそうなこんなものが操作として提供されているのだろう？」と疑問に思うでしょう。この通り、これと同じ操作は簡単に実装できます。

.. code-block:: none

   x = GET foo
   x = x + 1
   SET foo x

.. The problem is that doing the increment this way will work as long as 
   there is only a client working with the value x at a time. See what 
   happens if two computers are accessing this data at the same time:

この方法でインクリメントしたときに、この値 ``x`` に操作を行うクライアントが一つしかない場合は問題なく動作します。2つのコンピュータが同時にこのデータにアクセスしに行った時に何が起きるか見てみましょう。

.. x = GET foo (yields 10)
   y = GET foo (yields 10)
   x = x + 1 (x is now 11)
   y = y + 1 (y is now 11)
   SET foo x (foo is now 11)
   SET foo y (foo is now 11)

.. code-block:: none

  x = GET foo (xは10)
  y = GET foo (yも10)
  x = x + 1 (xは11)
  y = y + 1 (yも11)
  SET foo x (fooは11になった)
  SET foo y (fooここでまた11が設定された)

.. Something is wrong with that! We incremented the value two times, but 
   instead to go from 10 to 12 our key holds 11. This is because the INCR 
   operation done with GET / increment / SET is not an atomic operation. 
   Instead the INCR provided by Redis, Memcached, ..., are atomic 
   implementations, the server will take care to protect the 
   get-increment-set for all the time needed to complete in order to 
   prevent simultaneous accesses.

何かおかしなことがおきています！2回インクリメントしたはずですので、10から12になってもいいのに、11です。これは自作の ``INCR`` 操作が、 :com:`GET` / インクリメント / :com:`SET` とアトミックな操作になっていません。RedisやMemcachedなどの提供する :com:`INCR` 操作はアトミックになっています。もし提供されていないとすると、取得して、演算して、格納する操作が終わるまでのすべてにわたって、同時アクセスを防ぐように気を配らなければなりません。

.. What makes Redis different from other key-value stores is that it provides
   more operations similar to INCR that can be used together to model complex
   problems. This is why you can use Redis to write whole web applications
   without using an SQL database and without to get mad.

Redisと他のキー・バリュー・ストアの大きな違いとなっているのは、Redisでは :com:`INCR` のように、複雑な問題に対して使えるような操作が数多く提供されているという点です。また、これがRedisを使うと、SQLのデータベースを使わなくても、誰も怒らないようなウェブアプリケーションを書くことができる秘訣です。

.. Beyond key-value stores

キー・バリュー・ストアの先の未来
--------------------------------

.. In this section we will see what Redis features we need to build our 
   Twitter clone. The first thing to know is that Redis values can be more
   than strings. Redis supports Lists and Sets as values, and there are 
   atomic operations to operate against this more advanced values so we 
   are safe even with multiple accesses against the same key. Let's start 
   from Lists:

このセクションでは、Twitterクローンをこれから作り上げていく上で必要となる、Redisの機能を紹介していきます。まず最初に知るべき事は、Redisの値が、単なる文字列以外にも持つことが可能である、ということです。Redisは値として、 :ref:`lists` と :ref:`sets` をサポートしています。 [#]_ 。また、これらの値を操作するためのアトミックな操作も多数用意しており、同じキーに対して安全に複数回アクセスできます。それではリストについて見て行きましょう。

.. LPUSH mylist a (now mylist holds one element list 'a')
   LPUSH mylist b (now mylist holds 'b,a')
   LPUSH mylist c (now mylist holds 'c,b,a')

.. code-block:: none

   LPUSH mylist a (mylistは、'a'という一つの要素を持つリスト)
   LPUSH mylist b (mylistは'b,a'を保持している)
   LPUSH mylist c (mylistは'c,b,a'を保持している)

.. rubric:: 脚注
.. [#] (訳注) これ以外にも、 :ref:`sortedsets` 、 :ref:`hashes` もサポートしていますが、今回は使いません。

.. LPUSH means Left Push, that is, add an element to the left (or to the 
   head) of the list stored at mylist. If the key mylist does not exist 
   it is automatically created by Redis as an empty list before the PUSH 
   operation. As you can imagine, there is also the RPUSH operation that 
   adds the element on the right of the list (on the tail).

:com:`LPUSH` は、「左にプッシュ」という意味です。これは ``mylist`` に対して、リストの左側(ヘッドとも呼ぶ)に要素を追加します。もし、 ``mylist`` というキーが存在していなかったとすると、Redisは :com:`LPUSH` の操作の前に自動的に空のリストを作ります。当然予想できると思いますが、 :com:`RPUSH` という操作もあります。これはリストの右側(テール)に要素を追加します。

.. This is very useful for our Twitter clone. Updates of users can be 
   stored into a list stored at username:updates for instance. There are 
   operations to get data or information from Lists of course. For instance 
   LRANGE returns a range of the list, or the whole list.

この操作はTwitterクローンを作る上でとても便利です。ユーザのステータス(ツイート)の更新は :samp:`{ユーザ名}:updates` という名前のリストに格納することができます。もちろん、リストからデータや情報を取得してくる操作もあります。 :com:`LRANGE` はリストの範囲、もしくは全体のデータを返します。

.. code-block:: none

   LRANGE mylist 0 1 => c,b

.. LRANGE uses zero-based indexes, that is the first element is 0, the 
   second 1, and so on. The command aguments are LRANGE key first-index 
   last-index. The last index argument can be negative, with a special 
   meaning: -1 is the last element of the list, -2 the penultimate, and 
   so on. So in order to get the whole list we can use:

:com:`LRANGE` はゼロスタートのインデックスで範囲を指定します。最初の要素のインデックスは0で、2番目が1になります。コマンドの引数は、 :samp:`LRANGE {キー} {最初のインデックス} {最後のインデックス}` です。最後のインデックスには、負の数値を指定することもできます。この場合、-1はリストの一番最後の要素の意味となります。-2はその前の要素です。そのため、リストの全要素を取得したい場合には次のように書きます。

.. code-block:: none

   LRANGE mylist 0 -1 => c,b,a

.. and LTRIM that is like LRANGE but instead of returning the specified range 
   trims the list, so it is like Get range from mylist, Set this range as new 
   value but atomic. We will use only this List operations, but make sure to 
   check the Redis documentation to discover all the List operations supported by Redis.

他の重要な操作としては、リストの長さを返す :com:`LLEN` と、 :com:`LRANGE` に似ていますが、リストの指定された範囲以外の要素を削除した上で、制定範囲の値を返す :com:`LTRIM` があります。 :com:`LTRIM` は、 ``mylist`` から範囲を :com:`GET` して、新しく残したい範囲を :com:`SET` する、といった操作をアトミックに行うことができます。このシステムではこの以上の操作しか使いませんが、ぜひRedisのドキュメントを読んで、リストに対する全ての操作を学ぶようにしてください。

.. The set data type

セットデータ型
--------------

.. There is more than Lists, Redis also supports Sets, that are unsorted collecti
   on of elements. It is possible to add, remove, and test for existence of members, 
   and perform intersection between different Sets. Of course it is possible to ask 
   for the list or the number of elements of a Set. Some example will make it more 
   clear. Keep in mind that SADD is the add to set operation, SREM is the remove 
   from set operation, sismember is the test if it is a member operation, and SINTER is 
   perform intersection operation. Other operations are SCARD that is used to get
   the cardinality (the number of elements) of a Set, and SMEMBERS that will return 
   all the members of a Set.

リスト以外にも、Redisは :ref:`sets` をサポートしています。これは要素をソートしないで格納するコレクションです。セットに対しては、要素の追加と削除、セットのメンバーの中に属しているかどうかのテスト、他のセットとの積集合の計算などができます。もちろん、セットの要素をリスト化したり、要素数を問い合わせることもできます。例を紹介すると、よく分かるでしょう。まず覚えておく操作は、セットに対して値を追加する :com:`SADD` 、セットに対する要素の削除を行う :com:`SREM` 、メンバーとして指定された値が格納されているかどうかのテストする :com:`SISMEMBER` 、積集合を取る :com:`SINTER` です。これ以外に、セットの要素数を数える :com:`SCARD` 、セットの全ての要素を返す :com:`SMEMBERS` という操作があります。

.. code-block:: none

   SADD myset a
   SADD myset b
   SADD myset foo
   SADD myset bar
   SCARD myset => 4
   SMEMBERS myset => bar,a,foo,b

.. Note that SMEMBERS does not return the elements in the same order we added them, since Sets are unsorted
   collections of elements. When you want to store the order it is better to use Lists instead. Some more 
   operations against Sets:

:com:`SMEMBERS` の返り値は要素を追加した順序になっていないことに注意してください。セットは要素の順序を保持しません [#]_ 。もし順序を保持したいのであれば、リストを使う方が良いでしょう。セットに対してはリストにはない操作がいくつかサポートされています。

.. rubric:: 脚注
.. [#] 順序を保持する :ref:`sortedset` もRedisはサポートしています。

.. code-block:: none

   SADD mynewset b
   SADD mynewset foo
   SADD mynewset hello
   SINTER myset mynewset => foo,b

.. SINTER can return the intersection between Sets but it is not limited to two sets, you may 
   ask for intersection of 4,5 or 10000 Sets. Finally let's check how SISMEMBER works:

:com:`SINTER` はセット間の積集合を算出する操作ですし、2つ以上のセットに対しても処理を行うことができます。4、5セットから10000以上のセットまでの積集合を算出することができます。最後に、 :com:`SISMEMBER` の動作について見て行きましょう。

.. code-block:: none

   SISMEMBER myset foo => 1
   SISMEMBER myset notamember => 0

.. Ok I think we are ready to start coding!

実装に必要なRedisの動作が一通り理解できたので、実装の準備ができました

.. Prerequisites

要件
----

.. If you didn't download it already please grab the source code of Retwis. It's a simple tar.gz 
   file with a few of .php files inside. The implementation is very simple. You will find the PHP 
   library client inside (redis.php) that is used to talk with the Redis server from PHP. This 
   library was written by Ludovico Magnocavallo and you are free to reuse this in your own 
   projects, but for updated version of the library please download the Redis distribution.

もしまだダウンロードしていないのであれば、まずはダウンロードしてください。その :file:`.tar.gz` ファイルの実装は、1つの :file:`.py` ファイルと、複数のテンプレートで行われています。実装はシンプルです。Redisと通信するのは、redis-pyというライブラリです。このライブラリは＊＊によって書かれており、自由に使えるライセンスになっています。これはプロジェクトには含まれていないので、最新のバージョンを落としてインストールしてください。

.. Another thing you probably want is a working Redis server. Just get the source, compile with 
   make, and run with ./redis-server and you are done. No configuration is required at all in 
   order to play with it or to run Retwis in your computer.

もう一つ準備として行うことは、Redisサーバを起動させることです。ソースコードをダウンロードしてきて :program:`make` コマンドを起動してコンパイルしてください。その後、 :file:`./redis-server` コマンドを起動すると、サーバを起動することができます。Redisで遊んだり、実行させる上では設定を行う必要はありません。 [#]_

.. rubric:: 脚注
.. [#] (訳注) Windowsであっても、cygwinを利用するとビルドすることができます。gccとGNU makeをインストールして、cygwinの中から :program:`make` を実行してください。

.. Data layout

データレイアウト
----------------

.. Working with a relational database this is the stage were the database layout should be produced 
   in form of tables, indexes, and so on. We don't have tables, so what should be designed? We need 
   to identify what keys are needed to represent our objects and what kind of values this keys need
   to hold.

リレーショナルデータベースを使ってプログラムを作る場合、この段階で、データベースのテーブル構造などを作っていくことになるでしょう。キー・バリュー・ストアでは何を設計すべきでしょうか？ここで必要になるのは、自分たちのオブジェクトを表現するには、どのようなキーを使っていくのか、ということと、このキーは、どのような値を保持しているのか？ということです。

.. Let's start from Users. We need to represent this users of course, with the username, userid, password, 
   followers and following users, and so on. The first question is, what should identify an user inside our 
   system? The username can be a good idea since it is unique, but it is also too big, and we want to stay 
   low on memory. So like if our DB was a relational one we can associate an unique ID to every user. 
   Every other reference to this user will be done by id. That's very simple to do, because we have our 
   atomic INCR operation! When we create a new user we can do something like this, assuming the user is 
   callled "antirez":

それでは、ユーザに関連する情報から決めていきます。ユーザ情報に関しては、ユーザ名、ユーザID、パスワード、フォローしている人、フォローされている人などの情報が必要となります。最初の疑問は、システム内ではどのようにユーザを識別すべきか、というものです。ユーザ名がユニークであれば、これはとても良いアイディアです。しかし、メモリの消費を低く抑えたいと思っているので、発言やフォロー情報にひもづけて大量に保存されることになるため、ユーザ名はサイズが大きすぎてしまいます。そのため、リレーショナルデータベースと同様に、ユニークなIDをユーザごとに設定していきます。このidを参照することで、ユーザに対する参照が全て行えるようになります。Redisでは、アトミックな :com:`INCR` 操作があるため、とても簡単に実装することができます。例えば、「antirez」というユーザを作る場合には、つぎのようにします。

.. code-block:: none

   INCR global:nextUserId => 1000
   SET uid:1000:username antirez
   SET uid:1000:password p1pp0

.. We use the global:nextUserId key in order to always get an unique ID for every new user. Then we 
   use this unique ID to populate all the other keys holding our user data. This is a Design Pattern 
   with key-values stores! Keep it in mind. Besides the fields already defined, we need some more stuff 
   in order to fully define an User. For example sometimes it can be useful to be able to get the user 
   ID from the username, so we set this key too:

新しいユーザにユニークなIDを設定するのに、このプログラムでは ``global:nextUserId`` キーを利用します。ユーザに関するすべてのデータには、このキーを持たせるようにします。これは、キー・バリュー・ストアに関するデザインパターンです。ぜひ覚えておきましょう。フィールドが定義できたら、ユーザを定義する上でもっと必要な要素を見て行きましょう。例えば、ユーザ名からユーザIDが求められると便利でしょう。

.. code-block:: none

   SET username:antirez:uid 1000

.. This may appear strange at first, but remember that we are only able to access data by key! 
   It's not possible to tell Redis to return the key that holds a specific value. This is also 
   our strength, this new paradigm is forcing us to organize the data so that everything is 
   accessible by primary key, speaking with relational DBs language.

最初は奇妙に見えると覆いますが、キー・バリュー・ストアでは、キーを使わないとデータにアクセスできません。Redisに、特定の値に関連するキーを返させることはできません。リレーショナルデータベースの言葉を使って語るのであれば、すべてプライマリーキーによってのみアクセスさせることを強要するという新しいパラダイムが、キー・バリュー・ストアの戦略です。

.. Following, followers and updates

フォローしている、フォローされている、アップデート
--------------------------------------------------

.. There is another central need in our system. Every user has followers users and 
   following users. We have a perfect data structure for this work! That is... Sets. 
   So let's add this two new fields to our schema:

もう一つ、ソースコードを読み込んでおくべき箇所があります。すべてのユーザは、「フォローしている」「フォローされている」ユーザのリストを持っています。Redisはこれにとても良いデータ構造をサポートしています。それは :ref:`sets` です。データスキーマに、この２つのフィールドを追加しましょう。

.. uid:1000:followers => Set of uids of all the followers users
.. uid:1000:following => Set of uids of all the following users

:samp:`uid:{ユーザID}:followers`
   フォローされているすべてのユーザのユーザIDを格納するセット

:samp:`uid:{ユーザID}:following`
   フォローしているすべてのユーザのユーザIDを格納するセット

.. Another important thing we need is a place were we can add the updates to 
   display in the user home page. We'll need to access this data in chronological 
   order later, from the most recent update to the older ones, so the perfect 
   kind of Value for this work is a List. Basically every new update will be 
   LPUSHed in the user updates key, and thanks to LRANGE we can implement 
   pagination and so on. Note that we use the words updates and posts 
   interchangeably, since updates are actually "little posts" in some way.

もう一つ重要な点は、ユーザのホームのページにつぶやきを表示する機能です。これは時間順で表示されるべきです。このような用途に最適なデータ構造は :ref:`lists` です。基本的にすべての新しいデータは、ユーザのつぶやき情報を格納するキーに対して、 :com:`LPUSH` で追加します。また、 :com:`LRANGE` を使うと、ページネーション(次のページ、などの処理)なども実装できます。なお、この記事では、つぶやき、アップデート、ポストなどは同じ意味に使っています。

.. uid:1000:posts => a List of post ids, every new post is LPUSHed here.

:samp:`uid:{ユーザID}:posts`
   ポストのIDのリスト。すべての新しいポストは :com:`LPUSH` で追加される。

.. Authentication

認証
----

.. Ok we have more or less everything about the user, but authentication. We'll 
   handle authentication in a simple but robust way: we don't want to use PHP 
   sessions or other things like this, our system must be ready in order to be
   distributed among different servers, so we'll take the whole state in our Redis
   database. So all we need is a random string to set as the cookie of an 
   authenticated user, and a key that will tell us what is the user ID of the client
   holding such a random string. We need two keys in order to make this thing
   working in a robust way:

ユーザに関して確認しておくべきことがもう少しだけあります。それは認証です。このアプリケーションの中では、シンプルでしっかりとした方法で認証を実装していきます。どのようなサーバに配置してもすぐ動作するようにしたいので、特定のDBやミドルウェアなどに依存するような方法は取るつもりはありません。そのため、ユーザに関する状態についても、すべてRedisサーバに格納させます。認証したユーザについて、ランダムな文字列をクッキーとして持たせます。このキーによって、クライアントのユーザIDを特定します。堅牢なしくみを動作させるために、次の2つのキーを作ります。

.. code-block:: none

   SET uid:1000:auth fea5e81ac8ca77622bed1c2132a021f9
   SET auth:fea5e81ac8ca77622bed1c2132a021f9 1000

.. In order to authenticate an user we'll do this simple work (login.php):

認証を行うために、ユーザが行わなければならないことはわずかです(:class:`retwis.LoginHandler`)。

.. * Get the username and password via the login form
   * Check if the username:<username>:uid key actually exists
   * If it exists we have the user id, (i.e. 1000)
   * Check if uid:1000:password matches, if not, error message
   * Ok authenticated! Set "fea5e81ac8ca77622bed1c2132a021f9" (the value of uid:1000:auth) 
     as "auth" cookie.

* ユーザ名とパスワードをログインフォームから取得する。
* :samp:`username:{ユーザ名}:uid` というキーが存在するか確認する。
* その結果得られたユーザID(例えば、1000)が存在するか確認する。
* :samp:`uid:{ユーザID}:password` とマッチするか確認し、マッチしなければエラーメッセージを返す。
* マッチすれば認証できています。 :samp:`uid:{ユーザID}:auth` の値である、 ``fea5e81ac8ca77622bed1c2132a021f9`` という文字列を ``auth`` というクッキーに格納します。

.. This is the actual code:

実際のコードは次の通りです。

.. literalinclude:: retwis-py/retwis.py
   :language: python
   :linenos:
   :pyobject: WelcomeHandler

.. This happens every time the users log in, but we also need a function isLoggedIn 
   in order to check if a given user is already authenticated or not. These are the 
   logical steps preformed by the isLoggedIn function:

このコードはユーザがログインを行うたびに実行されます。次に、Tornadoの ``@authenticated`` デコレータで、認証されているかどうかの確認を行えるようにしていきます。ログインチェックのロジックを順を追って説明していきます。

.. * Get the "auth" cookie from the user. If there is no cookie, the user is not 
     logged in, of course. Let's call the value of this cookie <authcookie>
   * Check if auth:<authcookie> exists, and what the value (the user id) is 
     (1000 in the exmple).
   * In order to be sure check that uid:1000:auth matches.
   * Ok the user is authenticated, and we loaded a bit of information in the 
     $User global variable.

* ``auth`` クッキーをユーザ情報から取得します。もしクッキーがなければ、このユーザはログインしていません。このクッキーの値を ``<authクッキー>`` と呼ぶことにします。
* もし、 :samp:`auth:{<authクッキー>}` が存在していれば、その値がユーザIDになります。
* :samp:`uid:{ユーザID}:auth` と一致していることを確認します。
* もしOKであれば、そのユーザは認証されています。 :meth:`get_current_user()` の返り値で ``None`` 以外を返すようにします。

.. The code is simpler than the description, possibly:

コードは次のようになっています。

.. literalinclude:: retwis-py/retwis.py
   :language: python
   :linenos:
   :pyobject: RedisAuthMixin

.. loadUserInfo as separated function is an overkill for our application, 
   but it's a good template for a complex application. The only thing it's missing 
   from all the authentication is the logout. What we do on logout? That's simple, 
   we'll just change the random string in uid:1000:auth, remove the old 
   auth:<oldauthstring> and add a new auth:<newauthstring>.

Tornadoの場合、ハンドラクラスの :meth:`get_current_user()` メソッドが ``None`` 以外の情報を返すと、そのユーザは認証されているとみなされ、 ``@authenticated`` を付けるだけで、認証が必要な処理である、ということを明示できます。ハンドラのコード内では、この情報は、 :attr:`current_user` プロパティ経由で取得するようにします(キャッシュされるので、get_current_user()を呼ぶよりも高速です)。このシステムでは大げさですが、ログインチェックと、ログイン情報の抽出は別のメソッドに分けるとコードが見やすくなります。

認証に関して残っているテーマはログアウトです。どのようにしてログアウトを実装すればいいでしょうか？それは簡単です。 :samp:`uid:{ユーザID}:auth` に設定するランダムな文字列を改変してしまえばいいのです。古い方の :samp:`auth:<古い認証文字列>` というキーを削除し、新しい :samp:`auth:<新しい認証文字列>` を追加します。

.. Important: the logout procedure explains why we don't just authenticate the user 
   after the lookup of auth:<randomstring>, but double check it against uid:1000:auth. 
   The true authentication string is the latter, the auth:<randomstring> is just an 
   authentication key that may even be volatile, or if there are bugs in the program 
   or a script gets interrupted we may even end with multiple auth:<something> keys 
   pointing to the same user id. The logout code is the following (logout.php):

.. note::

   ログイン処理では、ただ :samp:`auth:{<ランダム文字列>}` を見つけた後に、 :samp:`uid:<ユーザID>:auth` に対してダブルチェックを行っています。パスワードを確認する真の認証はその後に行っています。ランダムな文字列は100%確実に判別できるものではありませんが、もしプログラムなどにバグがあったり、プログラムの実行が中断した場合に、同じユーザを指す、 :samp:`auth:{<何か>}` キーが複数登録されてしまうかもしれません。次に、ログアウトのコードを示します。

.. literalinclude:: retwis-py/retwis.py
   :language: python
   :linenos:
   :pyobject: LogoutHandler

.. Updates

更新
----

.. Updates, also known as posts, are even simpler. In order to create a new post on 
   the database we do something like this:

ポストやツイートとも呼ばれますが、更新に関してはユーザ情報よりもシンプルです。新しいポストをデータベースに登録する場合は、次のようにします。

.. INCR global:nextPostId => 10343
   SET post:10343 "$owner_id|$time|I'm having fun with Retwis"

.. code-block:: none

   INCR global:nextPostId => 10343
   SET post:10343 "<発言者ID>|<時間>|Retwis楽しいよ!"

.. As you can se the user id and time of the post are stored directly inside the 
   string, we don't need to lookup by time or user id in the example application 
   so it is better to compact everything inside the post string.

この :com:`SET` の値にあるように、文字列の中に発言者のIDと時間をいれてしまっているため、このサンプルアプリケーション内では追加でこれらの情報を取得してくるのにDBにアクセスする必要はなくなるため、プログラムがコンパクトになります。

.. After we create a post we obtain the post id. We need to LPUSH this post id 
   in every user that's following the author of the post, and of course in the 
   list of posts of the author. This is the file update.php that shows how this 
   is performed:

ポストを行うと、ポストのIDが得られます。このIDを、発言者をフォローしている人全員に :com:`LPUSH` します。 :class:`PostHandler` を見ると、どのように行っているかを見ることができます。

.. literalinclude:: retwis-py/retwis.py
   :language: python
   :linenos:
   :pyobject: PostHandler

.. The core of the function is the foreach. We get using SMEMBERS all the followers 
   of the current user, then the loop will LPUSH the post against the 
   uid:<userid>:posts of every follower.

このクラスの重要な部分は、 ``for fid in followers`` というところです。 :com:`SMEMBERS` を使ってフォローされている全員を取得し、ループの中で :samp:`uid:{フォローしている人のID}:posts` に対して、 :com:`LPUSH` を使って格納していきます。

.. Note that we also maintain a timeline with all the posts. In order to do so what 
   is needed is just to LPUSH the post against global:timeline. Let's face it, do you 
   start thinking it was a bit strange to have to sort things added in chronological 
   order using ORDER BY with SQL? I think so indeed.

また、ここではすべてのポストを表示したタイムラインも作っています。ここでは、 ``global:timeline`` というキーに対して :com:`LPUSH` を使って格納するだけです。これを見ると、SQLでは、なぜ ``ORDER BY`` を使って時間順に文字列をソートしなければならないか不思議に思いませんか？私は思います。

.. Paginating updates

更新のページ処理
----------------

.. Now it should be pretty clear how we can user LRANGE in order to get ranges of 
   posts, and render this posts on the screen. The code is simple:

この処理は、 :com:`LRANGE` の使用方法に関する良いサンプルとなっています。ここでは、ポストされた内容の一部を取り出し、ブラウザにそれを表示していきます。コードはシンプルです。このコードは、複数箇所から参照されるため、クラスとして実装しています。その一部を表示します。

.. literalinclude:: retwis-py/retwis.py
   :language: python
   :linenos:
   :pyobject: PostFormatter.show_post

.. literalinclude:: retwis-py/retwis.py
   :language: python
   :linenos:
   :pyobject: PostFormatter.show_user_posts

.. showPost will simply convert and print a Post in HTML while showUserPosts get 
   range of posts passing them to showPosts.

:meth:`show_post` は単純に1つのポストをHTMLに整形する処理です。 :meth:`show_user_posts` は、表示する範囲のポストを取得してきて、 :meth:`show_post` に処理を投げます。

.. Following users

ユーザをフォローする
--------------------

.. If user id 1000 (antirez) wants to follow user id 1001 (pippo), we can do this 
   with just two SADD:

ユーザID 1000(antirez)が、ユーザDI 1001(pippo)をフォローしたい時の処理を実装していきます。ここでは、 :com:`SADD` を2回呼ぶことで行えます。

.. code-block:: none

   SADD uid:1000:following 1001
   SADD uid:1001:followers 1000

.. Note the same pattern again and again, in theory with a relational database 
   the list of following and followers is a single table with fields like following_id 
   and follower_id. With queries you can extract the followers or following of every user. 
   With a key-value DB that's a bit different as we need to set both the 1000 is 
   following 1001 and 1001 is followed by 1000 relations. This is the price to pay, 
   but on the other side accessing the data is simpler and ultra-fast. And having this 
   things as separated sets allows us to do interesting stuff, for example using SINTER 
   we can have the intersection of 'following' of two different users, so we may add a 
   feature to our Twitter clone so that it is able to say you at warp speed, when you 
   visit somebody' else profile, "you and foobar have 34 followers in common" and things 
   like that.

同じようなパターンは何度も出てくるでしょう。リレーショナルデータベースの流儀では、 ``following_id`` と ``follower_id`` の両方をフィールドに持つテーブルを1つ作って実装するでしょう。キー・バリュー型のデータベースの場合はこれとは異なり、 ``1000が1001をフォローしている`` という情報と、 ``1001が1000にフォローされている`` という2つの関係を両方ともセットに追加します。これはコストはかかりますが、データのアクセスもシンプルで、超高速です。また、それぞれのセットが独立して存在しているため、あなたの独自のTwitterクローンでは、 :com:`SINTER` を使って、誰かのプロフィールを見たときに「共通のフォロワーが34人います」といったことも実現できるでしょう。

.. You can find the code that sets or removes a following/follower relation at follow.php. 
   It is trivial as you can see.

:class:`FollowHandler` クラスを見ると、フォロワーの追加と削除のコードが書かれています。これはとてもシンプルなコードです。

.. Making it horizontally scalable

スケーラビリティを上げる
========================

.. Gentle reader, if you reached this point you are already an hero, thank you. 
   Before to talk about scaling horizontally it is worth to check the performances 
   on a single server. Retwis is amazingly fast, without any kind of cache. On a 
   very slow and loaded server, apache benchmark with 100 parallel clients issuing 
   100000 requests measured the average pageview to take 5 milliseconds. This means 
   you can serve millions of users every day with just a single Linux box, and this 
   one was monkey asses slow! Go figure with more recent hardware.

ここまで実装してきたあなたは既に英雄です。どうもありがとうございます。スケーリングについて話を巣る前に、単一のサーバのパフォーマンスをチェックすることが大切です。Retwisはキャッシュの類を使用しなくても、とても高速です。とても遅く、データがロード済みのサーバに対して、apache benchmarkを実行したところ、クライアントを100台並列させ、10万リクエストを投げたところ、ページビューの平均は5ミリ秒ほどでした。数百万人のユーザがいたとしても、1台のLinuxマシンでさばくことができるだろう、ということを意味しています。

.. So, first of all, probably you will not need more than one server for a lot of 
   applications, even when you have a lot of users. But let's assume we are 
   Twitter and need to handle a huge amount of traffic. What to do?

そのため、サーバを複数台に増やさなければならないアプリケーションというものは、例えユーザ数が多かったとしてもほとんどないでしょう。しかし、Twitterを想定すると、多くのトラフィックを処理しなければならないでしょう。どのように行えば良いでしょうか？


.. Hashing the key

キーのハッシュ化
----------------

.. The first thing to do is to hash the key and issue the request on different 
   servers based on the key hash. There are a lot of well known algorithms to do so,
   for example check the Redis Ruby library client that implements consistent hashing,
   but the general idea is that you can turn your key into a number, and than take
   the reminder of the division of this number by the number of servers you have:

最初に行うことは、キーのハッシュに従って別のサーバーで処理が行われるように設定することです。これを行うためのアルゴリズムは数多く知られていますが、RedisのRuby版のライブラリは、コンシステントハッシュを実装しています。一般的な方法としては、ハッシュを使ってキーを数値にして、これをサーバ数で割って余りを計算することで、どのサーバを利用するかを決めることができます。

.. server_id = crc32(key) % number_of_servers

.. code-block:: ruby

   server_id = crc32(キー) % サーバ数

.. This has a lot of problems since if you add one server you need to move too 
   much keys and so on, but this is the general idea even if you use a better 
   hashing scheme like consistent hashing.

しかし、この方法を使うと、1つサーバを追加しただけで、数多くのキーを移動しなければならないという問題があります。これは、コンシステントハッシュなどの良いハッシュアルゴリズムを使ったとしても、一般的に発生する問題です。

.. Ok, are key accesses distributed among the key space? Well, all the user data will 
   be partitioned among different servers. There are no inter-keys operations used 
   (like SINTER, otherwise you need to care that things you want to intersect will 
   end in the same server. This is why Redis unlike memcached does not force a specific
   hashing scheme, it's application specific). Btw there are keys that are accessed
   more frequently.

この場合、キーアクセスはキーの空間に分散するのでしょうか？この場合、すべてのユーザデータは複数のサーバの間に振り分けられて保存されます。使用されているキーをまたがる操作はありません。 :com:`SINTER` のようなものは同じサーバ内で行われるように注意する必要があります。これは、Redisがmemcachedと異なり、特定のハッシュを強制しないからです。)  これとは別に、より頻繁にアクセスされるキーもあります。

.. Special keys

特別なキー
----------

.. For example every time we post a new message, we need to increment the 
   global:nextPostId key. How to fix this problem? A Single server will get a lot 
   if increments. The simplest way to handle this is to have a dedicated server 
   just for increments. This is probably an overkill btw unless you have really 
   a lot of traffic. There is another trick. The ID does not really need to be 
   an incremental number, but just it needs to be unique. So you can get a random 
   string long enough to be unlikely (almost impossible, if it's md5-size) to collide,
   and you are done. We successfully eliminated our main problem to make it really
   horizontally scalable!

例えば、新しいメッセージをポストするたびに、この実装では ``global:nextPostId`` というキーをインクリメントしています。この問題を修正するにはどうすれば良いのでしょうか？サーバが一つであれば、インクリメントしていけば数多くのキーを生成することができますが、本当に多くのアクセスがなければ、これは過剰な品質です。IDをインクリメントしない、というトリックもあります。ユニークであれば、インクリメントしていく必要もありません。十分に長いランダムな文字列(md5のサイズがあればほぼ)衝突はしないでしょう。水平方向にスケーラブルにしていくための主な問題はこれで回避することができます。

.. There is another one: global:timeline. There is no fix for this, if you need
   to take something in order you can split among different servers and then
   merge when you need to get the data back, or take it ordered and use a single
   key. Again if you really have so much posts per second, you can use a single
   server just for this. Remember that with commodity hardware Redis is able to
   handle 100000 writes for second, that's enough even for Twitter, I guess.

別の問題としては、 ``global:timeline`` があります。これの修正方法はありません。複数のサーバに分けるのであれば、データを利用するタイミングで、マージを行って、順番に並び替え、一つのキーを使うようにする必要があります。繰り返しになりますが、相当多くのポストがある場合でも、一つのサーバで処理できます。一般的なハードウェアであっても、Redisは毎秒10万の書き込みを処理できますので、Twitterのようなサービスでも十分対応できると思います。