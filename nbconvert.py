#!/usr/bin/env python
"""Convert IPython notebooks to other formats, such as ReST, and HTML.

Example:
  ./nbconvert.py --format rst file.ipynb

Produces 'file.rst', along with auto-generated figure files
called nb_figure_NN.png.
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function


# From IPython
from IPython.external import argparse

# local

from converters.converterrst import ConverterRST
from converters.converterhtml import ConverterHTML
from converters.converterlatex import ConverterLaTeX
from converters.convertermarkdown import ConverterMarkdown
from converters.converterpy import ConverterPy


#-----------------------------------------------------------------------------
# Class declarations
#-----------------------------------------------------------------------------




known_formats = "rst (default), html, latex, markdown, py"

def main(infile, fmt='rst'):
    """Convert a notebook to html in one step"""
    # XXX: this is just quick and dirty for now. When adding a new format,
    # make sure to add it to the `known_formats` string above, which gets
    # printed in in the catch-all else, as well as in the help
    if fmt == 'rst':
        converter = ConverterRST(infile)
        converter.render()
    elif fmt == 'markdown':
        converter = ConverterMarkdown(infile)
        converter.render()
    elif fmt == 'html':
        converter = ConverterHTML(infile)
        converter.render()
    elif fmt == 'latex':
        converter = ConverterLaTeX(infile)
        converter.render()
    elif fmt == 'py':
        converter = ConverterPy(infile)
        converter.render()
    else:
        raise SystemExit("Unknown format '%s', " % fmt +
                "known formats are: " + known_formats)

#-----------------------------------------------------------------------------
# Script main
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawTextHelpFormatter)
    # TODO: consider passing file like object around, rather than filenames
    # would allow us to process stdin, or even http streams
    # parser.add_argument('infile', nargs='?',
    #                    type=argparse.FileType('r'), default=sys.stdin)

    #Require a filename as a positional argument
    parser.add_argument('infile', nargs=1)
    parser.add_argument('-f', '--format', default='rst',
                        help='Output format. Supported formats: \n' +
                        known_formats)
    args = parser.parse_args()
    main(infile=args.infile[0], fmt=args.format)
