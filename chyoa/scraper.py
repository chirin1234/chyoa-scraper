__all__ = ["ChyoaPageParser", "Scraper"]

from .chapter import Chapter, ChapterReference
from .story import Story
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

    def get_chapter(self, url):
        if url.startswith(":"):
            with open(url[1:], "r") as fh:
                html = fh.read()
        else:
            response = urlopen(url)
            charset = self.get_charset(response.getheader("Content-Type"))
            html = response.read().decode(charset)

        self.feed(html)
        fields = {
            "text": "".join(self.body),
            "author": self.author,
            "question": " ".join(self.question).strip(),
            "choices": self.choices,
        }

        if self.title and self.description:
            fields["title"] = self.title
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
                self.choices.append(ChapterReference(data.strip(), self.current_choice))

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

    def scrape(self):
        chapter = self.parser.get_chapter(self.url)
        self.visited.add(self.url)
        print(chapter)
        print(chapter.text)

    @staticmethod
    def is_chyoa_url(url):
        return bool(CHYOA_URL_REGEX.match(url))

