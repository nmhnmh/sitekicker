import os

def resolve_path(path):
    path = os.path.expanduser(path)
    return os.path.abspath(path)
