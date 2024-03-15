from wavedave import *


report = WaveDavePDF()

report.header_text = "WaveDave4"

report.add_header("This is a header")

report.add(
    Text(
        "Some text, just because we can<p>This is HTML with limited support for tags. <b>bold</b> <i>italic</i> <u>underline</u> <br>line break",
    )
)

# or, easier

report.add_text('Text added with a convenience method')

report.open()
