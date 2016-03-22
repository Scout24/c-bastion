====================================================
`c-bastion` -- Cloud Bastion Host (a.k.a. jump-host)
====================================================

.. image:: https://travis-ci.org/ImmobilienScout24/c-bastion.svg?branch=master
   :target: https://travis-ci.org/ImmobilienScout24/c-bastion

About
=====

``c-bastion`` allows you to create users in a docker container via a CLI tool
and then log in with these formerly created users. The CLI tool is called
``cbas`` and can be found at:

https://github.com/immobilienscout24/cbas

The purpose of this project is to provide an EC2 instance with a Docker
container that can be used as a jump-host with dynamically created user. After
creation, the user is able to log in into the Docker container by using his/her
given SSH key.

The basic flow is as follows::

    +-----------------+  +-----------------+  +-----------------+
    |                 |  |                 |  |                 |
    |    developer    |  |    jump host    |  |   auth server   |
    |                 |  |                 |  |                 |
    +--------+--------+  +--------+--------+  +--------+--------+
             |                    |                    |
             +----------------------------------------->
             | request token      |                    |
             <-----------------------------------------+
             | receive token      |                    |
             |                    |                    |
             +-------------------->                    |
             | upload key         +-------------------->
             |                    | validate token     |
             |                    <--------------------+
             <--------------------+                    |
             | upload OK          |                    |
             |                    |                    |
             +-------------------->                    |
             | ssh log in         |                    |
             |                    |                    |
             |                    |                    |
             |                    |                    |
             +                    +                    +

Where ``developer`` is your local machine (desktop, laptop, etc..) ``auth
server`` is the auth-server and ``jump host`` is the jump host. ``cbas`` takes
care of obtaining the token and uploading the ssh-key.

Features
========

The bastion host is a slim Ubuntu and contains the following extra features:

* `vim-nox`_
* `screen`_ and `tmux`_
* `zsh`_
* python with `pip`_ and `virtualenv`_
* Import `your Personal Environment via SSH`__

.. __: http://blog.schlomo.schapiro.org/2014/02/ssh-with-personal-environment.html

.. _vim-nox: http://packages.ubuntu.com/trusty/vim-nox
.. _screen: http://packages.ubuntu.com/trusty/screen
.. _tmux: http://packages.ubuntu.com/trusty/tmux
.. _zsh: http://packages.ubuntu.com/trusty/zsh
.. _pip: http://packages.ubuntu.com/trusty/python-pip
.. _python-virtualenv: http://packages.ubuntu.com/trusty/python-virtualenv


Architecture
============

The main server-code is written Python and everything is packaged as a Docker
container. Inside the Docker container we use
`Supervisor <http://supervisord.org/>`_ to run multiple processes. You may
inspect the file ``supervisord.conf`` to see the how it has been configured
(and where the log files are).

Configuration
=============

To run the jump-host you will need a so called auth-server that can provide
`OpenID Connect <http://openid.net/connect/>`_
`Json Web Tokens <http://jwt.io/>`_. To configure this server, please supply
the URL via an environment variable called ``AUTH_URL``. Note, that is
configured as a full url *including* the protocol and *without* a trailing
slash, e.g. ``http://auth-server.example``.

Docker Image Availability
=========================

The project is built with continuous integration on `Travis CI
<https://travis-ci.org/>`_.  This tests the server code, builds the Docker
image and uploads it to `Docker Hub <https://hub.docker.com/>`_ via Travis.
Hence you may obtain the Docker image from our organization on Docker Hub:

https://hub.docker.com/r/immobilienscout24/c-bastion/


Deployment
==========

Personally, we use `AWS CloudFormation
<https://aws.amazon.com/de/cloudformation/>`_ in conjunction with `(our own
custom version of ) Stups Taupage
<http://stups.readthedocs.org/en/latest/components/taupage.html>`_ to deploy.
Your milage may vary. Unfortuntaley the templates we use contain private
configuartion so we are unable to make those available to the public.

API
===

There are a total of three endpoints:

:``status``: Check if the server is up and running.
:``create``: Upload ssh-key-file and create user.
:``delete``: Delete the user again.
:``version``: Report the version as JSON.

Note however, that the preferred way to interact with the server is ``cbas``.

Local Testing
=============

Pull the image from Docker Hub:

.. code-block::

    $ docker pull immobilienscout24/c-bastion

You can then launch the Docker image using, note how the ``AUTH_URL`` is
supplied:

.. code-block::

    $ docker run -p 127.0.0.1:8080:8080 -e AUTH_URL=http://auth-server.example immobilienscout24/c-bastion:latest

And finally, check that the container has started and that the jump-host server
has come up:

.. code-block::

   $ curl http://127.0.0.1:8080/status
   OK

You could also check the current version:

.. code-block::

   $ curl http://127.0.0.1:8080/version
   {'version': '53'}

Development
===========

The project is written in Python 2.7 and uses PyBuilder and GNU-Make as build and test tool. GNU-Make is
used in addition to PyBuilder since this project is basically some Python code
and some Docker logic so more than *just* PyBuilder was needed. The
build-system is cobbled together and somewhat flakey, so a few tips and tricks
follow.

#. You should always build and test within a virtual-environment, that contains
   an up-to-date `pip` and `pybuilder`:

   .. code-block::

       $ virtualenv venv
       $ source venv/bin/activate
       (venv) $ pip install -U pip
       (venv) $ pip install pybuilder
       (venv) $ pyb install_dependencies

#. To run just the unit-tests, static code analysis and coverage reporting:

   .. code-block::

       (venv) $ pyb
       ...

#. To build the Docker image:

   .. code-block::

       (venv) $ make build

#. To system-test the Docker image:

   .. code-block::

       (venv) $ make system-test

#. To build and run all available tests, simply type:

   .. code-block::

       (venv) $ make

The makefile also has some other convenience targets, please familiarise
yourself with it.

License
=======

Copyright 2016 Immobilien Scout GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
