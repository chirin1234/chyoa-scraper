__all__ = ["Downloader"]

from .scraper import Scraper
from .serial import write_story, write_tar, write_zip, write_chapter
import re

ZIP_FILE_REGEX = re.compile(r".*\.zip", re.IGNORECASE)
TAR_FILE_REGEX = re.compile(r".*\.tar(?:\.([a-z]+)|)", re.IGNORECASE)

class Downloader(object):
    def __init__(self, recursive=True):
        self.recursive = recursive

    def download(self, url, dest, debug=False):
        if not Scraper.is_chyoa_url(url):
            print("warning: This does not look like a CHYOA url. They are usually")
            print("warning: in the form of \"https://chyoa.com/story/NAME.ID\"")

        if debug: print("Scraper().scrape(%s)" % url)
        scraper = Scraper()
        scraper.scrape(url, self.recursive)
        story = scraper.story
        if debug: print("story: %s" % story)

        if ZIP_FILE_REGEX.fullmatch(dest):
            if debug: print("%s: zip file" % dest)
            write_zip(story, dest, is_story=self.recursive)
        else:
            if debug: print("%s: tar file" % dest)
            match = TAR_FILE_REGEX.fullmatch(dest)
            if match:
                compression = match.group(1)
                if compression:
                    if debug: print("%s: tar.%s file" % (dest, compression))
                    write_tar(story, dest, compression, is_story=self.recursive)
                else:
                    write_tar(story, dest, is_story=self.recursive)
            elif self.recursive:
                if debug: print("%s: no compression" % dest)
                write_story(story, dest)
            else:
                if debug: print("%s: no compression (chapter)" % dest)
                write_chapter(story, dest)

