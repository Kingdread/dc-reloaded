Installation
============

DC reloaded ships with a ``setup.py``, allowing a comfortable installation. The
program should work on any platform that supports Python and PyQt, which
includes Linux, Windows and Mac.

Installing the requirements
---------------------------

DC reloaded depends on merely two things:

* `Python 3`_
* `PyQt 5`_

You should head to the project's homepage to get more instructions for your
platform. Alternatively (if you are using Linux) you can consult your
distributions manual, for example Arch Linux has Python in its
repositories. Thus, on Arch, you can install Python with::

    sudo pacman -S python

Once you have made sure that every requirement is installed, you can proceed to
install DC reloaded itself.
    
.. _Python 3: https://www.python.org/
.. _PyQt 5: http://www.riverbankcomputing.co.uk/software/pyqt/intro

Installing DC reloaded system wide (Linux)
------------------------------------------

This is probably the easiest method, but also the one that could fuck up your
system the most. It will put the library into the global Python library path
and the start script into ``/usr/bin``.

The downside to this approach is that it might introduce dependency issues,
though the only dependency DC reloaded has is PyQt, so you should be
fine. Still, you might run into problems if other projects have a module called
``dc``, which will interfere with this one.

The best practice therefore is to install it using virtual envs (see below),
but since DC reloaded has such few requirements, it's probably okay to install
it system wide (don't hang me please).

In order to install DC reloaded you simply have to navigate to the source
folder, e.g.::

    $ git clone https://github.com/Kingdread/dc-reloaded.git
    $ cd dc-reloaded

and then run::

    $ sudo python3 setup.py install

DC reloaded can then be started by typing::

    $ dc-reloaded

Installation in a virtual env (Linux)
-------------------------------------

A `virtual env`_ provides a way to keep dependencies of a program bundled
together and seperate of the global python installation or other virtual
environments. Installing DC reloaded in such an environment is straightforward
and prefered over the system wide installation if you want to keep your global
libraries clean.

I recommend reading the docs and taking a look at `virtualenvwrapper`_ if you
want a more comfortable interface to virtual environments.

First, we need to create the virtual environment in which we will install our
environment (assuming you have your virtual envs at ``~/.PyEnvs/``)::

    $ cd ~/.PyEnvs
    $ virtualenv -p /usr/bin/python3 dc_reloaded

Next, we need to copy the modules ``PyQt5`` and ``sip`` into our virtual env::

    $ cp -r /usr/lib/python3.4/site-packages/PyQt5 dc_reloaded/lib/python3.4/site-packages
    $ cp /usr/lib/python3.4/site-packages/sip.so dc_reloaded/lib/python3.4/site-packages

.. note::

   You need to specify your version of Python (e.g. python3.3) if you are
   using a different version than 3.4

Now we need to install DC reloaded::

    $ cd ~/src/
    $ git clone https://github.com/Kingdread/dc-reloaded.git
    $ cd dc-reloaded
    $ source ~/.PyEnvs/dc_reloaded/bin/activate
    $ python setup.py install

The ``source ...`` command will activate the virtual environment and the last
command will finally install DC reloaded. You can leave the virtual env by
using::

    $ deactivate

To start DC reloaded, you need to first activate the virtual env and then run
``dc-reloaded``::

    $ source ~/.PyEnvs/dc_reloaded/bin/activate
    $ dc-reloaded

You can automate this commands by using a small shell script:

.. code-block:: bash

    #!/usr/bin/sh
    source ~/.PyEnvs/dc_reloaded/bin/activate
    dc-reloaded

.. _virtual env: https://virtualenv.pypa.io/en/latest/
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/
