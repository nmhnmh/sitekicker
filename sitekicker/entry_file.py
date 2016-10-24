import os
import logging
import shutil

class EntryFile:
    """ Represents a binary file inside an entry """
    def __init__(self, entry, src):
        self.entry = entry
        self.src = src

    def __str__(self):
        return "Entry file: %s" % self.src

    def copy(self):
        dest = os.path.join(
            self.entry.output_dir,
            os.path.basename(self.src)
        )
        logging.debug("Copy %s to %s" % (self.src, dest))
        shutil.copy(self.src, dest)
