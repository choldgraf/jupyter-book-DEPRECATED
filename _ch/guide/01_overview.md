---
title: 'Overview'
permalink: '/ch/guide/01_overview'
prev_page:
  url: /ch/guide/00_intro
  title: 'Deployment Guide'
next_page:
  url: /ch/guide/02_setup
  title: 'Setup and Install'
comment: "***PROGRAMMATICALLY GENERATED, DO NOT EDIT. SEE FILES IN /NOTEBOOKS***"
---
# The Jupyter Books Guide

This repository / website is a guide for hosting your own book using
Jekyll and Jupyter Notebooks. All course content is written in markdown and
Jupyter Notebooks, and a set of helper scripts converts these notebooks into
Jekyll-based markdown fit for hosting on the web. This short guide will
help you through the process should you want to do this for your own book.

## The structure underneath Jupyter Books

This page gives a general idea for what we mean by a "Jupyter Book". Jupyter Books
are essentially these things:

1. [**A collection of notebooks and markdown files**](https://github.com/choldgraf/jupyter-book/tree/master/notebooks). These are in `notebooks/`. When you run `scripts/generate_book.py`,
   they'll be converted to `.md` files (or just copied if they're already `.md` files) and placed in `/ch`.
Here's a page with a bunch of code that can be used
to demonstrate how the highlighting looks.
2. [**A Table of Contents file**](https://github.com/choldgraf/jupyter-book/tree/master/_data/toc.yml) (`_data/toc.yml`). This is
   the Table of Contents, which will be used to create the sidebar for your site. Links in this file point to the **output directory**
   of `scripts/generate_book.py`. Be default, this is `_ch`. You can choose whatever structure you like - see the TOC for this template
   for a couple of examples.
3. [**Supporting markdown files**](https://github.com/choldgraf/jupyter-book/blob/master/index.md) (such as this one). Because
   Jupyter Book is built on top of Jekyll, you can include any extra markdown files with Jekyll yaml headers. As long as you link these
   in the `toc.yml` file, they'll show up in the sidebar and are viewable by users.

## The build process

The build process in general goes something like this (we'll go into each
step in more detail in this guide):

* Get yourself a copy of the template repository. [Here's the repo URL on GitHub](https://github.com/choldgraf/jupyter-book).
* Put your Jupyter Notebooks in `notebooks/` (they can be in sub-folders)
* Edit the `_data/toc.yml` file for your Table of Contents. This defines the structure
  of your textbook. The location of URLs should be the *destination* of your notebooks (e.g., `/ch/myfolder/mynotebook`)
* Navigate to the repo root, then run `make book` to convert your Jupyter Notebooks into Jekyll-ready markdown.
* Push these changes to GitHub.
* Tell GitHub you want to build a website from your fork of the repository.
* That's it!

For a more complete description of the relevant files for the template repository,
see the [Advanced topics section](../07_advanced).

See the rest of this guide in the links to the left for detailed
instructions on this process. The next section covers [Setting up your environment](../02_setup).
