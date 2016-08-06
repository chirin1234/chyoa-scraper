__all__ = ["write_story", "write_chapter", "write_zip"]

from zipfile import ZipFile
import json
import os
import tarfile
import tempfile

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<title>%s</title>
</head>
<body>
%s
</body>
</html>
"""

def write_story(story, dest_dir):
    data = {
        "title": story.title,
        "description": story.description.replace("\r\n", "\n"),
        "author": story.author,
        "root": story.id,
    }

    story_path = os.path.join(dest_dir, "meta.json")

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    with open(story_path, "w") as fh:
        json.dump(data, fh)

    write_chapter(story, dest_dir)
    for chapter in story.chapters.values():
        write_chapter(chapter, dest_dir)

def write_chapter(chapter, dest_dir):
    metadata = {
        "title": chapter.title,
        "author": chapter.author,
        "id": chapter.id,
        "question": chapter.question,
    }

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    choice_ids = []
    for choice in chapter.choices:
        choice_ids.append(choice[0])

    metadata["choices"] = choice_ids

    html = HTML_TEMPLATE % (chapter.title, chapter.text)

    metadata_path = os.path.join(dest_dir, "%s.json" % chapter.id)
    html_path = os.path.join(dest_dir, "%s.html" % chapter.id)

    with open(metadata_path, "w") as fh:
        json.dump(metadata, fh)

    with open(html_path, "w") as fh:
        fh.write(html)

def write_tar(story, dest_file, compression=""):
    temp_dir = tempfile.TemporaryDirectory()
    write_story(story, temp_dir.name)

    with tarfile.open(dest_file, "w:%s" % compression.lower()) as tarfh:
        os.chdir(temp_dir.name)
        for fn in os.listdir(temp_dir.name):
            tarfh.add(fn)

def write_zip(story, dest_file):
    temp_dir = tempfile.TemporaryDirectory()
    write_story(story, temp_dir.name)

    with ZipFile(dest_file, "w") as zipfh:
        os.chdir(temp_dir.name)
        for fn in os.listdir(temp_dir.name):
            zipfh.write(fn)

