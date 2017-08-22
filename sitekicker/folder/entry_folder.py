import os
import glob

from ..entry.entry import Entry

class EntryFolder:
    def __init__(self, site, path):
        self.path = path
        self.site = site

    def __str__(self):
        return "EntryFolder: [%s]" % self.path

    def find_entries(self):
        entries = []
        glob_pattern = os.path.join(self.path, '*.md')
        main_candidates = glob.glob(glob_pattern)
        if(main_candidates):
            for candidate in main_candidates:
                if EntryFolder.detect_file_content(candidate):
                    entries.append(Entry(self.site, candidate))
        return entries

    @staticmethod
    def is_entry_folder(path):
        """ Detect if a folder contains a valid entry inside it """
        glob_pattern = os.path.join(path, '*.md')
        main_candidates = glob.glob(glob_pattern)
        if(main_candidates):
            for candidate in main_candidates:
                return EntryFolder.detect_file_content(candidate)
            else:
                return False
        else:
            False

    @staticmethod
    def detect_file_content(path):
        """ Check if a file is valid entry file, by check its front matter """
        with open(path, 'rt', encoding='utf8') as mf:
            all_lines = ''.join(mf.readlines())
            try:
                # valid entry must have valid "front matter" block(options block)
                start_index = all_lines.index("---\n", 0)
                end_index = all_lines.index("---\n", 4)
                # valid entry must have id, title
                all_lines.index("\nid: ", start_index, end_index)
                all_lines.index("\ntitle: ", start_index, end_index)
                # all_lines.index("\ndate: ", start_index, end_index)
            except Exception:
                return False
            else:
                return True
