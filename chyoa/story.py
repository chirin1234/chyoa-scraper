__all__ = ["Chapter", "Story"]

from .util import abridge

class Chapter(object):
    def __init__(self, url, name, description, id, author, text, question, choices):
        self.url = url
        self.name = name.replace('%', '%%')
        self.id = id
        self.author = author.replace('%', '%%')
        self.text = text.replace('%', '%%')
        self.question = question.replace('%', '%%')
        self.choices = choices # set( (id, chapter_url) )

    def __repr__(self):
        return """Chapter(url=%r, name=%r, author=%r, text=%r, question=%r, choices=%s\n)""" % (
                self.url, self.name, self.author, abridge(self.text), self.question, self.choices)

class Story(Chapter):
    def __init__(self, **kwargs):
        Chapter.__init__(self, **kwargs)
        self.title = kwargs["name"]
        self.name = "Introduction"
        self.description = kwargs["description"]
        self.chapters = {}
        # chapters: { id: chapter_object }

    def __repr__(self):
        return """Story(title=%r, description=%r, root=%s\n)""" % (
                self.title, self.description, Chapter.__repr__(self))

