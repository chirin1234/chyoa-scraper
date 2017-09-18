__all__ = ["write_story", "write_chapter", "write_zip"]

from zipfile import ZipFile
import codecs
import html
import json
import os
import tarfile
import tempfile
import urllib.parse

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<title>%s</title>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
<meta charset="UTF-8" />
%s
</head>
<body>
%%s
%s
%%s
</body>
</html>
"""


TOC_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<title>%s</title>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
<meta charset="UTF-8" />
%s
</head>
<body>
<ul>
%s
</ul>
</body>
</html>
"""






STORY_METADATA_TEMPLATE = """\
<meta name="author" content="%s" />
<meta name="tags" content="%s" />
<meta name="comment" content="%s" />
<meta name="pubdate" content="%s" />
<meta name="date of creation" content="%s" />
<meta name="publisher" content="chyoa.com" />
<meta name="url" content="url:%s" />
"""


CHAPTER_HEADER_TEMPLATE = """\
<center>
%s
<h1>%s</h1>
%s
%s
<h4>Chapter %s by <a href="https://chyoa.com/user/%s">%s</a></h4>
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
    prev_question = ""
    if chapter.prev_question is not None:
        prev_question = "<h2>%s</h2>" % chapter.prev_question
    subtitle = ""
    if hasattr(chapter, "subtitle"):
        subtitle = "<h2>%s</h2>" % chapter.subtitle

    if hasattr(chapter, "description"):
        description = "<h3>%s</h3>" % chapter.description
    else:
        description = ""
        
    return format_html(CHAPTER_HEADER_TEMPLATE,
            prev_question, name, subtitle, description, chapter.chapter_number, chapter.author.strip(), chapter.author.strip())

def generate_chapter_links(chapter, chapter_pool):
    links = []

    for choice_id, choice_url in chapter.choices:
        (_, _, choice_path) = choice_url.rpartition('/')
        choice_path = choice_path.replace('%22', '_')
        if choice_id in chapter_pool.keys():
            name = chapter_pool[choice_id].name
        else:
            (choice_name, _, _) = choice_path.rpartition('.')
            name = urllib.parse.unquote(choice_name.replace('-','%20'))
        links.append("<li><a href=\"./%s.html\">%s</a>"
            % (choice_path, html.escape(name)))

    return format_html(CHAPTER_LINKS_TEMPLATE, chapter.question, "\n".join(links))

def write_story(story, dest_dir):
    data = {
        "title": story.title,
        "description": story.description.replace("\r\n", "\n"),
        "author": story.author,
        "root": story.id,
        "url": story.url,
        "tags": story.tags,
        "file_path": story.file_path,
        "created": story.created,
        "modified": story.modified,
        "chapter_number": story.chapter_number,
        "subtitle": story.subtitle,
    }

    story_path = os.path.join(dest_dir, "meta.json")
    index_path = os.path.join(dest_dir, "index.html")

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    with codecs.open(story_path, "w", "utf-8") as fh:
        json.dump(data, fh)

    with codecs.open(index_path, "w", "utf-8") as fh:
        fh.write(generate_toc(story))


    write_chapter(story, dest_dir, story.chapters)
    for chapter in story.chapters.values():
        write_chapter(chapter, dest_dir)

def generate_toc(story):
    # Calibre's html import by default is kinda screwy and won't import
    #  more than five levels of html files by default and it's difficult 
    #  to override. This obviously won't work with chyoa stories that 
    #  are dozens or hundreds of chapters deep, so just write out a TOC
    #  file with links to all the chapters.
    retval = TOC_TEMPLATE % \
        (story.title, get_metadata(story), '\n'.join(get_all_links(story)))
    return retval

def get_all_links(story):
    retval = [get_link(story)]
    for chapter in story.chapters.values():
        retval.append(get_link(chapter))
    return retval

def get_link(chapter):
    return '<li><a href="./%s.html">%s</a></li>' % (urllib.parse.quote(chapter.file_path),chapter.name)


def write_chapter(chapter, dest_dir, chapter_pool={}):
    metadata = {
        "name": chapter.name,
        "author": chapter.author,
        "id": chapter.id,
        "question": chapter.question,
        "tags" : chapter.tags,
        "file_path": chapter.file_path,
        "url": chapter.url,
        "prev_question": chapter.prev_question,
        "chapter_number": chapter.chapter_number,
    }

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    choice_ids = []
    for choice in chapter.choices:
        (_, _, choice_name) = choice[1].rpartition('/')
        choice_name = choice_name.replace('%22', '_')
        choice_ids.append(choice_name)

    metadata["choices"] = choice_ids
    name = chapter.name
    if hasattr(chapter, "title"):
        name = chapter.title
        metadata["title"] = chapter.title
        metadata["description"] = chapter.description
        # apply meta tags so calibre will generate meaningful metadata

    meta_tags = get_metadata(chapter)

    html_data = format_html(HTML_TEMPLATE, name, meta_tags, chapter.text)
    html_data = html_data % (generate_chapter_header(chapter), generate_chapter_links(chapter, chapter_pool))
    if "<li>" not in html_data:
        # the empty ul tag breaks calibre's parsing, so remove 'em
        html_data = html_data.replace("<ul>\n\n</ul>", "")
    metadata_path = os.path.join(dest_dir, "%s.json" % chapter.file_path)
    html_path = os.path.join(dest_dir, "%s.html" % chapter.file_path)

    with codecs.open(metadata_path, "w", "utf-8") as fh:
        json.dump(metadata, fh)

    with codecs.open(html_path, "w", "utf-8") as fh:
        fh.write(html_data)

def get_metadata(chapter):
    description = ''
    if hasattr(chapter, "description"):
        description = chapter.description
    meta_tags = STORY_METADATA_TEMPLATE % \
        (chapter.author, ','.join(chapter.tags), description, chapter.modified, chapter.created, chapter.url)
    meta_tags = meta_tags.replace("%", "%%")
    return meta_tags

def write_tar(story, dest_file, compression="", is_story=True):
    temp_dir = tempfile.TemporaryDirectory()
    if is_story:
        write_story(story, temp_dir.name)
    else:
        write_chapter(story, temp_dir.name)

    with tarfile.open(dest_file, "w:%s" % compression.lower()) as tarfh:
        os.chdir(temp_dir.name)
        for fn in os.listdir(temp_dir.name):
            tarfh.add(fn)

def write_zip(story, dest_file, is_story=True):
    temp_dir = tempfile.TemporaryDirectory()
    if is_story:
        write_story(story, temp_dir.name)
    else:
        write_chapter(story, temp_dir.name)

    with ZipFile(dest_file, "w") as zipfh:
        os.chdir(temp_dir.name)
        for fn in os.listdir(temp_dir.name):
            zipfh.write(fn)

