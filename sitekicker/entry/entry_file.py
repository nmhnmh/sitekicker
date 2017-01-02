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
        dest = os.path.join(self.entry.output_path, self.src[len(self.entry.dir)+1:])
        dest_dir = os.path.dirname(dest)
        logging.debug("Copy entry file from %s to %s" % (self.src, dest))
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        shutil.copy(self.src, dest)
