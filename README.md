Formproject is about publishing translations for german official forms. They
are supposed to help refugees and migrants to cope with the german
administrative chaos.

The translations this is based on are published by [KuB
Berlin](//www.kub-berlin.org/formularprojekt/). They are created by volunteers
and are not official.

This repository contains

-   form transcriptions (see [Transcribe forms](#transcribe-forms))
-   translations in CSV format (`data/`)
-   a python tool to format those translations. (If you have python3 installed,
    you can simply run `make`.)
-   a web application that aides in annotationg forms (see
    [Annotate forms](#annotate-forms))

# How to contribute

## Translate

The translations in this project are provided by
[KuB Berlin](//www.kub-berlin.org/). You can contribute as a translator via
[transifex](//www.transifex.com/kub/formulare/).

## Transcribe forms

Form transcriptions are stored in `data/*/form.json`. It contains of

-   a title
-   the list of strings (rows) and their position in the document
-   a URI of the official source document
-   the date of the last revision of that source document
-   the md5 checksum of the official form file it is based on
-   a list of externally available translations

If a row is a heading and has a number or similar (e.g. 1, 1.1, 1.1.2, A, B),
please provide that separately (in the JSON files this is called `structure`).
Please also note down on which page a row is (starting with 0).

You do not need to provide any of `align`, `x1`, `x2`, `y1`, or `y2`. This will
be handled in the step [annotate forms](#annotate-forms).

Here are some more tipps for transcription:

-   If there is empty space in a sentence (e.g. `Das Kind ____ ist ____ Jahre
    alt.`) do not split it into parts but leave it as a whole. This makes
    translation simpler.

-   If there is long running texts, create one row per paragraph.  You can use
    the `append` field on subsequent rows to make it behave like a single row
    in the annotation step. The value of the `append` field should be the
    string that is inserted before the row, e.g. `"\n\n"`.

-   Avoid additional whitespace in the strings.

-   You can use markdown to signify emphasis or other kinds of formatting.
    Simple emphasis is rendered as underline.

## Extract backgrounds

If a page in a form contains relevant lines or graphics, it is included in this
project as a background image located in `data/*/bg/`. It should be a SVG
file. It should be named `bg-{i}.svg` where `{i}` is the number of the page,
starting with 0.

One way to get those background images is to open a PDF in inkscape and
removing all text from it. Please leave all structural information (e.g. 1,
1.1, 1.1.2, A, B) intact as they help with orientation.

## Annotate forms

In order to display formatted versions of forms we need to know the positions
of each string on a page. To help with collecting this information, there is a
web application contained in this repository

### Installation

    git clone https://github.com/xi/formularprojekt.git
    apt install python3 npm
    cd formularprojekt
    make serve

Now you can go to <http://localhost:8000/> in your webbrowser. You should see
an index of available files.  On <http://localhost:8000/annotator/> you can now
access the annotator webapp.

### Usage

On the top right corner you can select which page of which form you want to
annotate. Once you have selected one, you can select a row in the right column.

You can now position the string either by clicking in the left column (click
sets the top left corner, ctrl-click sets the bottom right corner of the first
line). You can also tweak the value by using the input fields in the right
column. These are: `x1`, `x2`, `width`, `y1`, `y2`, `fontsize`, `alignment`.

You can also click "update" in the top bar to reset the data to the latest
version on the server. This is useful in two cases:

-   You made a mistake and want to reset everything
-   The version on the server is newer than the one saved wih the annotator

When you are done, you can export the annotated form.json by clicking "export"
in the top bar.
