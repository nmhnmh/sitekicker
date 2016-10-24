**SiteKicker** is yet another static site builder written in python3(python2 is not supported).
It is inspired by many other well-known site generators like [Jekyll](http://jekyllrb.com/).

Current Status: **Under Active Development**

## Todos

- [] site status reporter
- [] cached rebuild
- [] support pages
- [] Add unittest
- [] sitemap
- [] feed
- [] toc
- [] reStructuredText
- [] latex
- [] pandoc
- [] site link checker

## Features

- Built-in supports for common tools and services(code highlight, math formulas, siteamp, feed, toc and more), works out-of-box
- Useful for both blogs and websites
- Local live preview with real-time directory watch and incremental build
- Support multiple formats like markdown, reStructuredText, latex etc
- compile with external compilers of your choice, **pandoc** for example
- Flexible to generate sites for various purposes(blog, static site, product documentation etc)
- Built-in support for image compression and watermark
- Site link monitor, find broken links easily
- Works only with **Python3**

## Recommended Directory structure
```
```

## site.yml
```yml
# Name of the site, optional
name: An Awesome Site
# Base URL for the site, will be used to generate absolute urls, optional
base: https://example.org
# Generate absolute urls for all links, if set, base url must be set, default no, optional
absolute_urls: no
# Directory where build output will be saved, could be relative path or absolute path
output_dir: .dist
# Directory that contains layout/templates, default: layout, optional
layout_dir: layout
# Directories that will be copied, such as folders with assets or binary files
copy_dirs:
  - assets
# Options for site images processing
image_options:
  watermark:
    - text: '@niminghao'
      position: left top
      transparency: 90%
    - image: logo.png
      position: right bottom
      transparency: 90%
  resize:
    max-width: 3000px
    max-height: 3000px
  quantity: 90%
# Directories that will be process, if not set, will process all directories
# if set, will only process directories listed, optional
content_dirs:
  - pages
  - movies
  - books
  - posts
  - projects
```

## meta.yml
```yml
# The options set in this file will be applied to all entries inside the folder where this file is found,
# we refer to these entries as 'affected items of this file' below.
# This is a good place to set some common options and flags.
# You could also add any custom options below, prefix and tags are special because they has special meaning

# The prefix will be prepend to all items affected by this file, 'article.html' will be 'abc/article.html'
# if multiple prefix specified along the way, they will be contatenated and prefixed to the final url,
# so if two prefix 'a' and 'b' specified, then the final url will be '/a/b/article.html'
prefix: abc
# The tags listed here will be added to all items affected by this file, tags specified at different places
# will be merged, duplicate tags will be removed, original order of tags will be maintained
tags:
  - global tag 1
  - global tag 2
```

## Entry Front Matter
```yml
# In this file your specified options for the entry, beside some predefined ones like 'id', 'title', 'date'
# you can add your own custom options, and use it inside your templates, options specified here will override
# options specified in meta.yml in parent folder, except 'prefix' and 'tags', the former will be concatenated,
# the later will be merged

# A unique id to identify the entry, no special chars, space will be substitued with hyphens, mandatory
id: some-thing-as-name
# Title of the entry
title: Sitekicker is another Static Site Generator
# Date of the writting
date: 2016-10-20
# Tags that applies to this entry, optional
tags:
  - tag1
  - tag2
  - tag3
```
