from wand.image import Image as Img
from PIL import Image
from pytesseract import image_to_string

import argparse
import pprint
import langid
import statistics
import time

def get_language(doc_id,path):
	language_list = []
	count = 0
	imagename = '/tmp/temp.png'
	try:
		with(Img(filename=path,resolution=300)) as source:
			time_out = time.time() + 30
			while time.time() <= time_out:
				source.compression_quality = 99 
				images=source.sequence
				pages=len(images)
				for i in range(pages):
					count += 1
					Img(images[i]).save(filename=imagename)
					text = image_to_string(Image.open(imagename))
					if (text.strip()):
						(language,waight) =  langid.classify(text)
						language_list.append(language)
					else:
						language_list.append("*")
					if count == 6:
						return statistics.mode(language_list)
		if count == 0:
			language_list.append("difficult")
			print("Difficult document: " + doc_id + " - " + path)
		return statistics.mode(language_list)
	except:
		print("Document Error: " + doc_id + " - " + path)
		return
	
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required=True,
help="path to pdf file")
args = vars(ap.parse_args())
example_file = args["filename"]

if example_file:
	language = get_language("Local",example_file)
	print(language)
else:
	print("File missing")