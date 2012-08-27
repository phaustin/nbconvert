
class ConverterPy(Converter):
    """
    A converter that takes a notebook and converts it to a .py file.

    What distinguishes this from PyWriter and PyReader in IPython.nbformat is
    that subclasses can specify what to do with each type of cell.
    Additionally, unlike PyWriter, this does not preserve the '# <markdown>'
    opening and closing comments style comments in favor of a cleaner looking
    python program.

    Note:
        Even though this produces a .py file, it is not guaranteed to be valid
        python file, since the notebook may be using magics and even cell
        magics.
    """
    extension = 'py'

    def __init__(self, infile, show_prompts=True, show_output=True):
        super(ConverterPy, self).__init__(infile)
        self.show_prompts = show_prompts
        self.show_output = show_output

    @staticmethod
    def comment(input):
        "returns every line in input as commented out"
        return "# "+input.replace("\n", "\n# ")

    @DocInherit
    def render_heading(self, cell):
        return ['#{0} {1}'.format('#'*cell.level, cell.source), '']

    @DocInherit
    def render_code(self, cell):
        if not cell.input:
            return []
        lines = []
        if self.show_prompts:
            lines.extend(['# In[%s]:' % cell.prompt_number])
        src = cell.input
        lines.extend([src, ''])
        if self.show_output:
            if cell.outputs :
                lines.extend(['# Out[%s]:' % cell.prompt_number])
            for output in cell.outputs:
                conv_fn = self.dispatch(output.output_type)
                lines.extend(conv_fn(output))
        return lines

    @DocInherit
    def render_markdown(self, cell):
        return [self.comment(cell.source), '']

    @DocInherit
    def render_raw(self, cell):
        if self.raw_as_verbatim:
            return [self.comment(indent(cell.source)), '']
        else:
            return [self.comment(cell.source), '']

    @DocInherit
    def render_pyout(self, output):
        lines = []

        ## if 'text' in output:
        ##     lines.extend(['*Out[%s]:*' % output.prompt_number, ''])

        # output is a dictionary like object with type as a key
        if 'latex' in output:
            pass

        if 'text' in output:
            lines.extend([self.comment(indent(output.text)), ''])

        lines.append('')
        return lines

    @DocInherit
    def render_pyerr(self, output):
        # Note: a traceback is a *list* of frames.
        return [indent(remove_ansi('\n'.join(output.traceback))), '']

    @DocInherit
    def _img_lines(self, img_file):
        return [ self.comment('image file: %s' % img_file), '']

    @DocInherit
    def render_display_format_text(self, output):
        return [self.comment(indent(output.text))]

    @DocInherit
    def _unknown_lines(self, data):
        return [self.comment('Warning: Unknown cell'+ str(data))]

    @DocInherit
    def render_display_format_html(self, output):
        return [self.comment(output.html)]

    @DocInherit
    def render_display_format_latex(self, output):
        return []

    @DocInherit
    def render_display_format_json(self, output):
        return []

    @DocInherit
    def render_display_format_javascript(self, output):
        return []
