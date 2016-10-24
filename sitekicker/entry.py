import os
import markdown
import logging
import shutil

from .entry_dir import EntryDir
from .entry_file import EntryFile
from .entry_image import EntryImage
from .options import merge_entry_options

class Entry:
    """
    An entry usually a folder with main content file and assets, images etc. It corresponds to a unique url in generated site.
    """
    def __init__(self, site, eid, options, raw_content):
        self.site = site
        self.id = eid
        self.options = options
        self.raw_content = raw_content
        self.reset()

    def reset(self):
        """ Reset preview entry build results, prepare for a new build """
        self.perm_link = None
        self.dirs = []
        self.files = []
        self.images = []
        self.build_output = None
        self.html_output = None
        self.output_dir = None

    def __str__(self):
        return "Entry: %s, at %s, %i dirs, %i files, %i images" % (
            self.id,
            self.options['_entry_path'],
            len(self.dirs),
            len(self.files),
            len(self.images)
        )

    def build_markdown(self):
        """ Build the main content of the entry, which is written in markdown """
        md_out = markdown.markdown(
            self.raw_content,
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.toc',
                'markdown.extensions.codehilite',
                'pymdownx.arithmatex',
            ]
        )
        return md_out

    def build_rst(self):
        pass

    def build_latex(self):
        pass

    def assemble_html(self):
        """ Link entry content with header, footer to get the final html output for the entry """
        page_template = self.site.templates.get_template(self.options.get('layout', 'default')+'.j2')
        template_data = {
            'entry_content': self.build_output,
            'site': self.site,
        }
        template_data.update(self.options)
        return page_template.render(template_data)

    def write(self):
        """ Save the final html output to file """
        output_path = os.path.join(self.output_dir, 'index.html')
        with open(output_path, 'w') as of:
            logging.info("Writing built html to: %s", output_path)
            of.write(self.html_output)

    def build(self):
        """ Build the entry, do all the jobs """
        self.reset()
        for entry_item in os.scandir(self.options['_entry_path']):
            src = entry_item.path
            if entry_item.is_dir() and entry_item.name[0] != '.':
                self.dirs.append(EntryDir(self, src))
            if entry_item.is_file() and entry_item.name[0] != '.':
                if entry_item.name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    self.images.append(EntryImage(self, src))
                else:
                    self.files.append(EntryFile(self, src))
        logging.info('Building: %s', self)
        folder_options = self.site.get_folder_data(self.options['_entry_path'])
        self.options = merge_entry_options(*folder_options, self.options)
        if self.id == 'index':
            self.output_dir = self.site.options['output_dir']
            self.perm_link = '/'
            self.build_output = self.build_markdown()
            self.html_output = self.assemble_html()
            self.write()
        else:
            self.output_dir = os.path.join(self.site.options['output_dir'], *self.options['prefix'], self.id)
            self.perm_link = '/'+'/'.join([*self.options['prefix'], self.id])
            if os.path.isdir(self.output_dir):
                shutil.rmtree(self.output_dir)
            os.makedirs(self.output_dir)
            self.build_output = self.build_markdown()
            self.html_output = self.assemble_html()
            self.write()
            self.copy_entry_items()

    def copy_entry_items(self):
        """ Copy assets, images, binary files in side the entry folder """
        for dir in self.dirs:
            dir.copy()
        for file in self.files:
            file.copy()
        for image in self.images:
            image.resize()
