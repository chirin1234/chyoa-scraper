__all__ = ["ChyoaTree", "TreeCharset", "Tree", "STANDARD_TREE_CHARSET", "ASCII_TREE_CHARSET"]

import json
import os
import urllib.parse


class TreeCharset(object):
    def __init__(self, trunk, intersection, branch, corner):
        self.trunk = trunk
        self.intersection = intersection
        self.branch = branch
        self.corner = corner

STANDARD_TREE_CHARSET = TreeCharset("│", "├", "─", "└")
ASCII_TREE_CHARSET = TreeCharset("|", "|", "-", "`")

class Tree(object):
    def __init__(self, root, children):
        # Children in form {child: {grandchildren}}
        self.root = root
        self.children = children

    def display(self, charset=STANDARD_TREE_CHARSET):
        print(self.root)
        self.display_subtree(self.children, [], charset)

    def display_subtree(self, children, level, charset):
        child_list = list(children.keys())
        child_list.sort()

        for i in range(len(child_list)):
            notlast = (i < len(child_list) - 1)

            if notlast:
                corner = charset.intersection
            else:
                corner = charset.corner

            child = child_list[i]
            print("%s%s%s %s" %
                (self.get_indent(level, charset), corner, charset.branch, child))

            if children[child]:
                self.display_subtree(children[child], level + [notlast], charset)

    @staticmethod
    def get_indent(level, charset):
        separator = []

        for active in level:
            if active:
                separator.append("%s  " % charset.trunk)
            else:
                separator.append("    ")

        return "".join(separator)

class ChyoaTree(Tree):
    def __init__(self, path):
        prev_dir = os.getcwd()
        os.chdir(path)
        with open("meta.json", "r") as fh:
            meta = json.load(fh)

        name, tree = self.build_dict(meta["file_path"])
        Tree.__init__(self, name, tree)
        os.chdir(prev_dir)

    @staticmethod
    def build_dict(id):
        tree = {}

        with open("%s.json" % urllib.parse.unquote(id), "r") as fh:
            chapter = json.load(fh)

        name = chapter["name"]

        for child in chapter["choices"]:
            child_name, grandchildren = ChyoaTree.build_dict(child)
            tree[child_name] = grandchildren

        return name, tree

