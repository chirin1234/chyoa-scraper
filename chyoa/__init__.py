#!/usr/bin/env python3

__all__ = ["main"]
__license__ = "MIT"

from .scraper import Scraper
from .util import get_elapsed_time

import os.path
import time

def main(argv=[__file__]):
    if len(argv) < 2:
        print("Usage: %s url [destination]" % os.path.basename(argv[0]))
        exit(1)

    url = argv[1]
    if len(argv) < 3:
        dest = "."
    else:
        dest = argv[2]

    if not Scraper.is_chyoa_url(url):
        print("warning: This does not look like a CHYOA url. They are usually")
        print("warning: in the form of \"https://chyoa.com/story/NAME.ID\"")

    start = time.time()
    scraper = Scraper(argv[1])
    scraper.scrape()
    #TODO
    print("Finished in %s." % get_elapsed_time(time.time() - start))

