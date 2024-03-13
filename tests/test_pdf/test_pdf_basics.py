from wavedave import WaveDavePDF

if __name__ == '__main__':
    pdf = WaveDavePDF()

    pdf.cell(40, 10, 'Hello World!')
    pdf.output('tuto1.pdf')

    # open the pdf in the browser
    import webbrowser
    webbrowser.open('tuto1.pdf')