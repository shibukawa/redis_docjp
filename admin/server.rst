サーバプログラム
================

.. The redis.conf file included in the source code distribution is a 
   starting point, you should be able to modify it in order do adapt 
   it to your needs without troubles reading the comments inside the file.

ソースコードの配布物に含まれている :file:`redis.conf` ファイルは、設定ファイルを作成する場合の良い出発点になるでしょう。このファイル内のコメントを読んで設定することで、トラブルに悩まされることなく自分のニーズに合わせることができるようになるでしょう。

.. In order to start Redis using a configuration file just pass the 
   file name as the sole argument when starting the server:

設定ファイルを用いてRedisを起動するには、単に設定ファイルのパスを引数に渡して起動するだけで大丈夫です。

.. code-block:: bash

   $ ./redis-server redis.conf
