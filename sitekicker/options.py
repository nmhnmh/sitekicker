import os
import yaml
import copy

from .dotdict import dotdict

def get_default_site_options():
    return dotdict({
        'name': "A Static Website",
        'base': '',
        'absolute_urls': False,
        'layout_dir': 'layout',
        'output_dir': '.dist',
        'copy_dirs': [],
        'content_dirs': [],
        'copy_hidden': False,
        'image_options': {
            'resize': {
                'max-width': 3000,
                'max-height': 3000,
            },
            'watermark': []
        },
    })

def read_site_yml(working_directory):
    site_yml_path = os.path.join(working_directory, 'site.yml')
    if os.path.isfile(site_yml_path):
        with open(site_yml_path, 'r') as site_config:
            site_options = yaml.load(site_config)
            return site_options
    else:
        return {}

def read_meta_yml(folder_path):
    meta_yml_path = os.path.join(folder_path, 'meta.yml')
    if os.path.isfile(meta_yml_path):
        with open(meta_yml_path, 'r') as meta_config:
            meta_options = yaml.load(meta_config)
            return meta_options
    else:
        return {}

def remove_list_duplicate(lst):
    """ Remove duplicate from a list, maintain original order """
    seen = set()
    seen_add = seen.add
    return [x for x in lst if not (x in seen or seen_add(x))]

def merge_entry_options(*options):
    merged_options = {
        'prefix': [],
        'tags': [],
    }
    for opt in options:
        for k, v in opt.items():
            if k == 'tags':
                merged_options[k].extend(v)
                merged_options[k]=remove_list_duplicate(merged_options[k])
            elif k == 'prefix':
                merged_options[k].append(v)
            else:
                merged_options[k]=v
    return merged_options
