import os
import glob
import logging
import yaml
import shutil
import jinja2

from .entry import Entry

class Site:
    def __init__(self, options={}):
        self.options = options
        self.templates = None
        self.folder_data = {}
        self.possible_entry_folders = []
        self.entries = {}
        self.possible_index_folders = []
        self.index_entries = {}

    def __str__(self):
        return "Site: [%s], output to [%s]" % (self.options.working_dir, self.options.output_dir)

    def reset(self):
        self.templates = None
        self.folder_data = {}
        self.possible_entry_folders = []
        self.entries = {}
        self.possible_index_folders = []
        self.index_entries = {}

    def load_templates(self):
        self.templates = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(self.options.working_dir, self.options.template_dir)))

    def copy_dirs(self):
        for dir_item in self.options.file_dirs:
            src_path = os.path.join(self.options.working_dir, dir_item)
            dest_path = os.path.join(self.options.output_dir, dir_item)
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)

    def preprocess_entry_folder(self, folder):
        for (path, dirs, files) in os.walk(folder):
            dir_paths = [os.path.join(path, d) for d in dirs if d[0]!='.']
            for dp in dir_paths:
                self.possible_entry_folders.append(dp)

    def preprocess_index_folder(self, folder):
        for (path, dirs, files) in os.walk(folder):
            dir_paths = [os.path.join(path, d) for d in dirs if d[0]!='.']
            for dp in dir_paths:
                self.possible_index_folders.append(dp)

    def preprocess_entry(self, entry_path):
        """ Pre-process an entry folder, if it is valid entry folder, queue it up for later build """
        logging.debug("Detecting possible folder: %s", entry_path)
        # read item meta data
        entry_data, raw_content = self.detect_folder_content(entry_path)
        if not entry_data:
            return
        # check title or id
        eid = entry_data['id']
        title = entry_data['title']
        if not title or not eid:
            logging.warning("Invalid ID or Title for entry %s!" % entry_path)
            return
        if eid in self.entries:
            raise ValueError("ID conflict found! %s and %s are using same eid!" % (self.entries[eid], entry_path))
        else:
            self.entries[eid] = Entry(self, eid, entry_data, raw_content)

    def preprocess_index_entry(self, entry_path):
        """ Pre-process an index page folder, if it is valid entry folder, queue it up for later build """
        logging.debug("Detecting index folder: %s", entry_path)
        # read item meta data
        entry_data, raw_content = self.detect_folder_content(entry_path)
        if not entry_data:
            return
        # check title or id
        eid = entry_data['id']
        title = entry_data['title']
        if not title or not eid:
            logging.warning("Invalid ID or Title for index entry %s!" % entry_path)
            return
        if eid in self.entries or eid in self.index_entries:
            raise ValueError("ID conflict found! %s and %s are using same eid!" % (self.entries[eid], entry_path))
        else:
            self.index_entries[eid] = Entry(self, eid, entry_data, raw_content)

    def detect_folder_content(self, folder_path):
        """ Detect if a folder contains a valid entry inside it """
        glob_pattern = os.path.join(folder_path, '*.md')
        main_candidates = glob.glob(glob_pattern)
        if(main_candidates):
            for candidate in main_candidates:
                entry_data, raw_content = self.detect_file_content(candidate)
                if(entry_data):
                    return entry_data, raw_content
            else:
                return {}, None
        else:
            return {}, None

    def detect_file_content(self, file_path):
        """ Try to read from a file, treat it like a valid entry document """
        with open(file_path, 'r') as mf:
            all_lines = mf.readlines()
            try:
                first_line_index = all_lines.index("---\n", 0)
                second_line_index = all_lines.index("---\n", 1)
                meta_data_str = ''.join(all_lines[first_line_index+1:second_line_index])
                raw_content = ''.join(all_lines[second_line_index+1:])
                entry_data = yaml.load(meta_data_str)
                eid = entry_data['id']
                if eid is not None:
                    entry_data['id'] = str(eid)
                    entry_data['_entry_path'] = os.path.dirname(file_path)
                    entry_data['_entry_main_file'] = os.path.basename(file_path)
            except Exception:
                return {}, None
            else:
                return entry_data, raw_content

    def get_folder_data(self, folder_path):
        folder_data = []
        while folder_path != self.options['working_dir']:
            if folder_path in self.folder_data:
                if self.folder_data[folder_path]:
                    folder_data.insert(0, self.folder_data[folder_path])
            else:
                meta_file_path = os.path.join(folder_path, 'meta.yml')
                if os.path.isfile(meta_file_path):
                    with open(meta_file_path, 'r') as meta_file:
                        data = yaml.load(meta_file)
                        self.folder_data[folder_path] = data
                        folder_data.insert(0, data)
                else:
                    self.folder_data[folder_path] = {}
            folder_path = os.path.dirname(folder_path)

        return folder_data

    def build(self):
        try:
            self.reset()
            self.load_templates()
            # Build entries
            for content_dir in self.options.entry_dirs:
                logging.info("Processing folder: %s", content_dir)
                self.preprocess_entry_folder(os.path.join(self.options['working_dir'], content_dir))
            for entry_folder in self.possible_entry_folders:
                logging.debug("Pre-process entry folder: %s" % entry_folder)
                self.preprocess_entry(entry_folder)
            logging.info("%d valid entries are found!", len(self.entries))
            for eid, entry in self.entries.items():
                entry.build()
            # Build indexes
            for index_dir in self.options.index_dirs:
                self.preprocess_index_folder(os.path.join(self.options['working_dir'], index_dir))
            for entry_folder in self.possible_index_folders:
                logging.debug("Pre-process index folder: %s" % entry_folder)
                self.preprocess_index_entry(entry_folder)
            logging.info("%d valid index entries are found!", len(self.index_entries))
            for eid, entry in self.index_entries.items():
                entry.build()
            # Copy file dirs
            self.copy_dirs()
        except Exception as e:
            raise e
            logging.error("%s" % e)

    def incremental_build(self, folder):
        try:
            self.reset()
            self.load_templates()
            self.possible_entry_folders = [folder]
            for entry_folder in self.possible_entry_folders:
                logging.debug("Pre-process entry folder: %s" % entry_folder)
                self.preprocess_entry(entry_folder)
            logging.info("%d valid entries are found!", len(self.entries))
            for eid, entry in self.entries.items():
                entry.build()
            self.copy_dirs()
        except Exception as e:
            logging.error("%s" % e)
