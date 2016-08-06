### CHYOA Scraper
Currently [CHYOA](https://chyoa.com) has no way of exporting stories. This project's goal is to fix that. Hopefully the format it outputs is sane enough for other people to write their own formats if they wish.

#### Usage
This program uses Python 3. You can run the program from the command line:

`python -m chyoa chyoa-story-url [destination-path]`

By default the program stores the exported story in the current directory. If an archive file is listed as the `destination-path` (e.g. `.zip`, `.tar.xz`) then the files are stored inside of the specified archive.

### API
You can also use this as a library. After adding the directory of this repository to your python path, simply do `import chyoa`.

The `Scraper` class: You initialize this with a URL to a CHYOA story, and then invoking `scrape()` will recursively fetch all the webpages of the child chapters until it has a full reconstruction of the story. This is then returned to you as a `Story` object.

The `ChapterParser` class: Use this if you want to only download a particular chapter or want to fetch chapters in some order not supported by `Scraper`. Once the parser is initialized, you just call `get_chapter()` and pass a URL. Note that this method may return a `Story` object if the chapter is the root in its chain.

The `Chapter` class: Represents a chapter in a story. It is mostly a container class, storing it's title, chapter ID, author, the body of the story as HTML, the question, and the possible choices in the form `(id, url)`.

The `Story` class: Represents a story. This is actually a subclass of `Chapter` since CHYOA "stories" can be thought of a root chapter that indirectly points to all its children via the `choices` field. It has additional information not present in the `Chapter` object, namely the `description` and a dictionary of all the gathered `Chapter` objects, which, when followed in the manner mentioned above, can recreate the entire story chain.

The `write_chapter` function: Serializes a `Chapter` object in the given destination directory, which is created if it does not exist. This will create two files: a JSON file that contains information about the chapter, and an HTML file that stores the actual contents of the chapter.

The `write_story` function: Essentially the same as `write_chapter`, except that it will invoke `write_chapter` on every child chapter as well. It also creates a file called `meta.json` that stores gathered metadata about the story. This file is what differentiates a "story" from a "pile of chapters", since it holds a reference to the root chapter. (Of course, you could always calculate the root by iterating through all the chapter objects and looking for one with no parents).

The `write_zip` function: The same as `write_story`, except that it stores the contents in a zip file.

The `write_tar` function: The same as `write_zip`, but for tar files. In addition, if the filename specifies a compression type (e.g. `my_story.tar.bz2`), then this function will apply that compression algorithm to the file.

### File Format
Each story is serialized as multiple files within a directory. A file called `meta.json` will contain metadata about the story. All the other files are chapters, referenced by their CHYOA IDs. These files are unordered, allowing chapters to link to as many or as few other chapters as they wish. All that is needed to recreate the story is a reference to the root chapter, which is given in `meta.json`.

Each chapter is composed of two files: a JSON file and an HTML file. The JSON file stores metadata about the chapter, such as the author and the avaible choices for the next chapter, while the HTML file stores the actual contents of the chapter.

#### License
Available under the terms of the MIT license. See `LICENSE`.

