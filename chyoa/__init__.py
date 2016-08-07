#!/usr/bin/env python3

__all__ = ["main"]
__license__ = "MIT"

from .download import Downloader
from .tree import ChyoaTree
from .util import get_elapsed_time
import os.path
import time

def main(argv=[__file__]):
    if len(argv) < 2:
        print("Usage: %s action [options]" % os.path.basename(argv[0]))
        exit(1)

    action = argv[1]

    start = time.time()
    if action in ("download", "download-only"):
        if len(argv) < 3:
            print("Usage: %s %s url [destination]" % (os.path.basename(argv[0]), action))
            exit(1)

        dl = Downloader(recursive=(action == "download"))

        url = argv[2]
        if len(argv) < 4:
            dest = "."
        else:
            dest = argv[3]

        dl.download(url, dest)
    elif action == "tree":
        if len(argv) < 3:
            print("Usage: %s tree path" % os.path.basename(argv[0]))
            exit(1)

        path = argv[2]
        tree = ChyoaTree(path)
        tree.display()
    else:
        print("Unknown action: %s" % action)
        print("Available actions: download, download-only, tree")
        exit(1)

    print("Finished in %s." % get_elapsed_time(time.time() - start))


