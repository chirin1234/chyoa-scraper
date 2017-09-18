__all__ = ["Chapter", "Story"]

from .util import abridge
import urllib.parse

class Chapter(object):
    def __init__(self, **kwargs):
        #url, name, description, id, author, text, question, choices, tags, created_time, modified_time):
        self.url = kwargs["url"]
        self.name = kwargs["name"].replace('%', '%%')
        self.id = kwargs["id"]
        self.author = kwargs["author"].replace('%', '%%')
        self.text = kwargs["text"].replace('%', '%%')
        self.question = kwargs["question"].replace('%', '%%')
        self.choices = kwargs["choices"] # set( (id, chapter_url) )
        (_,_,path) = kwargs["url"].rpartition('/')
        # strip quotes out of the filesystem name because windows will choke on them
        self.file_path = urllib.parse.unquote(path).replace('"', '_')
        self.modified = kwargs["modified_time"]
        self.created = kwargs["created_time"]
        self.tags = kwargs["tags"]
        self.prev_question = kwargs["prev_question"]
        self.chapter_number = kwargs["chapter_number"]

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
        self.subtitle = kwargs["subtitle"]

    def __repr__(self):
        return """Story(title=%r, description=%r, root=%s\n)""" % (
            self.title, self.description, Chapter.__repr__(self))
