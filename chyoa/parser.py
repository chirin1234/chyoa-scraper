__all__ = ["ChapterParser"]

from .story import Chapter, Story
from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.error import HTTPError
import re

CHARSET_REGEX = re.compile(r"charset=([^ ]+)")
CHAPTER_ID_REGEX = re.compile(r"https://chyoa.com/[^.]+\.([0-9]+)")
CHYOA_CHAPTER_REGEX = re.compile(r"https://chyoa.com/chapter/[A-Za-z0-9\-_]+.[0-9]+")
CHYOA_USER_REGEX = re.compile(r"https://chyoa.com/user/([A-Za-z0-9\-_]+)")
CHAPTER_NUMBER_REGEX = re.compile(r'Chapter ([0-9]+?)')


class ChapterParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

    def _reset(self):
        self.name = None
        self.title = None
        self.description = None
        self.author = None
        self.in_body = False
        self.body = []
        self.in_question = False
        self.question = []
        self.in_choices = False
        self.current_choice = None
        self.choices = set()
        self.tags = []
        self.modified_time = None
        self.created_time = None
        self.in_story_header = False
        self.in_chapter_header = False
        self.in_cover = False
        self.in_meta = False
        self.subtitle = None
        self.prev_question = None
        self.chapter_number = None
        self.cover_url = None
        self.in_h2 = False

    def get_chapter_fields(self, url):
        self._reset()

        print("Reading %s..." % url)
        try:
            response = urlopen(url)
        except HTTPError as err:
            if err.code == 404:
                print("Chapter deleted, skipping...")
                return None
            else:
                raise

        charset = self.get_charset(response.getheader("Content-Type"))
        html = response.read().decode(charset)
        self.feed(html)

        return {
            "url": url,
            "name": self.name,
            "description": self.description,
            "id": self.get_id(url),
            "author": self.author,
            "text": "".join(self.body),
            "question": " ".join(self.question).strip(),
            "choices": self.choices,
            "tags": self.tags,
            "created_time": self.created_time,
            "modified_time": self.modified_time,
            "subtitle": self.subtitle,
            "prev_question": self.prev_question,
            "cover_url" : self.cover_url,
            "chapter_number" : self.chapter_number
        }

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            for key, value in attrs:
                if key == "property":
                    if value == "og:title":
                        self.name = dict(attrs)["content"]
                    elif value == "og:description":
                        self.description = dict(attrs)["content"]
                    elif value == "article:published_time":
                        self.created_time = dict(attrs)["content"]
                    elif value == "article:modified_time":
                        self.modified_time = dict(attrs)["content"]
                    elif value == "article:tag":
                        self.tags = [x.strip() for x in dict(attrs)["content"].split(',')]
                if key == "name" and value =="description":
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
                if key == "class" and value == "story-header":
                    self.in_story_header = True
                if key == "class" and value == "chapter-header":
                    self.in_chapter_header = True
                    
        elif tag == "a":
            for key, value in attrs:
                if key == "href":
                    if self.in_choices and not value.endswith("login"):
                        self.current_choice = value
                    else:
                        match = CHYOA_USER_REGEX.fullmatch(value)
                        if match:
                            self.author = match.group(1)
        elif tag == "h2":
            self.in_h2 = True
        elif tag == "img" and self.in_story_header and 'cover' in dict(attrs)["src"]:
            self.cover_url = dict(attrs)["src"]
        elif self.in_body:
            self.body.append(self.create_tag(tag, attrs))

    def handle_data(self, data):
        if self.in_story_header or self.in_chapter_header:
            match = CHAPTER_NUMBER_REGEX.search(data)
            if match:
                self.chapter_number = match.group(1)
        if self.in_h2:
            if self.in_story_header:
                self.subtitle = data
            elif self.in_chapter_header:
                self.prev_question = data
        if self.in_body:
            self.body.append(data)
        elif self.in_question:
            self.question.append(data.strip())
        elif self.in_choices:
            if self.current_choice:
                name = data.strip()
                self.choices.add((self.get_id(self.current_choice), self.current_choice))
                self.current_choice = None

    def handle_endtag(self, tag):
        if self.in_body:
            if tag == "div":
                self.in_body = False
            else:
                self.body.append("</%s>" % tag)
        elif self.in_question and tag == "header":
            self.in_question = False
        elif self.in_story_header and tag == "header":
            self.in_story_header = False
        elif self.in_chapter_header and tag == "header":
            self.in_chapter_header = False
        elif self.in_choices and tag == "div":
            self.in_choices = False
        elif tag == "h2":
            self.in_h2 = False

    @staticmethod
    def create_tag(tag, attrs):
        if attrs:
            parts = [""]
        else:
            parts = []

        for key, value in attrs:
            parts.append("%s=\"%s\"" % (key, value))

        return "<%s%s>" % (tag, " ".join(parts))

    @staticmethod
    def get_charset(header):
        if not header.startswith("text/html"):
            raise ValueError("Document type is not HTML")

        match = CHARSET_REGEX.findall(header)
        if match:
            return match[0]
        else:
            # Can't detect the charset, take a guess
            return "UTF-8"

    @staticmethod
    def get_id(url):
        match = CHAPTER_ID_REGEX.fullmatch(url)
        if match is None:
            raise ValueError("Unable to extract chapter ID from URL (%s)" % url)

        return int(match.group(1))

