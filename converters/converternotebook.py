from converter import Converter
from decorators import DocInherit
from shutil import rmtree
from utils.utils import cell_to_lines
import json

class ConverterNotebook(Converter):
    """
    A converter that is essentially a null-op.
    This exists so it can be subclassed
    for custom handlers of .ipynb files 
    that create new .ipynb files.

    What distinguishes this from JSONWriter is that
    subclasses can specify what to do with each type of cell.

    Writes out a notebook file.

    """
    extension = 'ipynb'

    def __init__(self, infile, outbase):
        Converter.__init__(self, infile)
        self.outbase = outbase
        rmtree(self.files_dir)

    def convert(self):
        return unicode(json.dumps(json.loads(Converter.convert(self, ',')), indent=1, sort_keys=True))

    def optional_header(self):
        s = \
"""{
 "metadata": {
 "name": "%(name)s"
 },
 "nbformat": 3,
 "worksheets": [
 {
 "cells": [""" % {'name':self.outbase}

        return s.split('\n')

    def optional_footer(self):
        s = \
"""]
  }
 ]
}"""
        return s.split('\n')

    @DocInherit
    def render_heading(self, cell):
        return cell_to_lines(cell)

    @DocInherit
    def render_code(self, cell):
        return cell_to_lines(cell)

    @DocInherit
    def render_markdown(self, cell):
        return cell_to_lines(cell)

    @DocInherit
    def render_raw(self, cell):
        return cell_to_lines(cell)

    @DocInherit
    def render_pyout(self, output):
        return cell_to_lines(output)

    @DocInherit
    def render_pyerr(self, output):
        return cell_to_lines(output)

    @DocInherit
    def render_display_format_text(self, output):
        return [output.text]

    @DocInherit
    def render_display_format_html(self, output):
        return [output.html]

    @DocInherit
    def render_display_format_latex(self, output):
        return [output.latex]

    @DocInherit
    def render_display_format_json(self, output):
        return [output.json]


    @DocInherit
    def render_display_format_javascript(self, output):
        return [output.javascript]

