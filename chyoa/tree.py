__all__ = ["ChyoaTree", "TreeCharset", "Tree", "STANDARD_TREE_CHARSET", "ASCII_TREE_CHARSET"]

from pprint import pprint
import json
import re
import os

class TreeCharset(object):
    def __init__(self, trunk, intersection, branch, corner):
        self.trunk = trunk
        self.intersection = intersection
        self.branch = branch
        self.corner = corner

STANDARD_TREE_CHARSET = TreeCharset("│", "├", "─", "└")
ASCII_TREE_CHARSET = TreeCharset("|", "|", "-", "`")

JSON_CHAPTER_FILE = re.compile(r'([0-9]+)\.json', re.IGNORECASE)

class Tree(object):
    def __init__(self, root_id, root_name):
        self.root_id = root_id
        self.root_name = root_name

    def get_children(self, id):
        # returns [(id, name)...]
        raise NotImplementedError("Invoking virtual method")

    def display(self, charset=STANDARD_TREE_CHARSET):
        print(self.root_name)
        stack = [(self.root_id, False)]

        while stack:
            children = self.get_children(stack.pop()[0])
            for i, (id, name) in enumerate(children):
                last = bool(i == (len(children) - 1))
                if last:
                    corner = charset.corner
                else:
                    corner = charset.intersection

                print(''.join((
                    self.get_indent(stack, charset),
                    corner,
                    charset.branch,
                    ' ',
                    name,
                )))
                self._push_children(stack, id)

    def _push_children(self, stack, id):
        children = self.get_children(id)
        for i, (id, name) in enumerate(children):
            last = bool(i == (len(children) - 1))
            stack.append((id, last))

    @staticmethod
    def get_indent(stack, charset):
        separator = []
        for child, last in stack:
            if last:
                separator.append(charset.trunk)
            else:
                separator.append(' ')
            separator.append('  ')
        return ''.join(separator)

class ChyoaTree(Tree):
    def __init__(self, path):
        self.objects = {}

        meta_fn = os.path.join(path, 'meta.json')
        with open(meta_fn, 'r') as fh:
            meta = json.load(fh)

        # Read in all chapter objects
        for fn in os.listdir(path):
            match = JSON_CHAPTER_FILE.match(fn)
            if match is None:
                continue
            id = int(match.group(1))
            with open(os.path.join(path, fn), 'r') as fh:
                obj = json.load(fh)
            self.objects[id] = obj
        Tree.__init__(self, meta['root'], self.objects[meta['root']]['name'])

    def get_children(self, id):
        l = []
        for child in self.objects[id]['choices']:
            l.append((child, self.objects[child]['name']))
        return l

