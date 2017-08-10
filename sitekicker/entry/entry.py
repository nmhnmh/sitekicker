import os
import logging
import yaml

from ..util import merge_options

class Entry:
    """
    An entry usually a folder with main content file and assets, images etc. It corresponds to a unique url in generated site.
    """
    def __init__(self, site, path):
        self.site = site
        self.path = path
        self.dir = os.path.dirname(path)
        self.read_entry_content()
        self.resolve_entry_options()
        self.id = self.user_options.get('id') if self.user_options else None
        self.date = self.user_options.get('date') if self.user_options else None
        self.mtime = os.path.getmtime(self.path)
        perm_link_parts = list(self.options.get('prefix', []))
        perm_link_parts.append(str(self.id))
        self.perm_link = site.user_options['base_url'] + '/' + "/".join(perm_link_parts)
        self.link = '/' + "/".join(perm_link_parts)
        self.external_images = []
        self.linked_images = []
        self.inlined_files = []
        self.linked_files = []

    def __str__(self):
        return "Entry(%s): [%s]" % (self.id, self.path)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.date == other.date

    def __gt__(self, other):
        return self.date > other.date

    def __lt__(self, other):
        return self.date < other.date

    def read_entry_content(self):
        with open(self.path, 'r') as mf:
            all_lines = mf.readlines()
            try:
                first_line_index = all_lines.index("---\n", 0)
                second_line_index = all_lines.index("---\n", 1)
                self.user_options = yaml.load(''.join(all_lines[first_line_index+1:second_line_index])) or {}
                self.raw_content = ''.join(all_lines[second_line_index+1:])
            except Exception as e:
                logging.debug("Entry read exception: %s", e)
                self.user_options = {}
                self.raw_content = ''

    def resolve_entry_options(self):
        self.options = {}
        enclosing_folder = os.path.dirname(self.dir)
        enclosing_folder_options = self.site.folders.get(enclosing_folder).get_combined_options()
        merge_options(self.options, enclosing_folder_options)
        merge_options(self.options, self.user_options)

    def build(self):
        for name, hooks in self.site.entry_hooks.items():
            for hook in hooks:
                hook(self)
