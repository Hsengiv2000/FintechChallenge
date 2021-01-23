import cv2
import numpy as np 
import pytesseract
import os
from PIL import Image
from pymongo import MongoClient
from bson.objectid import ObjectId
import tkinter as tk
import urllib.request
import datetime
import csv
import xlrd
import pandas as pd
#import traceback

client = MongoClient('localhost', 27017)
db = client.fintech
templateCollection  = db.template
invoiceCollection = db.invoice
fraudCollection = db.fraud
print(templateCollection.find_one({'_id': ObjectId("600c5cd07e03a162d98eb1e5")}))
class CommodityPricing:
	#This class modified from https://github.com/datasets/commodity-prices/blob/master/scripts/process.py

	source = 'http://www.imf.org/external/np/res/commod/External_Data.xls'

	def setup(self):
		'''Crates the directories for archive and data if they don't exist
		
		'''
		if not os.path.exists('archive'):
			os.mkdir('archive')
		if not os.path.exists('data'):
			os.mkdir('data')

	def retrieve(self):
		'''Downloades xls data to archive directory
		
		'''
		urllib.request.urlretrieve(self.source,'archive/external-data.xls')

	def process(self):
		'''Gets the data from xls file and puts them in seperete csv files for each comoditie
		
		'''		
		
		header = [
			'Date',
			'All Commodity Price Index',
			'Non-Fuel Price Index',
			'Food and Beverage Price Index',
			'Food Price Index',
			'Beverage Price Index',
			'Industrial Inputs Price Index',
			'Agricultural Raw Materials Index',
			'Metals Price Index',
			'Fuel Energy Index',
			'Crude Oil petroleum',
			'Aluminum',
			'Bananas',
			'Barley',
			'Beef',
			'Coal',
			'Cocoa beans',
			'Coffee Other Mild Arabicas',
			'Coffee Robusta',
			'Rapeseed oil',
			'Copper',
			'Cotton',
			'Fishmeal',
			'Groundnuts peanuts',
			'Hides',
			'China import Iron Ore Fines 62% FE spot',
			'Lamb',
			'Lead',
			'Soft Logs',
			'Hard Logs',
			'Maize corn',
			'Natural Gas - Russian Natural Gas border price in Germany',
			'Natural Gas - Indonesian Liquefied Natural Gas in Japan',
			'Natural Gas - Spot price at the Henry Hub terminal in Louisiana',
			'Nickel',
			'Crude Oil - petroleum-simple average of three spot prices',
			'Crude Oil - petroleum - Dated Brent light blend',
			'Oil Dubai',
			'Crude Oil petroleum - West Texas Intermediate 40 API',
			'Olive Oil',
			'Oranges',
			'Palm oil',
			'Swine - pork',
			'Poultry chicken',
			'Rice',
			'Rubber',
			'Fish salmon',
			'Hard Sawnwood',
			'Soft Sawnwood',
			'Shrimp',
			'Soybean Meal',
			'Soybean Oil',
			'Soybeans',
			'Sugar European import price',
			'Sugar Free Market',
			'Sugar U.S. import price',
			'Sunflower oil',
			'Tea',
			'Tin',
			'Uranium',
			'Wheat',
			'Wool coarse',
			'Wool fine',
			'Zinc'
		]
		
		with xlrd.open_workbook('archive/external-data.xls') as xls_data:
			sheet= xls_data.sheet_by_index(0)
			col_num = sheet.ncols
			row_num = sheet.nrows
			with open('data/commodity-prices.csv', 'w') as csv_file:
				csvwriter = csv.writer(csv_file)
				csvwriter.writerow(header)
				for row in range(4, row_num):
					csv_row = []
					for col in range(col_num):
						if not col:				
							date = datetime.date(int(sheet.cell_value(row, col).split('M')[0]), int(sheet.cell_value(row, col).split('M')[1]), 1)		
							csv_row.append(date)
						else:
							price = sheet.cell_value(row, col)
							csv_row.append(price)
					csvwriter.writerow(csv_row)
			
class Template:
	def __init__(self , path):

		self.image = cv2.imread(path)
		self.boxes =[]
		self.names = []
		self.ObjectId = ""

	def addField(self , box, name):
		self.boxes.append(box)
		self.names.append(name)
	def removeField(self, name):
		self.boxes.pop(self.names.index(name))
		self.names.pop(self.names.index(name))
	def setParams(self, boxes, names):
		self.names = names
		self.boxes=boxes



def parseInvoice(path, templateID): 
	dictionary={}
	image = cv2.imread(path)
	template = templateCollection.find_one({'_id': ObjectId(templateID)})
	boxes =[]
	names = []
	fraudList=[]
	fraud = False
	for i in template:
		if i !='_id':
			names.append(i)
			boxes.append(template[i])
	print(names, boxes)
	for idx,i in enumerate(boxes):

		dictionary[names[idx]]= pytesseract.image_to_string(image[int(i[1]):int(i[1]+i[3]), int(i[0]):int(i[0]+i[2])]).strip()
		
		fraud = comparePrice(names[idx], float(dictionary[names[idx]].replace(",","")))
		if fraud == True:
			fraudList.append(names[idx])

	if len(fraudList) ==0:
		fraud= False
	else:
		fraud=True
	print(fraudList)
		


	if (invoiceCollection.find_one({'0':dictionary.get('0',None)})==None or invoiceCollection.find_one({'id':dictionary.get('id')})==None )and fraud==False: #verifies invoice
		invoiceCollection.insert_one(dictionary)
		return True, dictionary
	else:
		fraudCollection.insert_one(dictionary)
		return False, dictionary

def comparePrice(commodity, price):
	table = pd.read_csv("data/commodity-prices.csv")
	for i in table.keys():
		if commodity in i:
			commodity = i 
			break
	if commodity not in table.keys():
		return False #if it is an unknown commodity, we cannot check
	marketPrice =table[commodity][len(table[commodity])-1]
	if marketPrice> 1.5* price or  marketPrice*1.5< price: 
		return True
	return False

def setTemplate(path):
	image = cv2.imread(path)
	temp = Template(path)


	count = 0
	while(True):	
		
	
		box = cv2.selectROI("roi", image,False)
		
		if( box[2:]!=(0,0)):
			temp.addField(box, str(count))
			count+=1
			

		if cv2.waitKey(0) ==ord('q'):

			break

	root = tk.Tk()
	root.geometry("400x240")
	root.title("Enter the names of the boxes seperated by commas and then close")
	
	def getTextInput():
	    result=textExample.get("1.0","end")
	    result = result.strip().split(",")
	    textExample.delete("1.0","end")
	    for idx, i in enumerate(result):
	    	temp.names[idx] = i.strip()
	    
	    
	    print(result)

	textExample=tk.Text(root, height=10)
	textExample.pack()
	btnRead=tk.Button(root, height=1, width=10, text="Read", 
	                    command=getTextInput)

	btnRead.pack()

	root.mainloop()
	print(dict(zip(temp.names, temp.boxes)))
	templateCollection.insert_one(dict(zip(temp.names, temp.boxes))) 
	temp.ObjectId = ObjectId(templateCollection.find_one(dict(zip(temp.names, temp.boxes)))['_id'])
	print(temp.ObjectId)
	return temp


if 'archive' not in os.listdir():
	cp = CommodityPricing()
	cp.setup()
	cp.retrieve()
	cp.process()

#print(comparePrice('Crude Oil',20))
#temp=setTemplate("receipt.jpg")


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
print(parseInvoice("testreceipt.jpg", "600c6f9b1f9224279f486e61"))
