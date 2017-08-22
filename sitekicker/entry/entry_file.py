import os
import logging
import shutil

class EntryFile:
    """ Represents a binary file inside an entry """
    def __init__(self, entry, title, name):
        self.entry = entry
        self.title = title
        self.name = name
        self.fullpath = os.path.realpath(os.path.join(entry.dir, name))
        self.dest_fullpath = os.path.join(entry.output_path, self.fullpath[len(self.entry.dir)+1:])
        self.check_file()

    def check_file(self):
        if not os.path.isfile(self.fullpath):
            raise Exception("Post [{} > {}] referencing a non-exist local file: [{}]!".format(self.entry.id, self.title, self.name))

    def __str__(self):
        return "Entry file: %s" % self.fullpath

    def copy(self):
        dest_dir = os.path.dirname(self.dest_fullpath)
        logging.debug("Copy entry file from %s to %s" % (self.fullpath, self.dest_fullpath))
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        shutil.copyfile(self.fullpath, self.dest_fullpath)
