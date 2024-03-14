import tempfile
import webbrowser
from pathlib import Path

import fpdf
from fpdf.fonts import FontFace

LOGO = Path(__file__).parent / "logo.png"


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

        # set to A4
        self.add_font("Arial", "", "c:\\windows\\fonts\\arial.ttf")
        self.set_font("Arial", "", 10)
        self.add_page(format="a4")

    def header(self):
        # draw revision and date on right side
        with self.use_font_face(FontFace(color=(0, 0, 0), emphasis="I", size_pt=8)):


            self.set_x(-50)
            self.set_y(2)
            self.multi_cell(w=0, h=self.fontsize, txt=self.title + ' - ' + str(self.date), align="R")

            self.set_fill_color((0, 0, 0))

    def footer(self):
        self.set_y(-10)

        with self.use_font_face(FontFace(color=(0, 0, 0), emphasis="I", size_pt=8)):
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

    def add_new_page_if_needed(self):
        """Adds a new page if we are below the middle of the page."""
        if self.get_y() > 0.5 * self.eph:
            self.add_page()

    def open(self, filename=None):
        # if no filename is supplied, make a temporary file
        if filename is None:
            filename = self.temp_folder / "report.pdf"

        self.output(name=filename)

        webbrowser.open(filename)
