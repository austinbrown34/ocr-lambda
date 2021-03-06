import PyPDF2
import os


class PDFExtractor(object):
    @staticmethod
    def total_pages(pdf_path):
        num_pages = 0
        with open(pdf_path, 'rb') as f:
            pdf = PyPDF2.PdfFileReader(f)
            num_pages = pdf.getNumPages()
        return num_pages

    @staticmethod
    def get_text(pdf_path):
        with open(pdf_path, 'rb') as f:
            read_pdf = PyPDF2.PdfFileReader(f)
            number_of_pages = read_pdf.getNumPages()
            page = read_pdf.getPage(0)
            page_content = page.extractText()
            return page_content.encode('utf-8')

    @staticmethod
    def get_pages(pdf_path, folder):
        fname = os.path.splitext(os.path.basename(pdf_path))[0]
        with open(pdf_path, 'rb') as f:
            pdf = PyPDF2.PdfFileReader(f)
            for page in range(pdf.getNumPages()):
                pdf_writer = PyPDF2.PdfFileWriter()
                pdf_writer.addPage(pdf.getPage(page))
                output_filename = '{}_page_{}.pdf'.format(
                    fname,
                    page + 1
                )
                dst = os.path.join(folder, output_filename)
                with open(dst, 'wb') as out:
                    pdf_writer.write(out)

                print('Created: {}'.format(dst))

    @staticmethod
    def get_page(pdf_path, folder, page_num):
        fname = os.path.splitext(os.path.basename(pdf_path))[0]
        dst = ''
        with open(pdf_path, 'rb') as f:
            pdf = PyPDF2.PdfFileReader(f)
            pdf_writer = PyPDF2.PdfFileWriter()
            pdf_writer.addPage(pdf.getPage(page_num - 1))
            output_filename = '{}_page_{}.pdf'.format(
                fname,
                page_num
            )
            dst = os.path.join(folder, output_filename)
            with open(dst, 'wb') as out:
                pdf_writer.write(out)

            print('Created: {}'.format(dst))
        return dst
