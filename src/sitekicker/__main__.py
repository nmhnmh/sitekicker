import os
import sys
import logging
import time
import subprocess

from .site import Site
from .util import parse_command_line_options

def main():
    argv_options=parse_command_line_options(sys.argv[1:])
    # Logging Configuration
    logging_level = getattr(logging, argv_options.log_level.upper(), logging.WARNING)
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s::%(levelname)s::%(message)s",
        datefmt="%H:%M:%S"
    )
    site = Site(argv_options)
    logging.info("%s", site)

    if argv_options.watch:
        site.build()
        if argv_options.serve:
            site.watch(True)
        else:
            site.watch()
    else:
        site.build()
        if argv_options.serve:
            try:
                site.serve()
            except KeyboardInterrupt:
                print('exiting')
            except e:
                print(e)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
