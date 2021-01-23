import cv2
import numpy as np 
import pytesseract
import os
from PIL import Image
class Template:
	def __init__(self , path):
		self.image = cv2.imread(path)
		self.boxes =[]
		self.names = []

	def addField(self , box, name):
		self.boxes.append(box)
		self.names.append(name)
	def removeField(self, name):
		self.boxes.pop(self.names.index(name))
		self.names.pop(self.names.index(name))


def getText(path):

	pass


def getText(path, template):
	dictionary={}
	image = cv2.imread(path)
	for idx,i in enumerate(template.boxes):

		dictionary[template.names[idx]]= pytesseract.image_to_string(image[int(i[1]):int(i[1]+i[3]), int(i[0]):int(i[0]+i[2])]).strip()
	return dictionary

def setTemplate(path):
	image = cv2.imread(path)
	temp = Template(path)
	cv2.imshow('template', image)


	count = 0
	while(True):	
		
	
		box = cv2.selectROI("roi", image,False)
		
		if( box[2:]!=(0,0)):
			temp.addField(box, count)
			count+=1
			

		if cv2.waitKey(0) ==ord('q'):

			break
	return temp
temp=setTemplate("receipt.jpg")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
print(getText("receipt.jpg", temp))
	
	