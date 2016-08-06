__all__ = ["ChyoaPageParser", "Scraper"]

from .chapter import Chapter, ChapterReference
from .story import Story
from .util import get_choice_names
from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse
import re
import sys

CHARSET_REGEX = re.compile(r"charset=([^ ]+)")
CHYOA_URL_REGEX = re.compile(r"^https://chyoa.com/story/[A-Za-z0-9\-_]+.[0-9]+$")
CHYOA_CHAPTER_REGEX = re.compile(r"^https://chyoa.com/chapter/[A-Za-z0-9\-_]+.[0-9]+$")
CHYOA_USER_REGEX = re.compile(r"^https://chyoa.com/user/([A-Za-z0-9\-_]+)$")

class ChyoaChapterParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

    def get_chapter(self, url):
        self.title = None
        self.description = None
        self.author = None
        self.in_body = False
        self.body = []
        self.in_question = False
        self.question = []
        self.in_choices = False
        self.current_choice = None
        self.choices = []

        if url.startswith(":"):
            filename = url[1:]
            print("Fetching file locally: %s" % filename)
            with open(filename, "r") as fh:
                html = fh.read()
        else:
            print("Fetching file remotely: %s" % url)
            response = urlopen(url)
            charset = self.get_charset(response.getheader("Content-Type"))
            html = response.read().decode(charset)

        self.feed(html)
        fields = {
            "title": self.title,
            "author": self.author,
            "text": "".join(self.body),
            "question": " ".join(self.question).strip(),
            "choices": self.choices,
        }

        if self.description:
            fields["description"] = self.description
            return Story(**fields)
        else:
            return Chapter(**fields)

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            for key, value in attrs:
                if key == "property" and value == "og:title":
                    self.title = dict(attrs)["content"]
                if key == "name" and value == "description":
                    self.description = dict(attrs)["content"]
        elif tag == "div":
            for key, value in attrs:
                if key == "class":
                    if value == "chapter-content":
                        self.in_body = True
                    elif value == "question-content":
                        self.in_choices = True
        elif tag == "header":
            for key, value in attrs:
                if key == "class" and value == "question-header":
                    self.in_question = True
        elif tag == "a":
            for key, value in attrs:
                if key == "href":
                    if self.in_choices and not value.endswith("login"):
                        self.current_choice = value
                    else:
                        match = CHYOA_USER_REGEX.match(value)
                        if match:
                            self.author = match.group(1)
        elif self.in_body:
            self.body.append("<%s>" % tag)

    def handle_data(self, data):
        if self.in_body:
            self.body.append(data)
        elif self.in_question:
            self.question.append(data.strip())
        elif self.in_choices:
            if self.current_choice:
                name = data.strip()
                self.choices.append(ChapterReference(name, self.current_choice))
                self.current_choice = None

    def handle_endtag(self, tag):
        if self.in_body:
            if tag == "div":
                self.in_body = False
            else:
                self.body.append("</%s>" % tag)
        elif self.in_question and tag == "header":
            self.in_question = False
        elif self.in_choices and tag == "div":
            self.in_choices = False

    def get_charset(self, header):
        if not header.startswith("text/html"):
            raise ValueError("Document type is not HTML")

        match = CHARSET_REGEX.findall(header)
        if match:
            return match[0]
        else:
            # Can't detect the charset, take a guess
            return "UTF-8"

class Scraper(object):
    def __init__(self, url):
        self.parser = ChyoaChapterParser()
        self.url = url
        self.visited = set()
        self.story = None
        self.chapters = {}
        self.resolved = False

    def scrape(self):
        self.story = self.parser.get_chapter(self.url)
        self.visited.add(self.url)

        print("Root chapter \"%s\":\n%s" % (self.story.title, get_choice_names(self.story.choices)))
        for ref in self.story.choices:
            self._scrape_chapter(ref.url, ref.id)

    def _scrape_chapter(self, url, id):
        if url in self.visited:
            print("(already visited %s)" % url)
            return

        chapter = self.parser.get_chapter(url)
        self.chapters[id] = chapter
        self.visited.add(url)

        print("Chapter \"%s\":\n%s" % (chapter.title, get_choice_names(chapter.choices)))
        for ref in chapter.choices:
            self._scrape_chapter(ref.url, ref.id)

    def resolve(self):
        print("Attaching root chapter...")
        root_ref = ChapterReference(self.story.title, self.url)
        self.story.attach(root_ref.id, self.chapters)
        self.resolved = True

    def get_story(self):
        if not self.resolved:
            raise ValueError("Chapter references are not resolved yet.")

        return self.story

    @staticmethod
    def is_chyoa_url(url):
        return bool(CHYOA_URL_REGEX.match(url))

