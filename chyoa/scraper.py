__all__ = ["Scraper"]

from .parser import ChapterParser
from .story import Chapter, Story
from .util import get_choice_names
import re

CHYOA_URL_REGEX = re.compile(r"^https://chyoa.com/story/[^ ]+\.[0-9]+$")

class Scraper(object):
    def __init__(self):
        self.parser = ChapterParser()
        self.story = None
        self.visited = set()
        self.to_visit = []

    def scrape(self, url):
        self.story = self.parser.get_chapter(url)
        self.visited.add(url)

        if not isinstance(self.story, Story):
            raise TypeError("The given URL points to a chapter, not a full story.")

        print("Story \"%s\":\nRoot \"%s\":\n%s" % (
            self.story.title, self.story.name, get_choice_names(self.story.choices)))

        self._scrape_urls(list(self.story.choices))

        while self.to_visit:
            self._scrape_urls(self.to_visit)

    def _scrape_urls(self, urls):
        new_to_visit = []

        for i in range(len(urls) - 1, -1, -1):
            id, url = urls[i]
            del urls[i]

            if url in self.visited:
                print("(already visited %s)" % url)
                continue

            self.visited.add(url)
            chapter = self.parser.get_chapter(url)
            if chapter is None:
                continue

            self.story.chapters[id] = chapter
            print("Chapter \"%s\":\n%s" % (chapter.name, get_choice_names(chapter.choices)))

            for id, url in chapter.choices:
                new_to_visit.append((id, url))

        self.to_visit = new_to_visit

    @staticmethod
    def is_chyoa_url(url):
        return bool(CHYOA_URL_REGEX.fullmatch(url))

