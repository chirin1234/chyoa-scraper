#!/usr/bin/env python3

__all__ = ["main"]
__license__ = "MIT"

from .scraper import Scraper
from .serial import write_story, write_tar, write_zip
from .util import get_elapsed_time

import os.path
import re
import time

ZIP_FILE_REGEX = re.compile(r".*\.zip", re.IGNORECASE)
TAR_FILE_REGEX = re.compile(r".*\.tar(?:\.([a-z]+)|)", re.IGNORECASE)

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
    scraper = Scraper()
    scraper.scrape(argv[1])
    story = scraper.story

    if ZIP_FILE_REGEX.fullmatch(dest):
        write_zip(story, dest)
    else:
        match = TAR_FILE_REGEX.fullmatch(dest)
        if match:
            compression = match.group(1)
            if compression:
                write_tar(story, dest, compression)
            else:
                write_tar(story, dest)
        else:
            write_story(story, dest)

    print("Finished in %s." % get_elapsed_time(time.time() - start))

