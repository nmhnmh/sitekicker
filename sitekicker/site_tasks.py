import os
import logging
import jinja2
import json
import time
import collections

from .util import check_is_ignored
from .entry.entry_template import EntryTemplate
from .folder.enclosure_folder import EnclosureFolder
from .folder.template_folder import TemplateFolder
from .folder.asset_folder import AssetFolder
from .folder.entry_folder import EntryFolder

def register_site_tasks(site):
    site.register_site('pre-scan', start_building)
    site.register_site('pre-scan', load_templates)
    site.register_site('pre-scan', prepare_output_path)
    site.register_site('pre-scan', load_previous_build_snapshot)
    site.register_site('scan', scan_site_folders)
    site.register_site('pre-build', convert_entry_folders)
    site.register_site('pre-build', sort_entries_by_date)
    site.register_site('pre-build', group_entries_by_tag)
    site.register_site('build', build_site_entries)
    site.register_site('post-build', end_building)
    site.register_site('pre-summary', dump_build_snapshot)
    site.register_site('pre-summary', copy_assets)
    site.register_site('summary', summary)

def start_building(site):
    print(site)
    site.start_build_time = time.time()

def summary(site):
    site.end_build_time = time.time()
    print("%d seconds used to build!" % int(site.end_build_time - site.start_build_time))

def end_building(site):
    # wait until all tasks are done
    site.task_pool.close()
    site.task_pool.join()

def dump_build_snapshot(site):
    snpashot_path = os.path.join(site.output_path, '.snapshot')
    # manually dump to json to make the output predictable
    with open(snpashot_path, 'wt', encoding='utf8') as sf:
        ordered_data = collections.OrderedDict(sorted(site.snapshots.items(), key=lambda e: e[0]))
        sf.write('{\n')
        for k, v in ordered_data.items():
            sf.write('  {}:{},\n'.format(json.dumps(k), json.dumps(v)))
        sf.write('"":""')
        sf.write('\n}')

def load_previous_build_snapshot(site):
    snpashot_path = os.path.join(site.output_path, '.snapshot')
    if os.path.isfile(snpashot_path):
        with open(snpashot_path, 'rt', encoding="utf8") as sf:
            site.snapshots.clear()
            try:
                data = json.loads(sf.read())
            except:
                data = {}
            site.snapshots.update(data)

def copy_assets(site):
    for path, folder in site.folders.items():
        if isinstance(folder, AssetFolder):
            folder.copy()

def build_site_entries(site):
    print("{} entries found!".format(len(site.entries)))
    for eid, entry in site.entries.items():
        if entry.id and entry.date:
            logging.debug("Building %s", entry)
            entry.build()

def sort_entries_by_date(site):
    valid_entries = [entry for entry in site.entries.values() if entry.id and entry.date]
    site.sorted_entries = sorted(valid_entries, reverse=True)

def group_entries_by_tag(site):
    for entry in site.sorted_entries:
        for t in entry.options.get('tags', []):
            if t not in site.grouped_entries:
                site.grouped_entries[t]=[entry]
            else:
                site.grouped_entries[t].append(entry)

def convert_entry_folders(site):
    for path, folder in site.folders.items():
        if isinstance(folder, EntryFolder):
            folder_entries = folder.find_entries()
            for entry in folder_entries:
                if not entry.id:
                    continue
                if entry.id not in site.entries:
                    site.entries[entry.id] = entry
                else:
                    raise Exception("More than one entry with id: [%s]" % entry.id)
            site.folder_entries[path] = folder_entries

def scan_site_folders(site):
    def detect_folder(path):
        logging.debug("Detecting Folder: [%s]" % path)
        items = os.scandir(path)
        for item in items:
            if item.is_dir() and check_is_ignored(site.build_options['ignore_dirs'], item.path):
                logging.warn("User ignore folder: %s", item.path)
                continue
            if item.is_file() and not item.name == 'folder.yml' and not item.name.startswith('.'):
                logging.debug("Skipping folder file: [%s]", item.path)
            elif not item.is_dir():
                continue
            elif item.name.startswith('.'):
                logging.debug("Skipping Folder: [%s]", item.path)
                continue
            elif EntryFolder.is_entry_folder(item.path):
                site.folders[item.path] = EntryFolder(site, item.path)
                logging.debug("Found New %s", site.folders[item.path])
            else:
                site.folders[item.path] = EnclosureFolder(site, item.path)
                logging.debug("Found New %s", site.folders[item.path])
                detect_folder(item.path)
    site_dirs = os.scandir(site.working_path)
    for sdir in site_dirs:
        if check_is_ignored(site.build_options['ignore_dirs'], sdir.path):
            logging.warn("User ignore folder: %s", sdir.name)
            continue
        if sdir.is_dir() and not sdir.name.startswith('.'):
            if type(site.build_options.asset_dirs)==list and sdir.name in site.build_options.asset_dirs:
                site.folders[sdir.path] = AssetFolder(site, sdir.path)
                logging.debug("Found New %s", site.folders[sdir.path])
            elif sdir.name == site.build_options.template_dir:
                site.folders[sdir.path] = TemplateFolder(site, sdir.path)
                logging.debug("Found New %s", site.folders[sdir.path])
            else:
                site.folders[sdir.path] = EnclosureFolder(site, sdir.path)
                logging.debug("Found New %s", site.folders[sdir.path])
                detect_folder(sdir.path)

def prepare_output_path(site):
    if not os.path.isdir(site.output_path):
        logging.debug("Output path: [%s] not fould, try to create it!", site.output_path)
        os.mkdir(site.output_path)
    elif not os.access(site.output_path, os.W_OK | os.X_OK):
        raise Exception("Output path: [%s] exists, but the permission seems not right, please check!", site.output_path)
    else:
        logging.debug("Output path: [%s] is ok!", site.output_path)


def load_templates(site):
    template_dir = site.build_options['template_dir']
    full_template_path = os.path.realpath(os.path.join(site.working_path, template_dir))
    logging.debug("Scanning template dir: [%s]" % full_template_path)
    site.template_registry = {}
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(full_template_path),
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=['jinja2.ext.i18n']
    )
    env.install_null_translations()
    # Load Jinja2 Custom Filters
    from .jinja2_filters import xml_escape, date_to_rfc822, date_to_iso8601, escape_quote
    env.filters['xml_escape'] = xml_escape
    env.filters['date_to_rfc822'] = date_to_rfc822
    env.filters['date_to_iso8601'] = date_to_iso8601
    env.filters['escape_quote'] = escape_quote
    template_items = os.scandir(full_template_path)
    for it in template_items:
        if it.is_file() and not it.name.startswith('.') and it.name.endswith('.j2'):
            logging.debug("Find template [%s]@[%s]", it.name, full_template_path)
            site.template_registry[it.name] = EntryTemplate(it.name, env.get_template(it.name))
    logging.debug("%d templates are found!", len(site.template_registry))
