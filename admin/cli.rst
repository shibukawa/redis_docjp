.. _command_line_interface:

コマンドラインインタフェース
============================

.. For who it might help. The redis-cli command accepts commands 
   as parameters without need of type them interactively. Like:

:program:`redis-cli` コマンドは、Redisコマンドを引数として渡して、インタラクティブな操作なしでサーバに送信することができるようになっています:

.. code-block:: bash

   $ /path/to/redis/redis-cli ZINCRBY tagcloud 1 "redis is cool"

.. This is very useful to integrate redis-cli in maintenance tasks. 
   I do generate TXT files with one command per line and I launch 
   them all at once:. You can also pipe a file:

この機能のおかげで、 :program:`redis-cli` をメンテナンスのタスクに統合しやすくなっています。また、1行に1コマンドが書かれたテキストファイルを作成し、これを標準入力から流し込むことにより、一度ですべて実行することもできます:

.. code-block:: bash

   $ /path/to/redis/redis-cli < commands.txt
