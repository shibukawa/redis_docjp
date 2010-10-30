========
接続処理
========

.. command:: QUIT

   .. Ask the server to silently close the connection.

   サーバに対して、コネクションを静かにクローズするように依頼します。

   .. Return value

   返り値
   
     .. None. The connection is closed as soon as the QUIT command is received.

     なし。QUITコマンドが受信されると、即座にコネクションがクローズされます。

.. command:: AUTH password

   .. Request for authentication in a password protected Redis server. 
      A Redis server can be instructed to require a password before to 
      allow clients to issue commands. This is done using the requirepass 
      directive in the Redis configuration file.

   パスワードで保護されたRedisサーバへの認証のリクエストを行います。Redisサーバに対して、クライアントからコマンドを受け付ける前に、パスワードを必要とするように設定できます。この設定を行うには、Redisの設定ファイルの :conf:`requirepass` ディレクティブを使用します。

   .. If the password given by the client is correct the server replies 
      with an OK status code reply and starts accepting commands from the 
      client. Otherwise an error is returned and the clients needs to try 
      a new password. Note that for the high performance nature of Redis 
      it is possible to try a lot of passwords in parallel in very short 
      time, so make sure to generate a strong and very long password so 
      that this attack is infeasible.

   クライアントから与えられたパスワードが正しければ、サーバはOKというステータスコードを返し、クライアントからのコマンドを許可するようになります。正しくない場合にはエラーが返され、クライアントは新しいパスワードを送信しなければなりません。Redisは高性能であるが故に、攻撃側からのパスワードのリクエストも短期間に大量に処理できてしまうため、攻撃されないように、なるべく長く、強いパスワードを使うようにしてください。

   .. Return value

   返り値

      .. Status code reply

      :ref:`status_code_reply`