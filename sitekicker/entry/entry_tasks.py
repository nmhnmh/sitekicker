import os
import markdown
import logging
import shutil
from datetime import date
from bs4 import BeautifulSoup
import re
import yaml
import html

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
    site.register_entry('post-compile', process_responsive_images_tags)
    site.register_entry('post-compile', setup_meta_tags)
    site.register_entry('link', link_entry)
    site.register_entry('pre-link', resolve_output_path)
    site.register_entry('post-link', write_entry_output)
    site.register_entry('post-link', copy_entry_files)
    site.register_entry('post-link', process_entry_images)

def copy_entry_files(entry):
    for fi in entry.linked_files:
        fi.copy()

def process_entry_images(entry):
    for img in entry.linked_images:
        img.process()

def resolve_output_path(entry):
    user_output_path = entry.options.get('output_path', None)
    if user_output_path is not None:
        entry.output_path = os.path.join(entry.site.output_path, entry.options.get('output_path'))
    else:
        entry.output_path = os.path.join(entry.site.output_path, *entry.options.get('prefix', []), entry.id)

def resolve_inlined_files(entry):
    """ Inlined files must be read and insert to its anchor point, before compilation """
    entry.inlined_files = []
    def read_file(match):
        name = match.group(1)
        fullpath = os.path.join(entry.dir, name)
        entry.inlined_files.append(fullpath)
        logging.debug("Find inlined file: [%s]", fullpath)
        with open(fullpath, 'r') as f:
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
            'pymdownx.github',
            #'markdown.extensions.codehilite',
            'pymdownx.arithmatex',
        ]
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
    # Detect Code Blocks
    if re.search(r'\<code[^>]*>', entry.compile_output):
        entry.options['meta_tags'].add('code')

def resolve_linked_file(entry):
    """ Find out all files linked with <a> """
    entry.linked_files = []
    def tap_link(link_match):
        link_text = link_match.group(0)
        link = BeautifulSoup(link_text, 'html.parser').a
        attrs = link.attrs
        src = attrs.get('href')
        if src.startswith('http://') or src.startswith('https://'):
            pass
        else:
            fullpath = os.path.join(entry.dir, src)
            if os.path.isfile(fullpath):
                entry.linked_files.append(EntryFile(entry, fullpath))
            else:
                pass
    re.sub(r'\<a\s+[^>]*\s*\>([^<]+)</a>', tap_link, entry.compile_output)

def resolve_all_images(entry):
    """ Find out all images used by <image/> tag """
    entry.external_images = []
    entry.linked_images = []
    def sub_img(image_match):
        img_text = image_match.group(0)
        img = BeautifulSoup(img_text, 'html.parser').img
        attrs = img.attrs
        src = attrs.get('src')
        if src.startswith('http://') or src.startswith('https://'):
            entry.external_images.append(src)
        else:
            fullpath = os.path.join(entry.dir, src)
            entry.linked_images.append(EntryImage(entry, fullpath))
    re.sub(r'\<img\s+[^>]*\s*\>', sub_img, entry.compile_output)

def process_responsive_images_tags(entry):
    # Substitute <img> tag for lazy-responsive-load
    def sub_img(image_match):
        img_text = image_match.group(0)
        img = BeautifulSoup(img_text, 'html.parser').img
        attrs = img.attrs
        src = attrs.get('src')
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
    page_template = entry.site.template_registry.get(entry.options.get('layout', 'default')+'.j2')
    template_data = {
        'entry_content': entry.compile_output,
        'site': entry.site,
        'sitekicker': sitekicker,
        'perm_link': entry.perm_link,
    }
    template_data.update(entry.options)
    entry.html_output = page_template.render(template_data)

def write_entry_output(entry):
    """ Save the final html output to file """
    logging.info('Output path: %s', entry.output_path)
    if not os.path.isdir(entry.output_path):
        os.makedirs(entry.output_path)
    output_name = entry.options.get('output_name', 'index.html')
    output_path = os.path.join(entry.output_path, output_name)
    with open(output_path, 'w') as of:
        logging.info("Writing built html to: %s", output_path)
        of.write(entry.html_output)
