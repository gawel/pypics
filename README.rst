============
pypics
============

Host your pics in a git repository

pypics generate a static gallery from pictures stored in a git repository.

It use Ember.js_ and Galleria_

.. _ember.js: http://emberjs.com/
.. _galleria: http://galleria.io/

Installation
============

Server side::

  $ sudo aptitude install imagemagick
  $ wget https://raw.github.com/gawel/pypics/master/scripts/pics-init
  $ python pics-init a/PhotosAlbum

The ``PhotosAlbum`` directory must be served by your web server

Client side::

  $ sudo aptitude install exif # optionnal
  $ sudo aptitude install imagemagick # optionnal
  $ pip install git+git://github.com/gawel/pypics.git#egg=pypics


Usage
=====

Create an album and move some photos in it. You need to have a directories tree like this::

  - 2012
    - album1
  - 2013
    - album2
    - album3

Update metadata for the newly added pics::

  $ pics update

Set some metadata for the pics in you current directory::

  $ pics set title "My first album"
  $ pics addtag 2013

See the result::

  $ pics serve

Also check other commands::

  $ pics -h
