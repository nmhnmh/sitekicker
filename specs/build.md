# Build Spec

## Phase 1: Pre-Scan, Scan, Post-Scan
Scan all the content folders, templates, index pages, entries, images, files.

## Phase 1.1: Pre-Mark, Mark, Post-Mark
Mark items that need to be rebuild, with the help of previous build status records.

## Phase 2: Pre-Compile Entries
Prepare for entry building. Resolve entry meta data(including template used, output path, files, images). Resolve entry id, title, link, otput folder etc.
Resolve entry denpendencies.

## Phase 3: Compile Entries
Build entry, compile from **markdown to html**, link with template. Process images, files.

## Phase 4: Post-Compile Entries
Build entry, compile from **markdown to html**, link with template. Process images, files.

## Phase 5: Pre-Link Entries
Resolve referenced files.
Resolve code block.
Resolve responsive images.

## Phase 6: Link Entries
Resolve referenced files.
Resolve code block.
Resolve responsive images.

## Phase 7: Post-Link Entries
compress html output, strip spaces etc

## Phase 8: Summary
What is changed, what is build. Display statistics.