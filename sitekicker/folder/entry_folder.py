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
        with open(path, 'r') as mf:
            all_lines = mf.readlines()
            try:
                first_line_index = all_lines.index("---\n", 0)
                second_line_index = all_lines.index("---\n", 1)
                # meta_data_str = ''.join(all_lines[first_line_index+1:second_line_index])
                # raw_content = ''.join(all_lines[second_line_index+1:])
            except Exception:
                return False
            else:
                return True
