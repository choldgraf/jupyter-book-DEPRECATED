---
title: 'Build your book'
permalink: '/ch/guide/04_build'
prev_page:
  url: /ch/guide/03_configure
  title: 'Configuration'
next_page:
  url: /ch/guide/05_publish
  title: 'Publish your book'
comment: "***PROGRAMMATICALLY GENERATED, DO NOT EDIT. SEE FILES IN /NOTEBOOKS***"
---
To build your site, take the following steps.:

0. (optionally) clean out the auto-generated folders with the helper script

       python scripts/clean.py

   or by running

       make clean

1. Ensure that your Table of Contents file (`_data/toc.yml`) is up to date. The links in
   that file should point to the **location of your built book** inside `ch/`
   and **relative to the site's root**. See the template `toc.yml` for examples.
2. Build the textbook by navigating to the site root, and running the following command:

       make book

This will:

* Run `nbconvert` to turn the `.ipynb` files into markdown
* Replace relative image file paths with a `{{ site.baseurl }}` base for Jekyll
* Clean up formatting issues for displaying properly
* Place all these generated files in the `_ch/` directory.

You can the push the changes to GitHub, which will automatically build a Jekyll site with
your newly-created Markdown files. We'll cover this next.
