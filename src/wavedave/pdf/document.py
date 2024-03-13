import tempfile
import webbrowser
from pathlib import Path

import fpdf

LOGO = Path(__file__).parent / 'logo.png'

class WaveDavePDF(fpdf.FPDF):


    def __init__(self, title = "WaveDave Report"):
        super().__init__()

        # make a temporary folder for saving the pictures
        self.temp_folder = Path(tempfile.mkdtemp())

        self.title = title

        # set to A4
        self.add_font('Arial', '', 'c:\\windows\\fonts\\arial.ttf')
        self.set_font('Arial', '', 10)
        self.add_page(format="a4")

    def header(self):
        self.set_x(-25)
        self.set_y(2)
        self.write_html(text=self.title)
        self.set_x(self.l_margin)

    def footer(self):
        # Add the logo
        logo_x = self.epw + 3
        self.set_y(-18)
        self.image(LOGO, x=logo_x, w=15)

    def add_new_page_if_needed(self):
        """Adds a new page if we are below the middle of the page."""
        if self.get_y() > 0.5* self.eph:
            self.add_page()

    def open(self, filename= None):

        # if no filename is supplied, make a temporary file
        if filename is None:
            filename = self.temp_folder / 'report.pdf'

        self.output(name=filename)

        webbrowser.open(filename)



