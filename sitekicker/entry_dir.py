import shutil
import os
import logging

class EntryDir:
    def __init__(self, entry, src):
        self.entry = entry
        self.src = src

    def __str__(self):
        return "Entry Dir: %s " % self.src

    def copy(self):
        dest = os.path.join(
            self.entry.output_dir,
            os.path.basename(self.src)
        )
        logging.debug("Copy %s to %s" % (self.src, dest))
        shutil.copytree(self.src, dest)
