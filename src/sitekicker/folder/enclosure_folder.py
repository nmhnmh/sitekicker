import os
import yaml

from ..util import merge_options

class EnclosureFolder:
    def __init__(self, site, path):
        self.site = site
        self.path = path
        self.options = self.read_folder_options()
        self.combined_options = None

    def __str__(self):
        return "EnclosureFolder: [%s], folder options: %s" % (self.path, self.options)

    def read_folder_options(self):
        folder_yml_path = os.path.join(self.path, 'folder.yml')
        if os.path.isfile(folder_yml_path):
            with open(folder_yml_path, 'r', encoding='utf8') as folder_config:
                return yaml.load(folder_config) or {}
        else:
            return {}

    def get_combined_options(self):
        if self.combined_options is not None:
            return self.combined_options
        else:
            self.combined_options = {}
            merge_options(self.combined_options, self.options)
            enclosing_folder_path = os.path.dirname(self.path)
            enclosing_folder = self.site.folders.get(enclosing_folder_path, None)
            if enclosing_folder:
                enclosing_folder_options = enclosing_folder.get_combined_options()
                merge_options(self.combined_options, enclosing_folder_options)
            return self.combined_options
