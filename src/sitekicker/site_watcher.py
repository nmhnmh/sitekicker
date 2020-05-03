import time
import os
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .site_server import serve_standalone

class FsChangeHandler(FileSystemEventHandler):
    def __init__(self, site):
        self.site = site

    def on_any_event(self, event):
        if not event.is_directory and event.src_path.endswith('.swp'):
            return
        if event.is_directory and event.event_type=='modified':
            return
        logging.info("Change, DIR: %s, Type: %s, PATH: %s", event.is_directory, event.event_type, event.src_path)
        self.site.build()

def watch_site(site, serve_site=False):
    logging.info("Watching %s...", site)
    ob = Observer()
    serve_thread = None
    change_handler = FsChangeHandler(site)
    for item in os.scandir(site.working_path):
        if item.is_dir() and item.name[0] != '.':
            logging.info("Watching: %s", item.path)
            ob.schedule(change_handler, item.path, recursive=True)
    ob.start()
    if serve_site:
        serve_thread = serve_standalone(site)
        serve_thread.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        ob.stop()
    ob.join()
