.. -*- coding: utf-8 -*-

==============================
 パブリッシュ／サブスクライブ
==============================


.. command:: SUBSCRIBE channel_1 channel_2 ... channel_N

.. command:: UNSUBSCRIBE channel_1 channel_2 ... channel_N

.. command:: UNSUBSCRIBE (unsubscribe from all channels)

.. command:: PSUBSCRIBE pattern_1 pattern_2 ... pattern_N

.. command:: PUNSUBSCRIBE pattern_1 pattern_2 ... pattern_N

.. command:: PUNSUBSCRIBE (unsubscribe from all patterns)

.. command:: PUBLISH channel message

   .. versionadded:: 2.0.0

   .. Time complexity: subscribe is O(1), unsubscribe is O(N) where N is the number of clients already subscribed to a channel, publish is O(N+M) where N is the number of clients subscribed to the receiving channel, and M is the total number of subscribed patterns (by any client). Psubscribe is O(N) where N is the number of patterns the Psubscribing client is already subscribed to. Punsubscribe is O(N+M) where N is the number of patterns the Punsubscribing client is already subscribed and M is the number of total patterns subscribed in the system (by any client).

   計算時間: :com:`SUBSCRIBE` はO(1)、 :com:`UNSUBSCRIBE` はO(N)です。ここでNはすでにチャネルに接続しているクライアントの数です。 :com:`PUBLISH` はO(N+M)です。Nはチャネルをsubscribeしているクライアントの数で、Mはすべてのクライアントによるsubscribeのパターン数です。 :com:`PSUBSCRIBE` はO(N)です。NはすでにPSUBSCRIBEをしているクライアントのsubscribeのパターン数です。 :com:`PUNSUBSCRIBE` はO(N+M)です。NはPUBSUBSCRIBEをしているクライアントがすでにsubscribeしているパターン数で、Mはクライアントからシステムにsubscribeされているパターン数の合計です。

   .. SUBSCRIBE, UNSUBSCRIBE and PUBLISH commands implement the Publish/Subscribe messaging paradigm where (citing Wikipedia) senders (publishers) are not programmed to send their messages to specific receivers (subscribers). Rather, published messages are characterized into channels, without knowledge of what (if any) subscribers there may be. Subscribers express interest in one or more channels, and only receive messages that are of interest, without knowledge of what (if any) publishers there are. This decoupling of publishers and subscribers can allow for greater scalability and a more dynamic network topology.

   :com:`SUBSCRIBE` 、 :com:`UNSUBSCRIBE` と :com:`PUBLISH` はバブリッシュ／サブスクライブ・メッセージ・パラダイムです。sender(publisher)はメッセージを特定のreceiver(subscriber)に送信するのではなく、パブリッシュされたメッセージはチャネルに紐付けられます。このときどんなsubscriberがいるかは意識することはありません。subscriberは1つ以上のチャンネルを指定し、指定したチャンネルのメッセージのみ受信します。このpublisherとsubscriberのデカップリングはスケーラブルで動的なネットワークトポロジーを可能にします。

   .. For instance in order to subscribe to the channels foo and bar the client will issue the SUBSCRIBE command followed by the names of the channels.

   例えば、チャンネルfooとbarをsubscribeするためには、クライアントは :com:`SUBSCRIBE` コマンドをチャンネル名とともに発行します。

   .. code-block:: none

      SUBSCRIBE foo bar

   .. All the messages sent by other clients to this channels will be pushed by the Redis server to all the subscribed clients, in the form of a three elements bulk reply, where the first element is the message type, the second the originating channel, and the third argument the message payload.

   他のクライアントによるすべてのメッセージはRedisサーバによりsubscribeされているすべてのクライアントにプッシュされます。形式は3要素のBulk replyになります。最初の要素はメッセージの型、2番目はチャンネル、3番目はメッセージの中身です。

   .. A client subscribed to 1 or more channels should NOT issue other commands other than SUBSCRIBE and UNSUBSCRIBE, but can subscribe or unsubscribe to other channels dynamically.

   1つ以上のチャンネルを購読しているクライアントは :com:`SUBSCRIBE` と :com:`UNSUBSCRIBE` 以外のコマンドを発行するべきではありません。動的に他のチェンネルを subscribe や unsubscribe をすることは可能です。

   .. The reply of the SUBSCRIBE and UNSUBSCRIBE operations are sent in the form of messages, so that the client can just read a coherent stream of messages where the first element indicates the kind of message.

   :com:`SUBSCRIBE` と :com:`UNSUBSCRIBE` の返信は先に説明したメッセージの形で送信されます。クライアントは最初の要素がメッセージの種類を示しているので、それに基づいて一貫したストリームを読み取ることができます。

   .. **Format of pushed messages**

   **プッシュされたメッセージのフォーマット**

     .. Messages are in the form of multi bulk replies with three elements. The first element is the kind of message:

     メッセージは3要素のMulti bulk replyです。最初の要素はメッセージの種類です。

     .. * "subscribe": means that we successfully subscribed to the channel given as second element of the multi bulk reply. The third argument represents the number of channels we are currently subscribed to.

     * "subscribe" : これは無事に2番目の要素にあるチャンネルをsubscribeできたことを示しています。3番目の要素は現在subscribeしているチャンネル数を示しています。

     .. * "unsubscribe": means that we successfully unsubscribed from the channel given as second element of the multi bulk reply. The third argument represents the number of channels we are currently subscribed to. If this latest argument is zero, we are no longer subscribed to any channel, and the client can issue any kind of Redis command as we are outside the Pub/sub state.

     * "unsubscribe" : これは2番目の要素にあるチャンネルを無事にunsubscribeできたことを示しています。3番目の要素は現在subscribeしているチャンネル数を示しています。もし0になっていたらひとつもチャンネルを購読していないことを示しています。クライアントはパブリック／サブスクライブの状態からは外れているのでどんなRedisコマンドも発行できます。

     .. * "message": it is a message received as result of a PUBLISH command issued by another client. The second element is the name of the originating channel, and the third the actual message payload.

     * "message" : 他のクライアントによって発行された :com:`PUBLISH` コマンドの結果のメッセージです。2番目の要素はチャンネル名、3番目の要素はメッセージの中身です。

   .. **Unsubscribing from all the channels at once**

   **一度にすべてのチャンネルをunsubscribeする**

     .. If the UNSUBSCRIBE command is issued without additional arguments, it is equivalent to unsubscribing to all the channels we are currently subscribed. A message for every unsubscribed channel will be received.

     :com:`UNSUBSCRIBED` コマンドが引数なしで呼び出された場合、現在subscribeしているすべてのチャンネルをunsubscribeしたことになります。unsubscribeしたすべてのチャンネルにその旨のメッセージが送られます。

   .. **Wire protocol example**

   **ワイヤプロトコルの例**

   .. code-block:: none

      SUBSCRIBE first second
      *3
      $9
      subscribe
      $5
      first
      :1
      *3
      $9
      subscribe
      $6
      second
      :2

   .. at this point from another client we issue a PUBLISH operation against the channel named "second". This is what the first client receives:

   このとき他のクライアントからチャンネル "second" に対して :com:`PUBLISH` を発行します。次は最初のクライアントが受け取るものです。

   .. code-block:: none

      *3
      $7
      message
      $6
      second
      $5
      Hello

   .. Now the client unsubscribes itself from all the channels using the UNSUBSCRIBE command without additional arguments:

   次にクライアントは :com:`UNSUBSCRIBE` コマンドですべてのチャンネルからunsubscribeします。

   .. code-block:: none

      UNSUBSCRIBE
      *3
      $11
      unsubscribe
      $6
      second
      :1
      *3
      $11
      unsubscribe
      $5
      first
      :0

   .. **PSUBSCRIBE and PUNSUBSCRIBE: pattern matching subscriptions**

   **PSUBSCRIBEとPUNSUBSCRIBE: パターンマッチによるsubscribe**

     .. Redis Pub/Sub implementation supports pattern matching. Clients may subscribe to glob style patterns in order to receive all the messages sent to channel names matching a given pattern.

     Redisのパブリッシュ／サブスクライブの実装はパターンマッチもサポートしています。クライアントはglob形式のパターンを使って、パターンに該当するチャンネル名を持つ全てのメッセージを受信します。

     .. For instance the command:
     
     たとえばコマンドはこんな感じです。

     .. code-block:: none

       PSUBSCRIBE news.*

     .. Will receive all the messages sent to the channel news.art.figurative and news.music.jazz and so forth. All the glob style patterns as valid, so multiple wild cards are supported.

     この場合は ``news.art.figurative`` や ``news.music.jazz`` などといったチャンネルのすべてのメッセージを受信します。すべてのglob形式のパターンが有効です。複数のワイルドカードが対応しています。

     .. Messages received as a result of pattern matching are sent in a different format:

     パターンマッチの結果受け取ったメッセージは異なったフォーマットで送信されます。:

     .. * The type of the message is "pmessage": it is a message received as result of a PUBLISH command issued by another client, matching a pattern matching subscription. The second element is the original pattern matched, the third element is the name of the originating channel, and the last element the actual message payload.

     * メッセージタイプは "pmessage" です。他のクライアントによって :com:`PUBLISH` されたメッセージの受信結果です。2番目の要素は該当したパターン、3番目の要素はチャンネル名で、最後の要素は実際のメッセージの中身です。

     .. Similarly to SUBSCRIBE and UNSUBSCRIBE, PSUBSCRIBE and PUNSUBSCRIBE commands are acknowledged by the system sending a message of type "psubscribe" and "punsubscribe" using the same format as the "subscribe" and "unsubscribe" message format.

     :com:`SUBSCRIBE`, :com:`UNSUBSCRIBE`, :com:`PSUBSCRIBE`, :com:`PUNSUBSCRIBE` コマンドと同様に、メッセージタイプが"psubscribe"や"punsubscribe"のメッセージを送信しているシステムによって認識されています。そのシステムが送信しているメッセージの形式は"subscribe"や"unsubscribe"のものと同様です。

   .. **Messages matching both a pattern and a channel subscription**

   **パターンとチャンネル、両方のsubscribeに該当するメッセージ**

     .. A client may receive a single message multiple time if it's subscribed to multiple patterns matching a published message, or it is subscribed to both patterns and channels matching the message. Like in the following example:

     1つのメッセージに対して複数のパターンが該当する、あるいはパターンとチャンネル名両方がメッセージに該当する場合、クライアントはあるメッセージを複数回受信します。たとえば次ような例があります:

     .. code-block:: none

       SUBSCRIBE foo
       PSUBSCRIBE f*

     .. In the above example, if a message is sent to the foo channel, the client will receive two messages, one of type "message" and one of type "pmessage".

     上の例ではもしメッセージがfooチャンネルに送信され場合、クライアントは2つのメッセージを受け取ります。それぞれのメッセージタイプは"message"と"pmessage"になります。

   .. **The meaning of the count of subscriptions with pattern matching**

   **パターンマッチでsubscribe数を見る意味**

     .. In subscribe, unsubscribe, psubscribe and punsubscribe message types, the last argument is the count of subscriptions still active. This number is actually the total number of channels and patterns the client is still subscribed to. So the client will exit the Pub/Sub state only when this count will drop to zero as a result of unsubscription from all the channels and patterns.

     "subscribe", "unsubscribe", "psubscribe", "punsubscribe"のメッセージタイプでは、最後の要素は購読中のチャンネル数になっています。この数はクライアントがその時点でsubscribeしているチャンネルとパターンの合計です。クライアントは、すべてのチャンネルとパターンをunsubscribeした結果、この数が0になった時にだけパブリック／サブスクライブの状態を抜けることができます。

   .. **More details on the PUBLISH command**

   **PUBLISHコマンドの詳細**

     .. The Publish command is a bulk command where the first argument is the target class, and the second argument the data to send. It returns an Integer Reply representing the number of clients that received the message (that is, the number of clients that were listening for this class).

     :com:`PUBLISH` コマンドはbulkコマンドです。最初の引数がターゲットクラスで2番目の引数が送信されるデータです。呼び出すとInteger replyが返ってきます。値はメッセージを受け取ったクライアント数です。（つまりこのクラスを監視しているクライアント数です）

   .. **Programming Example**

   **プログラミング例**

     .. Pieter Noordhuis provided a great example using Event-machine and Redis to create a multi user high performance web chat, with source code included of course!

     Pieter Noordhuisが素晴らしいサンプルとして、Event-machineとRedisを使って複数ユーザのハイパフォーマンスWebチャットを作りました。ソースコードももちろん公開されています。

   .. **Client library implementations hints**

   **クライアントライブラリの実装のためのヒント**

     .. Because all the messages received contain the original subscription causing the message delivery (the channel in the case of "message" type, and the original pattern in the case of "pmessage" type) clinet libraries may bind the original subscription to callbacks (that can be anonymous functions, blocks, function pointers, and so forth), using an hash table.

     受信したすべてのメッセージにはメッセージの配信のきっかけとなった元々のsubscriptionを持っているので（"message"であればチャンネル名、"pmessage"であればパターン）、クライアントライブラリは元々のsubscriptionとコールバックをハッシュ表を使ってひもづけることができます。（コールバック先は関数、ブロック、ポインタなどなんでもかまいません）

     .. When a message is received an O(1) lookup can be done in order to deliver the message to the registered callback.

     メッセージが受け取られたときには、メッセージを登録したコールバックに配信するために、O(1)の参照が行われます。
