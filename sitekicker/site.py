import os
import yaml
import time
from multiprocessing import Pool, Manager
import collections

from .util import resolve_path, dotdict, get_default_site_options
from .site_tasks import register_site_tasks
from .entry.entry_tasks import register_entry_tasks
from .site_watcher import watch_site
from .site_server import serve

SITE_HOOK_NAMES = [
    'pre-scan',
    'scan',
    'post-scan',
    'pre-mark',
    'mark',
    'post-mark',
    'pre-build',
    'build',
    'post-build',
    'pre-summary',
    'summary',
    'post-summary',
]

ENTRY_HOOK_NAMES = [
    'pre-compile',
    'compile',
    'post-compile',
    'pre-link',
    'link',
    'post-link',
]

class Site:
    def __init__(self, argv_options):
        self.working_path = resolve_path(argv_options.folder)
        # Command line options
        self.cli_options = argv_options
        # Default options
        self.default_options = get_default_site_options()
        # This is the options from sitekicker.yml and command line options
        user_options_dict = dict(self.default_options)
        user_options_dict.update(self.read_sitekicker_yml())
        self.user_options = dotdict(user_options_dict)
        # This is the derived options from user settings, cli options etc
        self.build_options = dotdict({})
        self.build_options.update(self.default_options)
        self.build_options.update(self.user_options)
        self.output_path = resolve_path(argv_options.output_dir or self.user_options.output_dir or '.dist')
        self.build_options.output_path = self.output_path
        self.build_options.working_path = self.working_path
        # data placeholders
        self.time = time.localtime()
        self.timestamp = time.time()
        self.template_registry = []
        self.folders = {}
        self.folder_entries = {}
        self.entries = {}
        self.sorted_entries = []
        self.grouped_entries = {}
        # build hook registry
        self.site_hooks = collections.OrderedDict()
        self.entry_hooks = collections.OrderedDict()
        for hook in SITE_HOOK_NAMES:
            self.site_hooks[hook] = []
        for hook in ENTRY_HOOK_NAMES:
            self.entry_hooks[hook] = []
        # register site task
        register_site_tasks(self)
        register_entry_tasks(self)
        # global task pool for parallel processing
        self.task_pool = Pool()
        self.task_pool_manager = Manager()
        self.snapshots = self.task_pool_manager.dict()

    def reset(self):
        self.time = time.gmtime()
        self.template_registry = []
        self.folders = {}
        self.folder_entries = {}
        self.entries = {}
        self.sorted_entries = []
        self.grouped_entries = {}
        self.task_pool = Pool()
        self.snapshots = self.task_pool_manager.dict()

    def __str__(self):
        return "Site: [%s], output to [%s]" % (self.working_path, self.output_path)

    def read_sitekicker_yml(self):
        site_yml_path = os.path.join(self.working_path, 'sitekicker.yml')
        if os.path.isfile(site_yml_path):
            with open(site_yml_path, 'rt', encoding='utf8') as site_config:
                user_options = dotdict(yaml.load(site_config))
                return user_options
        else:
            raise Exception("sitekicker.yml is not found!")

    def register_site(self, hook, handler):
        if hook in self.site_hooks:
            self.site_hooks[hook].append(handler)
        else:
            raise Exception("Invalid Site Hook name: %s" % hook)

    def register_entry(self, hook, handler):
        if hook in self.entry_hooks:
            self.entry_hooks[hook].append(handler)
        else:
            raise Exception("Invalid Entry Hook name: %s" % hook)

    def build(self):
        """ Default build operation, lazy, only build parts that need to be built """
        self.reset()
        for hook in SITE_HOOK_NAMES:
            if self.site_hooks[hook]:
                for handler in self.site_hooks[hook]:
                    handler(self)

    def watch(self, serve_site=False):
        """ Watch for changes inside the site folder, rebuild items that changed """
        watch_site(self, serve_site)

    def serve(self):
        serve(self)
