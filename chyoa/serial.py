__all__ = ["write_story", "write_chapter", "write_zip"]

from zipfile import ZipFile
import html
import json
import os
import tarfile
import tempfile

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<title>%s</title>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
<meta charset="UTF-8" />
</head>
<body>
%%s
%s
%%s
</body>
</html>
"""

CHAPTER_HEADER_TEMPLATE = """\
<center>
<h1>%s</h1>
<h3>%s</h3>
by <a href="%s">%s</a>
</center>
"""

CHAPTER_LINKS_TEMPLATE = """\
<h3>%s</h3>
<ul>
%s
</ul>
"""

def format_html(pattern, *args):
    escaped = []

    for arg in args:
        escaped.append(html.escape(arg))

    return pattern % tuple(args)

def generate_chapter_header(chapter):
    if hasattr(chapter, "title"):
        name = chapter.title
    else:
        name = chapter.name

    if hasattr(chapter, "description"):
        description = chapter.description
    else:
        description = ""

    return format_html(CHAPTER_HEADER_TEMPLATE,
            name, description, chapter.author, chapter.author)

def generate_chapter_links(chapter, chapter_pool):
    links = []

    for choice_id, choice_url in chapter.choices:
        if choice_id in chapter_pool.keys():
            name = chapter_pool[choice_id].name
        else:
            name = choice_url

        links.append("<li><a href=\"%s\">%s</a>"
                % (html.escape(choice_url), html.escape(name)))

    return format_html(CHAPTER_LINKS_TEMPLATE, chapter.question, "\n".join(links))

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

    write_chapter(story, dest_dir, story.chapters)
    for chapter in story.chapters.values():
        write_chapter(chapter, dest_dir)

def write_chapter(chapter, dest_dir, chapter_pool={}):
    metadata = {
        "name": chapter.name,
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

    html_data = format_html(HTML_TEMPLATE, chapter.name, chapter.text)
    html_data = html_data % (generate_chapter_header(chapter), generate_chapter_links(chapter, chapter_pool))

    metadata_path = os.path.join(dest_dir, "%s.json" % chapter.id)
    html_path = os.path.join(dest_dir, "%s.html" % chapter.id)

    with open(metadata_path, "w") as fh:
        json.dump(metadata, fh)

    with open(html_path, "w") as fh:
        fh.write(html_data)

def write_tar(story, dest_file, compression="", is_story=True):
    temp_dir = tempfile.TemporaryDirectory()
    if hasattr(story, "chapters"):
        write_story(story, temp_dir.name)
    else:
        write_chapter(story, temp_dir.name)

    with tarfile.open(dest_file, "w:%s" % compression.lower()) as tarfh:
        os.chdir(temp_dir.name)
        for fn in os.listdir(temp_dir.name):
            tarfh.add(fn)

def write_zip(story, dest_file, s_story=True):
    temp_dir = tempfile.TemporaryDirectory()
    if hasattr(story, "chapters"):
        write_story(story, temp_dir.name)
    else:
        write_chapter(story, temp_dir.name)

    with ZipFile(dest_file, "w") as zipfh:
        os.chdir(temp_dir.name)
        for fn in os.listdir(temp_dir.name):
            zipfh.write(fn)

