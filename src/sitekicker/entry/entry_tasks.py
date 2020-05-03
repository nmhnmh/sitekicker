import os
import markdown
import logging
import shutil
from datetime import date
from bs4 import BeautifulSoup
import re
import yaml
import html
import jinja2

import sitekicker

from .entry_dir import EntryDir
from .entry_file import EntryFile
from .entry_image import EntryImage
from ..util import get_image_size

def register_entry_tasks(site):
    site.register_entry('pre-compile', resolve_inlined_files)
    site.register_entry('compile', compile_markdown)
    site.register_entry('post-compile', resolve_linked_file)
    site.register_entry('post-compile', resolve_all_images)
    if site.build_options['responsive_images']:
        site.register_entry('post-compile', process_responsive_images_tags)
    site.register_entry('post-compile', setup_meta_tags)
    site.register_entry('link', link_entry)
    site.register_entry('post-link', write_entry_output)
    site.register_entry('post-link', copy_entry_files)
    if site.build_options['responsive_images']:
        site.register_entry('post-link', process_responsive_entry_images)
    else:
        site.register_entry('post-link', copy_entry_images)
    site.register_entry('post-link', summary)

def summary(entry):
    print(entry)

def copy_entry_images(entry):
    for img in entry.linked_images:
        if not img.is_external:
            img.copy()

def copy_entry_files(entry):
    for fi in entry.linked_files:
        if not fi.is_external:
            fi.copy()

def process_responsive_entry_images(entry):
    for img in entry.linked_images:
        img.responsive_process()

def resolve_inlined_files(entry):
    """ Inlined files must be read and insert to its anchor point, before compilation """
    entry.inlined_files = []
    def read_file(match):
        name = match.group(1)
        fullpath = os.path.join(entry.dir, name)
        entry.inlined_files.append(fullpath)
        logging.debug("Find inlined file: [%s]", fullpath)
        with open(fullpath, 'rt', encoding="utf8") as f:
            return f.read()
    raw_content = entry.raw_content
    # read and insert file content for [[file: filename]] tags before build
    entry.raw_content = re.sub(r'\[\[file: ([^]]+)\]\]', read_file, raw_content)

def compile_markdown(entry):
    """ Build the main content of the entry, which is written in markdown at the moment """
    md_out = markdown.markdown(
        entry.raw_content,
        extensions=[
            'markdown.extensions.extra',
            'pymdownx.tilde',
            'pymdownx.magiclink',
            'pymdownx.arithmatex',
        ],
        output_format="html5"
    )
    entry.compile_output = md_out

def setup_meta_tags(entry):
    entry.options['meta_tags'] = set()
    # Detect MathJax usage
    if re.search(r'\\\(.*\\\)|\\\[.*\\\]', entry.compile_output):
        entry.options['meta_tags'].add('math')
    # Detect Images
    if entry.external_images or entry.linked_images:
        entry.options['meta_tags'].add('image')
        if re.search(r'srcset', entry.compile_output):
            entry.options['meta_tags'].add('responsive-image')
        if re.search(r'lazyload', entry.compile_output):
            entry.options['meta_tags'].add('lazyload-image')
    # Detect Code Blocks
    if re.search(r'\<code[^>]*>', entry.compile_output) or re.search(r'\<pre[^>]*>', entry.compile_output):
        entry.options['meta_tags'].add('code')

def resolve_linked_file(entry):
    """ Find out all files linked with <a> """
    entry.linked_files = []
    def tap_link(link_match):
        link_text = link_match.group(0)
        link = BeautifulSoup(link_text, 'html.parser').a
        attrs = link.attrs
        href = attrs.get('href')
        title = link.string
        if href.startswith('http://') or href.startswith('https://') or href.startswith('//'):
            pass
        else:
            entry.linked_files.append(EntryFile(entry, title, href))
    re.sub(r'\<a\s+[^>]*\s*\>([^<]+)</a>', tap_link, entry.compile_output)

def resolve_all_images(entry):
    """ Find out all images used by <image/> tag """
    entry.external_images = []
    entry.linked_images = []
    def sub_img(image_match):
        img_text = image_match.group(0)
        img = BeautifulSoup(img_text, 'html.parser').img
        attrs = img.attrs
        title = attrs.get('alt') or ''
        name = attrs.get('src') or attrs.get('data-src')
        if name.startswith('http://') or name.startswith('https://') or name.startswith('//'):
            entry.external_images.append(name)
        else:
            entry.linked_images.append(EntryImage(entry, title, name))
    re.sub(r'\<img\s+[^>]*\s*\>', sub_img, entry.compile_output)

def process_responsive_images_tags(entry):
    # Substitute <img> tag for lazy-responsive-load
    def sub_img(image_match):
        img_text = image_match.group(0)
        img = BeautifulSoup(img_text, 'html.parser').img
        attrs = img.attrs
        src = attrs.get('src') or attrs.get('data-src')
        alt = html.escape(attrs.get('alt') or src)
        classes = attrs.get('class') or []
        if src.startswith('http://') or src.startswith('https://') or src.startswith('//'):
            sub = '<img data-src="' + src + '" class="lazyload" />'
        else:
            alt = attrs.get('alt', '')
            src_parts = src.rsplit(sep='.', maxsplit=1)
            src_width, src_height = get_image_size(os.path.join(entry.dir, src))
            srcsets = []
            for width in entry.site.build_options['responsive_image_sizes']:
                if src_width<width:
                    srcsets.append(src_parts[0] + '-'+ str(src_width) +'px' + '.' + src_parts[1] + ' ' + str(src_width) + 'w')
                    break
                else:
                    srcsets.append(src_parts[0] + '-'+ str(width) +'px' + '.' + src_parts[1] + ' ' + str(width) + 'w')
            srcset_text = ','.join(srcsets)
            default_src = src_parts[0] + '-'+ str(entry.site.build_options['responsive_image_sizes'][1]) +'px' + '.' + src_parts[1]
            lqip_src = src_parts[0] + '-'+ str(entry.site.build_options['image_placeholder_size']) +'px' + '.' + src_parts[1]
            sub = '<img style="max-width: {max_width}px; max-height: {max_height}px;" src="{lqip_src}" data-src="{default_src}" data-sizes="auto" data-srcset="{src_set}" class="lazyload lqip-blur {classes}" alt="{alt}"/>'.format(max_width=str(src_width), max_height=str(src_height), lqip_src=lqip_src, default_src=default_src, src_set=srcset_text, alt=alt, classes=' '.join(classes))
        return sub
    entry.compile_output = re.sub(r'\<img\s+[^>]*\s*\>', sub_img, entry.compile_output)

def link_entry(entry):
    """ Link entry content with header, footer to get the final html output for the entry """
    entry_template_name = entry.options.get('layout', 'default')+'.j2'
    page_template = entry.site.template_registry.get(entry_template_name)
    if not page_template:
        if entry_template_name=='default.j2':
            page_template=jinja2.Template('{{ content }}')
        else:
            raise Exception("Entry[{}] using invalid template: [{}]".format(entry.id, entry_template_name))
    template_data = {
        'sitekicker': sitekicker,
        'site': entry.site,
        'entry': entry,
        'entry_content': entry.compile_output,
        'perm_link': entry.perm_link,
    }
    template_data.update(entry.options)
    entry.html_output = page_template.render(template_data)

def write_entry_output(entry):
    """ Save the final html output to file """
    logging.debug('Output path: %s', entry.output_path)
    if not os.path.isdir(entry.output_path):
        os.makedirs(entry.output_path)
    output_name = entry.options.get('output_name', 'index.html')
    output_path = os.path.join(entry.output_path, output_name)
    with open(output_path, 'wt', encoding="utf8") as of:
        logging.debug("Writing built html to: %s", output_path)
        of.write(entry.html_output)
