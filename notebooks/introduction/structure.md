# The structure underneath Jupyter Books

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

For more information about the structure / composition of this site, see [the Jupyter Books Guide](http://predictablynoisy.com/jupyter-book-guide/).