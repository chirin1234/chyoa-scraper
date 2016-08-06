__all__ = ["Chapter", "ChapterReference"]

from .util import abridge
import re

CHAPTER_ID_REGEX = re.compile(r"^https://chyoa.com/[^.]+\.([0-9]+)$")

class Chapter(object):
    def __init__(self, title=None, id=None, author=None, text=None, question=None, choices=[]):
        self.title = title
        self.id = id
        self.author = author
        self.text = text
        self.question = question
        self.choices = choices

    def __repr__(self):
        return "Chapter(title=%r, author=%r, text=%r, question=%r, choices=%r)" % (
                self.title, self.author, abridge(self.text), self.question, self.choices)

class ChapterReference(object):
    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url

        if url:
            match = CHAPTER_ID_REGEX.match(url)
            if match is None:
                raise ValueError("Unable to extract chapter ID from URL (%s)" % url)

            self.id = int(match.group(1))
        else:
            self.id = None

    def __repr__(self):
        return "ChapterReference(name=%r, url=%r, id=%r)" % (
                self.name, self.url, self.id)

