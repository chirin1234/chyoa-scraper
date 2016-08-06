### CHYOA Scraper
Currently [CHYOA](https://chyoa.com) has no way of exporting stories. This project's goal is to fix that. Hopefully the format it outputs is sane enough for other people to write their own formats if they wish.

#### Usage
This program uses Python 3. You can either import it as a library, or run it from the command line:

`python -m chyoa chyoa-story-url [destination-path]`

By default the program stores the exported story in the current directory.

### File Format
Each story is serialized as multiple files within a directory. A file called `meta.json` will contain metadata about the story. All the other files are chapters, referenced by their CHYOA IDs. These files are unordered, allowing chapters to link to as many or as few other chapters as they wish. All that is needed to recreate the story is a reference to the root chapter, which is given in `meta.json`.

Each chapter is composed of two files: a JSON file and an HTML file. The JSON file stores metadata about the chapter, such as the author and the avaible choices for the next chapter, while the HTML file stores the actual contents of the chapter.

#### License
Available under the terms of the MIT license. See `LICENSE`.

