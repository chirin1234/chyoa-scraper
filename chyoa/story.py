__all__ = ["Chapter", "Story"]

from .util import abridge

class Chapter(object):
    """
    Represents a chapter in a CHYOA story.
    The chapter tracks the contents of its part of the story, as well as the IDs of its children.
    """
    def __init__(self, title=None, id=None, author=None, text=None, question=None, choices=set()):
        self.title = title
        self.id = id
        self.author = author
        self.text = text
        self.question = question
        self.choices = choices

    def __repr__(self):
        return """Chapter(title=%r, author=%r, text=%r, question=%r, choices=%s\n)""" % (
                self.title, self.author, abridge(self.text), self.question, self.choices)

class Story(Chapter):
    def __init__(self, title=None, description=None, **kwargs):
        Chapter.__init__(self, **kwargs)
        self.title = title
        self.description = description
        self.chapters = {}

    def __repr__(self):
        return """Story(title=%r, description=%r, root=%s\n)""" % (
                self.title, self.description, Chapter.__repr__(self))

