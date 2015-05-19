============
pypics
============

pypics generate a static gallery from pictures stored in a git repository.

Installation
============

::

  $ sudo aptitude install imagemagick exif jhead
  $ pip install -e git+git://github.com/gawel/pypics.git#egg=pypics

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
