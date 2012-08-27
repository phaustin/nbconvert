from converter import Converter

class ConverterMarkdown(Converter):
    extension = 'md'

    def __init__(self, infile, highlight_source=True, show_prompts=False,
                 inline_prompt=False):
        super(ConverterMarkdown, self).__init__(infile)
        self.highlight_source = highlight_source
        self.show_prompts = show_prompts
        self.inline_prompt = inline_prompt

    @DocInherit
    def render_heading(self, cell):
        return ['{0} {1}'.format('#'*cell.level, cell.source), '']

    @DocInherit
    def render_code(self, cell):
        if not cell.input:
            return []
        lines = []
        if self.show_prompts and not self.inline_prompt:
            lines.extend(['*In[%s]:*' % cell.prompt_number, ''])
        if self.show_prompts and self.inline_prompt:
            prompt = 'In[%s]: ' % cell.prompt_number
            input_lines = cell.input.split('\n')
            src = prompt + input_lines[0] + '\n' + indent('\n'.join(input_lines[1:]), nspaces=len(prompt))
        else:
            src = cell.input
        src = highlight(src) if self.highlight_source else indent(src)
        lines.extend([src, ''])
        if cell.outputs and self.show_prompts and not self.inline_prompt:
            lines.extend(['*Out[%s]:*' % cell.prompt_number, ''])
        for output in cell.outputs:
            conv_fn = self.dispatch(output.output_type)
            lines.extend(conv_fn(output))

        #lines.append('----')
        lines.append('')
        return lines

    @DocInherit
    def render_markdown(self, cell):
        return [cell.source, '']

    @DocInherit
    def render_raw(self, cell):
        if self.raw_as_verbatim:
            return [indent(cell.source), '']
        else:
            return [cell.source, '']

    @DocInherit
    def render_pyout(self, output):
        lines = []
        
        ## if 'text' in output:
        ##     lines.extend(['*Out[%s]:*' % output.prompt_number, ''])

        # output is a dictionary like object with type as a key
        if 'latex' in output:
            pass

        if 'text' in output:
            lines.extend(['<pre>', indent(output.text), '</pre>'])

        lines.append('')
        return lines

    @DocInherit
    def render_pyerr(self, output):
        # Note: a traceback is a *list* of frames.
        return [indent(remove_ansi('\n'.join(output.traceback))), '']

    @DocInherit
    def _img_lines(self, img_file):
        return ['', '![](%s)' % img_file, '']
    
    @DocInherit
    def render_display_format_text(self, output):
        return [indent(output.text)]

    @DocInherit
    def _unknown_lines(self, data):
        return ['Warning: Unknown cell', data]

    @DocInherit
    def render_display_format_html(self, output):
        return [output.html]

    @DocInherit
    def render_display_format_latex(self, output):
        return ['LaTeX::', indent(output.latex)]

    @DocInherit
    def render_display_format_json(self, output):
        return ['JSON:', indent(output.json)]

    @DocInherit
    def render_display_format_javascript(self, output):
        return ['JavaScript:', indent(output.javascript)]


def return_list(x):
    """Ensure that x is returned as a list or inside one"""
    return x if isinstance(x, list) else [x]


# decorators for HTML output
def output_container(f):
    """add a prompt-area next to an output"""
    def wrapped(self, output):
        rendered = f(self, output)
        if not rendered:
            # empty output
            return []
        lines = []
        lines.append('<div class="hbox output_area">')
        lines.extend(self._out_prompt(output))
        classes = "output_subarea output_%s" % output.output_type
        if output.output_type == 'stream':
            classes += " output_%s" % output.stream
        lines.append('<div class="%s">' % classes)
        lines.extend(rendered)
        lines.append('</div>') # subarea
        lines.append('</div>') # output_area
        
        return lines
    
    return wrapped

def text_cell(f):
    """wrap text cells in appropriate divs"""
    def wrapped(self, cell):
        rendered = f(self, cell)
        classes = "text_cell_render border-box-sizing rendered_html"
        lines = ['<div class="%s">' % classes] + rendered + ['</div>']
        return lines
    return wrapped

