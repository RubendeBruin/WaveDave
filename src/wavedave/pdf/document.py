import tempfile
import webbrowser
from abc import abstractmethod
from pathlib import Path

import fpdf
from fpdf.fonts import FontFace

LOGO = Path(__file__).parent / "logo.png"

import os
import winreg


class ToPDFMixin:

    @abstractmethod
    def generate_pdf(self, report):
        pass

class Text(ToPDFMixin):

    def __init__(self, text, margin=9):
        self.text = text
        self.margin = margin

    def generate_pdf(self, report):
        report.set_x(report.l_margin + self.margin)
        report.write_html(self.text)

class Header(ToPDFMixin):

        def __init__(self, text, margin=9):
            self.text = text
            self.margin = margin

        def generate_pdf(self, report):
            report.set_x(report.l_margin + self.margin)
            with report.use_font_face(FontFace(size_pt=12, color=(0, 0, 0), emphasis="B")):
                report.write_html(self.text)
                report.ln()

class Image(ToPDFMixin):

        def __init__(self, filename):
            self.filename = filename

        def generate_pdf(self, report):
            report.set_x(report.l_margin)
            report.image(self.filename, w=report.epw )

class PageBreakIfNeeded(ToPDFMixin):

    def __init__(self, margin=0.5):
        self.margin = margin
    def generate_pdf(self, report):
        report._add_new_page_if_needed(self.margin)

class WaveDavePDF(fpdf.FPDF):
    def __init__(self):
        super().__init__()

        # make a temporary folder for saving the pictures
        self.temp_folder = Path(tempfile.mkdtemp())

        self.title = "Title"
        self.fontsize = 10

        self.date = "yesterday"
        self.project = "Project"
        self.author = "Author"

        # if on windows, add arial font
        if False and os.name == "nt":
            self.add_font("arial", "", fname = "c:/windows/fonts/arial.ttf")
            self.add_font("arial", "I", fname = "c:/windows/fonts/ariali.ttf")
            self.add_font("arial", "B", fname = "c:/windows/fonts/arialbd.ttf")

        # set to A4 and add arial font (note: only works on windows, on other systems it will default another font)
        self.set_font("arial", "", 10)

        self._produced = False

        self.sections : list[ToPDFMixin] = [] # report sections

    def add(self, section: ToPDFMixin):
        self.sections.append(section)

    def header(self):
        # draw revision and date on right side
        with self.use_font_face(FontFace(family='arial', color=(0, 0, 0), emphasis="I", size_pt=8)):


            self.set_x(-50)
            self.set_y(2)
            self.multi_cell(w=0, h=self.fontsize, txt=self.title + ' - ' + str(self.date), align="R")

            self.set_fill_color((0, 0, 0))

    def footer(self):
        self.set_y(-10)

        with self.use_font_face(FontFace(family='arial', color=(0, 0, 0), emphasis="I", size_pt=8)):
            # self.set_font(style='I', size=8)

            # Add a page number
            page = "PAGE " + str(self.page_no()) + "/{nb}"
            self.cell(w=0, h=5, txt=page, align="C")

            # Add number, project and author
            self.set_x(self.l_margin)
            self.set_y(-14)
            self.cell(w=0, h=5, txt=self.project, align="L")
            self.set_y(-10)
            self.set_x(self.l_margin)
            self.cell(w=0, h=5, txt="by: " + self.author, align="L")

        # Add the logo

        logo_x = self.epw + 3
        self.set_y(-18)
        self.image(LOGO, x=logo_x, w=15)

    def _add_new_page_if_needed(self, margin=0.5):
        """Adds a new page if we are below the middle of the page."""
        if self.get_y() > margin * self.eph:
            self.add_page()

    def open(self, filename=None):
        # if no filename is supplied, make a temporary file

        if not self._produced:
            self.produce()

        if filename is None:
            filename = self.temp_folder / "report.pdf"

        self.output(name=filename)

        webbrowser.open(filename)

    def produce(self):

        self.add_page(format="a4")

        for section in self.sections:
            section.generate_pdf(self)

        self._produced = True

    # === convenience methods ===

    def add_text(self, text):
        self.add(Text(text))

    def add_header(self, text):
        self.add(Header(text))

    def add_page_break(self):
        self.add(PageBreakIfNeeded(0.0))

    def add_image(self, filename):
        self.add(Image(filename))

if __name__ == '__main__':
    d = WaveDavePDF()

    # define the report metadata
    d.author = "Ping-pong tafel"
    d.title = "Simple report"
    d.project = "WaveDave example project"
    d.date = "2024-03-11"

    # add some elements using the convenience methods
    d.add_header("Hello")
    d.add_text("This is a very simple report")
    d.add_text("Add more content by defining Graphs and adding them to the report")

    # or, using the add method
    # this enables some additional options such as margins
    # and is also use for adding elements for which no convenience method exists
    # such as graphs or standard report sections
    text_element = Text("<p>This text is added by first defining a Text object"
                        " and then adding it to the report."
                        "<br>Note that some basic HTML tags are supported,"
                        " like <b>bold</b> and <i>italic</i>."
                        "<br>Also, line breaks are supported.<br>Like this."
                        "<br>And this.</p>"
                        "<a href='https://youtu.be/CTDov_uGLss'>This is a link</a><br>"
                        "The `margin` argument is used to increase the margin"
                        , margin=20)
    d.add(text_element)

    d.add(Text("<p>Images from the internet can also be added using HTML:</p>"))
    d.add(Text("<img src = 'https://usedave.nl/_images/welcome_image.jpg' width=400>"))

    # but local is also an option
    d.add(Image("logo.png"))

    d.open()
