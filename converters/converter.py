class ConversionException(Exception):
    pass

class Converter(object):
    default_encoding = 'utf-8'
    extension = str()
    figures_counter = 0
    infile = str()
    infile_dir = str()
    infile_root = str()
    files_dir = str()
    with_preamble = True
    user_preamble = None
    output = str()
    raw_as_verbatim = False
    
    def __init__(self, infile):
        self.infile = infile
        self.infile_dir, infile_root = os.path.split(infile)
        infile_root = os.path.splitext(infile_root)[0]
        files_dir = os.path.join(self.infile_dir, infile_root + '_files')
        if not os.path.isdir(files_dir):
            os.mkdir(files_dir)
        self.infile_root = infile_root
        self.files_dir = files_dir
        self.outbase = os.path.join(self.infile_dir, infile_root)

    def dispatch(self, cell_type):
        """return cell_type dependent render method,  for example render_code
        """
        return getattr(self, 'render_' + cell_type, self.render_unknown)

    def dispatch_display_format(self, format):
        """return output_type dependent render method,  for example render_output_text
        """
        return getattr(self, 'render_display_format_' + format, self.render_unknown_display)

    def convert(self, cell_separator='\n'):
        lines = []
        lines.extend(self.optional_header())
        converted_cells = []
        for worksheet in self.nb.worksheets:
            for cell in worksheet.cells:
                #print(cell.cell_type)  # dbg
                conv_fn = self.dispatch(cell.cell_type)
                if cell.cell_type in ('markdown', 'raw'):
                    remove_fake_files_url(cell)
                converted_cells.append('\n'.join(conv_fn(cell)))
        cell_lines = cell_separator.join(converted_cells).split('\n')
        lines.extend(cell_lines)
        lines.extend(self.optional_footer())
        return u'\n'.join(lines)

    def render(self):
        "read, convert, and save self.infile"
        if not hasattr(self, 'nb'):
            self.read()
        self.output = self.convert()
        return self.save()

    def read(self):
        "read and parse notebook into NotebookNode called self.nb"
        with open(self.infile) as f:
            self.nb = nbformat.read(f, 'json')

    def save(self, outfile=None, encoding=None):
        "read and parse notebook into self.nb"
        if outfile is None:
            outfile = self.outbase + '.' + self.extension
        if encoding is None:
            encoding = self.default_encoding
        with io.open(outfile, 'w', encoding=encoding) as f:
            f.write(self.output)
        return os.path.abspath(outfile)

    def optional_header(self):
        return []

    def optional_footer(self):
        return []

    def _new_figure(self, data, fmt):
        """Create a new figure file in the given format.

        Returns a path relative to the input file.
        """
        figname = '%s_fig_%02i.%s' % (self.infile_root, 
                                      self.figures_counter, fmt)
        self.figures_counter += 1
        fullname = os.path.join(self.files_dir, figname)

        # Binary files are base64-encoded, SVG is already XML
        if fmt in ('png', 'jpg', 'pdf'):
            data = data.decode('base64')
            fopen = lambda fname: open(fname, 'wb')
        else:
            fopen = lambda fname: codecs.open(fname, 'wb', self.default_encoding)
            
        with fopen(fullname) as f:
            f.write(data)
            
        return fullname

    def render_heading(self, cell):
        """convert a heading cell

        Returns list."""
        raise NotImplementedError

    def render_code(self, cell):
        """Convert a code cell

        Returns list."""
        raise NotImplementedError

    def render_markdown(self, cell):
        """convert a markdown cell

        Returns list."""
        raise NotImplementedError

    def _img_lines(self, img_file):
        """Return list of lines to include an image file."""
        # Note: subclasses may choose to implement format-specific _FMT_lines
        # methods if they so choose (FMT in {png, svg, jpg, pdf}).
        raise NotImplementedError

    def render_display_data(self, output):
        """convert display data from the output of a code cell

        Returns list.
        """
        lines = []

        for fmt in output.keys():
            if fmt in ['png', 'svg', 'jpg', 'pdf']:
                img_file = self._new_figure(output[fmt], fmt)
                # Subclasses can have format-specific render functions (e.g.,
                # latex has to auto-convert all SVG to PDF first).
                lines_fun = getattr(self, '_%s_lines' % fmt, None)
                if not lines_fun:
                    lines_fun = self._img_lines
                lines.extend(lines_fun(img_file))
            elif fmt != 'output_type':
                conv_fn = self.dispatch_display_format(fmt)
                lines.extend(conv_fn(output))
        return lines

    def render_raw(self, cell):
        """convert a cell with raw text

        Returns list."""
        raise NotImplementedError

    def render_unknown(self, cell):
        """Render cells of unkown type

        Returns list."""
        data = pprint.pformat(cell)
        logging.warning('Unknown cell: %s' % cell.cell_type)
        return self._unknown_lines(data)

    def render_unknown_display(self, output, type):
        """Render cells of unkown type

        Returns list."""
        data = pprint.pformat(output)
        logging.warning('Unknown output: %s' % output.output_type)
        return self._unknown_lines(data)

    def render_stream(self, output):
        """render the stream part of an output

        Returns list.

        Identical to render_display_format_text
        """
        return self.render_display_format_text(output)

    def render_pyout(self, output):
        """convert pyout part of a code cell

        Returns list."""
        raise NotImplementedError


    def render_pyerr(self, output):
        """convert pyerr part of a code cell

        Returns list."""
        raise NotImplementedError

    def _unknown_lines(self, data):
        """Return list of lines for an unknown cell.

        Parameters
        ----------
        data : str
          The content of the unknown data as a single string.
        """
        raise NotImplementedError

    # These are the possible format types in an output node

    def render_display_format_text(self, output):
        """render the text part of an output

        Returns list.
        """
        raise NotImplementedError

    def render_display_format_html(self, output):
        """render the html part of an output

        Returns list.
        """
        raise NotImplementedError

    def render_display_format_latex(self, output):
        """render the latex part of an output

        Returns list.
        """
        raise NotImplementedError

    def render_display_format_json(self, output):
        """render the json part of an output

        Returns list.
        """
        raise NotImplementedError

    def render_display_format_javascript(self, output):
        """render the javascript part of an output

        Returns list.
        """
        raise NotImplementedError


