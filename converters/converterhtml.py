from converter import Converter
from decorators import DocInherit
import os
from IPython.utils import path
from markdown import markdown
from utils.utils import highlight, coalesce_streams, ansi2html
import io
#------------------------
# decorators
#------------------------

def text_cell(f):
    """wrap text cells in appropriate divs"""
    def wrapped(self, cell):
        rendered = f(self, cell)
        classes = "text_cell_render border-box-sizing rendered_html"
        lines = ['<div class="%s">' % classes] + rendered + ['</div>']
        return lines
    return wrapped

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


class ConverterHTML(Converter):
    extension = 'html'

    def in_tag(self, tag, src, attrs={}):
        """Return a list of elements bracketed by the given tag"""
        attr_s = ""
        for attr, value in attrs.iteritems():
            attr_s += "%s=%s" % (attr, value)
        return ['<%s %s>' % (tag, attr_s), src, '</%s>' % tag]

    def _ansi_colored(self, text):
        return ['<pre>%s</pre>' % ansi2html(text)]

    def _stylesheet(self, fname):
        with io.open(fname, encoding='utf-8') as f:
            s = f.read()
        return self.in_tag('style', s, dict(type='text/css'))

    def _out_prompt(self, output):
        if output.output_type == 'pyout':
            n = output.prompt_number if output.prompt_number is not None else '&nbsp;'
            content = 'Out [%s]:' % n
        else:
            content = ''
        return ['<div class="prompt output_prompt">%s</div>' % content]

    def optional_header(self):
        from pygments.formatters import HtmlFormatter

        header = ['<html>', '<head>']

        static = os.path.join(path.get_ipython_package_dir(),
        'frontend', 'html', 'notebook', 'static',
        )
        here = os.path.split(os.path.abspath(__file__))[0]
        css = os.path.join(static, 'css')
        for sheet in [
            # do we need jquery and prettify?
            # os.path.join(static, 'jquery', 'css', 'themes', 'base', 'jquery-ui.min.css'),
            # os.path.join(static, 'prettify', 'prettify.css'),
            os.path.join(css, 'boilerplate.css'),
            os.path.join(css, 'fbm.css'),
            os.path.join(css, 'notebook.css'),
            os.path.join(css, 'renderedhtml.css'),
            # our overrides:
            os.path.join(here, 'css', 'static_html.css'),
        ]:
            header.extend(self._stylesheet(sheet))

        # pygments css
        pygments_css = HtmlFormatter().get_style_defs('.highlight')
        header.extend(['<meta charset="UTF-8">'])
        header.extend(self.in_tag('style', pygments_css, dict(type='text/css')))

        # TODO: this should be allowed to use local mathjax:
        header.extend(self.in_tag('script', '', {'type':'text/javascript',
            'src': '"https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS_HTML"',
        }))
        with io.open(os.path.join(here, 'js', 'initmathjax.js'), encoding='utf-8') as f:
            header.extend(self.in_tag('script', f.read(), {'type': 'text/javascript'}))

        header.extend(['</head>', '<body>'])

        return header

    def optional_footer(self):
        lines = []
        lines.extend([
            '</body>',
            '</html>',
        ])
        return lines

    @DocInherit
    @text_cell
    def render_heading(self, cell):
        marker = cell.level
        return [u'<h{1}>\n  {0}\n</h{1}>'.format(cell.source, marker)]

    @DocInherit
    def render_code(self, cell):
        if not cell.input:
            return []

        lines = ['<div class="cell border-box-sizing code_cell vbox">']

        lines.append('<div class="input hbox">')
        n = cell.prompt_number if getattr(cell, 'prompt_number', None) is not None else '&nbsp;'
        lines.append('<div class="prompt input_prompt">In [%s]:</div>' % n)
        lines.append('<div class="input_area box-flex1">')
        lines.append(highlight(cell.input))
        lines.append('</div>') # input_area
        lines.append('</div>') # input

        if cell.outputs:
            lines.append('<div class="vbox output_wrapper">')
            lines.append('<div class="output vbox">')

            for output in coalesce_streams(cell.outputs):
                conv_fn = self.dispatch(output.output_type)
                lines.extend(conv_fn(output))

            lines.append('</div>') # output
            lines.append('</div>') # output_wrapper

        lines.append('</div>') # cell

        return lines

    @DocInherit
    @text_cell
    def render_markdown(self, cell):
        return [markdown(cell.source)]

    @DocInherit
    def render_raw(self, cell):
        if self.raw_as_verbatim:
            return self.in_tag('pre', cell.source)
        else:
            return [cell.source]

    @DocInherit
    @output_container
    def render_pyout(self, output):
        for fmt in ['html', 'latex', 'png', 'jpeg', 'svg', 'text']:
            if fmt in output:
                conv_fn = self.dispatch_display_format(fmt)
                return conv_fn(output)
        return []

    render_display_data = render_pyout

    @DocInherit
    @output_container
    def render_stream(self, output):
        return self._ansi_colored(output.text)


    @DocInherit
    @output_container
    def render_pyerr(self, output):
        # Note: a traceback is a *list* of frames.
        # lines = []

        # stb =
        return self._ansi_colored('\n'.join(output.traceback))

    @DocInherit
    def _img_lines(self, img_file):
        return ['<img src="%s">' % img_file, '</img>']

    @DocInherit
    def _unknown_lines(self, data):
        return ['<h2>Warning:: Unknown cell</h2>'] + self.in_tag('pre', data)


    @DocInherit
    def render_display_format_png(self, output):
        return ['<img src="data:image/png;base64,%s"></img>' % output.png]

    @DocInherit
    def render_display_format_svg(self, output):
        return [output.svg]

    @DocInherit
    def render_display_format_jpeg(self, output):
        return ['<img src="data:image/jpeg;base64,%s"></img>' % output.jpeg]

    @DocInherit
    def render_display_format_text(self, output):
        return self._ansi_colored(output.text)

    @DocInherit
    def render_display_format_html(self, output):
        return [output.html]

    @DocInherit
    def render_display_format_latex(self, output):
        return [output.latex]

    @DocInherit
    def render_display_format_json(self, output):
        # html ignores json
        return []


    @DocInherit
    def render_display_format_javascript(self, output):
        return [output.javascript]


