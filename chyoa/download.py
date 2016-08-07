__all__ = ["Downloader"]

from .scraper import Scraper
from .serial import write_story, write_tar, write_zip
import re

ZIP_FILE_REGEX = re.compile(r".*\.zip", re.IGNORECASE)
TAR_FILE_REGEX = re.compile(r".*\.tar(?:\.([a-z]+)|)", re.IGNORECASE)

class Downloader(object):
    def __init__(self, recursive=True):
        self.recursive = recursive

    def download(self, url, dest):
        if not Scraper.is_chyoa_url(url):
            print("warning: This does not look like a CHYOA url. They are usually")
            print("warning: in the form of \"https://chyoa.com/story/NAME.ID\"")

            scraper = Scraper()
            scraper.scrape(url)
            story = scraper.story

            if ZIP_FILE_REGEX.fullmatch(dest):
                write_zip(story, dest, story=self.recursive)
            else:
                match = TAR_FILE_REGEX.fullmatch(dest)
                if match:
                    compression = match.group(1)
                    if compression:
                        write_tar(story, dest, compression, is_story=self.recursive)
                    else:
                        write_tar(story, dest, is_story=self.recursive)
                elif self.recursive:
                    write_story(story, dest)
                else:
                    write_chapter(story, dest)

