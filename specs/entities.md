# Sitekicker Glossaries

## Site
A **folder** with some contents inside it, and a **sitekicker.yml** file.

## sitekicker.yml
This is the global configuration file for the **Site**. The settings will apply to whole site.

## Templates
Templates are skeletons, they define the structure of the pages, thus the structure of the whole site, it is containers for contents.

## Enclosure Folders
These Folders are used to **organize** entries, you may use folders to organize your entries in the way you like, you may nest folders, under each folder you may place a **folder.yml** file, which contains meta data that will be applied to all entries inside the folder. Folders has nothing to do with built output, it is just used to organize things when you are writting. Enclosure folders should inlucde **Entry folders Only** or **Nested Enclosure Folders Only**, you can not mix the two inside the an Enclosure Folder.

## Entry Folder
Each entry has its own folder, that folder is the entry folder, it should contain only stuff about the entry, nothing else, and it could contain everything about the entry, files, sub-folders etc. Sub-folders inside the entry folders will not be processed, it will only be copied to entry output folder.

## Normal Folders
Just folders that are neither **Entry Folders** nor **Enclosure Folders**, contains anything you want. It will not be processed, except being copied.

## folder.yml
**folder.yml** is an optional configuration file for an **Enclosure Folder**,  its contents will apply to everything inside the **Enclosure Folder**. It is a good place to set some **folder-wide common settings**. Settings in sub-folders will override parent folder settings, if they contains conflicting settings, with the exception of **tags** and **prefix**, tags will be merged and combined, prefix will be concatenated to form a url prefix. 

## Entry
Entry is the smallest building unit, one entry will be built into a single web page, with a unique link. One entry is also one folder, and a folder can only include one entry(but it may have different languages, for example chinese version and english verison). All files and images related to the entry should be placed under the entry folder.

## Entry Images
Images used and referenced by the entry. Will be processed and resized for **responsive images** and **lazy loading**, the processed images will be copied to the entry output folder.

## Entry Files
Files used and referenced by the entry. It could be some **binary files**, linked by the entry for download. It could be some **text or source files**, referenced by the entry, when building, the text or source will be inserted into the web page. When building, these files will be copied to the entry output folder.

## Assets
Images, Stylesheets, Js files, icons, fonts etc, usually they will be placed under some asset folder, and will be copied to output directory.
