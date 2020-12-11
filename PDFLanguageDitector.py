from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed

import argparse
import io
import pprint
import langid
import statistics
import time
from datetime import datetime

def get_language(doc_id,path):
	laparams = LAParams()
	try:
		fp = open(path, 'rb')
		parser = PDFParser(fp)
		document = PDFDocument(parser)

		if not document.is_extractable:
			raise PDFTextExtractionNotAllowed

		rsrcmgr = PDFResourceManager()
		retstr = io.BytesIO()
		codec = 'utf-8'
		device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		language_list = []
		count = 1

		for page in PDFPage.create_pages(document):
			time_out = time.time() + 30
			while time.time() <= time_out:
				count += 1
				interpreter.process_page(page)
				text = retstr.getvalue()
				if (text.strip()):
					(language,waight) =  langid.classify(text)
					language_list.append(language)
				else:
					language_list.append("*")
				if count == 6:
					fp.close()
					return statistics.mode(language_list)
		fp.close()
		if count == 1:
			language_list.append("difficult")
			print("Difficult document: " + doc_id + " - " + path)
		return statistics.mode(language_list)
	except:
		print("Document missing: " + doc_id + " - " + path)
		return
	
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required=True,
help="path to pdf file")
args = vars(ap.parse_args())
example_file = args["filename"]

if example_file:
        language = get_language("Local",example_file)
else:
	print("Example file is missing")