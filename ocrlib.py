from PIL import Image
import pytesseract
import cv2
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')
os.environ['LD_LIBRARY_PATH'] = LIB_DIR
os.environ['TESSDATA_PREFIX'] = SCRIPT_DIR
pytesseract.pytesseract.tesseract_cmd = r'{}'.format(os.path.join(SCRIPT_DIR, 'tesseract'))

class OCR(object):
    @staticmethod
    def get_text(image_path, preprocess=None):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if preprocess == "thresh":
            gray = cv2.threshold(gray, 0, 255,
        	   cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        elif preprocess == "blur":
            gray = cv2.medianBlur(gray, 3)

        filename = "/tmp/{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)
        text = pytesseract.image_to_string(Image.open(filename))
        os.remove(filename)
        return text
