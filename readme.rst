show-my-ip
==========

There is no ``ifconfig`` in Cygwin,
so I wrote a little Python script to parse the result of ``ipconfig`` to get the name of NIC cards and their IP addresses.

The encoding of ``ipconfig`` is ``CP950``, I decoded it and encode it again with ``UTF-8``.

The function in the script returns a dictionary, with key as name and value as IP address.

20140501 update
---------------

Add ``ifconfig`` support to this program.

When tried upgrade to Python3 (still Python2 compatiable),
I found ``subprocess`` module in Python3 has some problem in UTF-8 environment,
so this program is not support in Cygwin+Python3.

20140806 update
---------------

After 5 months in school without going home, I finally request for a 7-day-long vacation to my boss.
Now I'm on the train to Hualien, yeeeeaaaaahhhh!

Few weeks ago I found that, just like many other commands, ``ifconfig`` has FreeBSD and GNU versions, my program does not support GNU version yet.

So I rewrite the program to extract more information of network interfaces, also add support to GNU ``ifconfig``.

Instead of using regex, I use a for loop to parse the ``ifconfig`` and ``ipconfig`` output line by line.

I found a ``codecs`` module in Python3, it solved my encoding problem in Python3.

Still working.
