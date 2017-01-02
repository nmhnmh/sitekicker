import os
import shutil

class AssetFolder:
    def __init__(self, site, path):
        self.path = path
        self.site = site

    def __str__(self):
        return "AssetFolder: [%s]" % self.path

    def copy(self):
        dest_path = os.path.join(self.site.output_path, os.path.basename(self.path))
        if os.path.isdir(dest_path):
            shutil.rmtree(dest_path)
        shutil.copytree(self.path, dest_path)
