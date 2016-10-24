import os
import sys
import logging
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .site import Site
from .arguments import parse_options
from .options import get_default_site_options, read_site_yml
from .util import resolve_path

class FsChangeHandler(FileSystemEventHandler):
    def __init__(self, site):
        self.site = site

    def on_any_event(self, event):
        logging.info("Change detected, dir: %s, type: %s, path: %s", event.is_directory, event.event_type, event.src_path)
        if event.is_directory:
            logging.debug("Rebuild: %s", event.src_path)
            self.site.incremental_build(event.src_path)

def main():
    site_options = get_default_site_options()
    argv_options=parse_options(sys.argv[1:])
    logging_level = getattr(logging, argv_options.log_level.upper(), logging.WARNING)
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s::%(levelname)s::%(message)s",
        datefmt="%H:%M:%S"
    )
    working_directory = resolve_path(argv_options.folder)
    site_yml_options = read_site_yml(working_directory)
    site_options.update(site_yml_options)
    output_dir_path = resolve_path(argv_options.output_dir or site_options.output_dir)
    if not os.path.isdir(output_dir_path):
        os.mkdir(output_dir_path)

    site_options.output_dir = output_dir_path
    site_options.working_dir = working_directory

    site = Site(site_options)

    if argv_options.watch:
        logging.info("%s", site)
        site.build()
        logging.info("Serving locally on port %s..." % argv_options.port)
        server = subprocess.Popen(['python3', '-m', 'http.server', argv_options.port], cwd=site_options.output_dir)
        logging.info("Watching for changes...")
        ob = Observer()
        change_handler = FsChangeHandler(site)
        for item in os.scandir(working_directory):
            if item.is_dir() and item.name[0] != '.':
                logging.info("Watching: %s", item.path)
                ob.schedule(change_handler, item.path, recursive=True)
        ob.start()
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            ob.stop()
        finally:
            server.terminate()
        ob.join()
    else:
        logging.info("%s", site)
        site.build()

if __name__ == '__main__':
    main()
