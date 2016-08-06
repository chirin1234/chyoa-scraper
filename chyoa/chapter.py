__all__ = ["Chapter", "ChapterReference"]

from .util import abridge
from pprint import pformat
import re

CHAPTER_ID_REGEX = re.compile(r"^https://chyoa.com/[^.]+\.([0-9]+)$")

class Chapter(object):
    """
    Represents a chapter in a CHYOA story.
    A chapter can either be "loose" or "attached". A loose chapter is one who is not
    part of a story tree. It's id is None and is choice dictionary is composed only of
    chapter references, rather than actual chapters.
    """
    def __init__(self, title=None, author=None, text=None, question=None, choices=[]):
        self.title = title
        self.id = None
        self.author = author
        self.text = text
        self.question = question
        self.choices = choices

    def is_loose(self):
        return self.id is None

    def attach(self, id, chapter_pool):
        self.id = id

        real_choices = []
        for ref in self.choices:
            print("Resolving \"%s\" (id: %d)." % (ref.name, ref.id))
            real_choices.append(ref.resolve(chapter_pool))
        self.choices = real_choices

    def __repr__(self):
        return """Chapter(
        loose=%s,
        title=%r,
        author=%r,
        text=%r,
        question=%r,
        choices=%s\n)""" % (
                self.is_loose(), self.title, self.author,
                abridge(self.text), self.question, pformat(self.choices, indent=8))

class ChapterReference(object):
    """
    Represents a link to a chapter.
    A reference to a chapter is a child of a chapter that has not been resolved yet.
    """
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

    def resolve(self, chapter_pool):
        if self.id not in chapter_pool.keys():
            raise ValueError("Chapter reference does not exist: \"%s\" (id: %d)" % (self.name, self.id))

        chapter = chapter_pool[self.id]

        if chapter.is_loose():
            print("Chapter \"%s\" (id: %d) is loose, attaching..." % (self.name, self.id))
            chapter.attach(self.id, chapter_pool)

        return chapter

    def __repr__(self):
        return "ChapterReference(name=%r, url=%r, id=%r)" % (
                self.name, self.url, self.id)

