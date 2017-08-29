import os
import argparse
import sitekicker
import subprocess
import re

def resolve_path(path):
    path = os.path.expanduser(path)
    return os.path.abspath(path)

def check_is_ignored(patterns, path):
    if not patterns:
        return False
    for p in patterns:
        if re.search(p, path) is not None:
            return True
    return False

def remove_list_duplicate(lst):
    """ Remove duplicate from a list, maintain original order """
    seen = set()
    seen_add = seen.add
    return [x for x in lst if not (x in seen or seen_add(x))]

def merge_options(to_options, from_options):
    for k, v in from_options.items():
        if k == 'tags':
            if not k in to_options:
                to_options[k] = list()
            to_options[k].extend(v)
            to_options[k]=remove_list_duplicate(to_options[k])
        elif k == 'prefix':
            if not k in to_options:
                to_options[k] = list()
            if type(v)==list:
                to_options[k].extend(v)
            else:
                to_options[k].append(v)
        else:
            to_options[k]=v

def parse_command_line_options(arguments):
    ap = argparse.ArgumentParser(description="SiteKicker")
    ap.add_argument(
        "--log-level",
        default='info',
        choices=['info', 'debug', 'warning', 'error', 'critical'],
        dest="log_level",
        help="Set log level, default is warning"
    )
    ap.add_argument('--no-parallel', action="store_true", default=False, help="Do not use parallel image processing, this will make build slower, default is False")
    ap.add_argument('--serve', '-s', action="store_true", default=False, help="Serve the built contents with a local server for preview, default is False")
    ap.add_argument('--watch', '-w', action="store_true", default=False, help="Watch for changes and rebuild, default is False")
    ap.add_argument('--full-build', '-f', action="store_true", default=False, help="Build everything from scratch, ignore all caches, it would slow down the build, default is False")
    ap.add_argument('--version', '-V', action="version", version=sitekicker.version, help="Show version number")
    ap.add_argument('--port', '-p', default="8000", help="Default port for the local preview server to listen")
    ap.add_argument('--output-dir', '-o', default="", help="Directory to write build output")
    ap.add_argument("folder", nargs="?", default=".", help="Folder to process, default is current directory")
    argv_options = ap.parse_args(arguments)
    return argv_options

def get_default_site_options():
    return dotdict({
        'name': "An Awesome Website",
        'base_url': '',
        'absolute_urls': False,
        'template_dir': 'templates',
        'output_dir': '.dist',
        'asset_dirs': ['assets'],
        'content_dirs': [],
        'ignore_dirs': [],
        'copy_hidden': False,
        'responsive_images': False,
        'responsive_image_sizes': [500, 1000, 1500],
        'image_placeholder_size': 48,
        'image_placeholder_quality': 15,
        'maximum_image_width': '1500',
        'compress_image': True,
        'compress_image_quality': 80
    })

class dotdict(dict):
    def __init__(self, *args, **kwargs):
        super(dotdict, self).__init__(*args, **kwargs)
        self._set_from_args(args, kwargs)

    def _set_from_args(self, args, kwargs):
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = dotdict(v)
                    else:
                        self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = dotdict(v)
                else:
                    self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(dotdict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(dotdict, self).__delitem__(key)
        del self.__dict__[key]

    def update(self, *args, **kwargs):
        super(dotdict, self).update(*args, **kwargs)
        self._set_from_args(args, kwargs)

def get_image_size(src):
    im_raw_size = subprocess.check_output(['identify', src])
    im_raw_size_match = re.search(r'\s(\d+)x(\d+)\s', im_raw_size.decode('utf8') if im_raw_size else '')
    if im_raw_size_match:
        return int(im_raw_size_match.group(1)), int(im_raw_size_match.group(2))
    else:
        return 0, 0
