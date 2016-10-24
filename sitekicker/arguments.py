import argparse
import sitekicker

def parse_options(arguments):
    ap = argparse.ArgumentParser(description="SiteKicker")
    ap.add_argument(
        "--log-level",
        default='info',
        choices=['info', 'debug', 'warning', 'error', 'critical'],
        dest="log_level",
        help="Set log level, default is warning"
    )
    ap.add_argument('--watch', '-w', action="store_true", default=False, help="Watch for changes and rebuild, default is false")
    ap.add_argument('--version', '-V', action="version", version=sitekicker.version, help="Version number")
    ap.add_argument('--port', '-p', default="8080", help="Local Preview Server Listen Port Number")
    ap.add_argument('--output-dir', '-o', default="", help="Directory to write build output")
    ap.add_argument("folder", nargs="?", default=".", help="Folder to process, default is current directory")
    argv_options = ap.parse_args(arguments)
    return argv_options
