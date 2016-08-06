__all__ = ["Story"]

from .chapter import Chapter

class Story(Chapter):
    def __init__(self, title=None, description=None, **kwargs):
        Chapter.__init__(self, **kwargs)
        self.title = title
        self.description = description

    def __repr__(self):
        return "Story(title=%r, description=%r, root=%r)" % (
                self.title, self.description, Chapter.__repr__(self))

