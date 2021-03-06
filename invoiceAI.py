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

client = MongoClient('localhost', 27017)  #accessing the monogdb database
db = client.fintech #our main database is called fintech
templateCollection  = db.template #collection to store templates
invoiceCollection = db.invoice #collection to store approved invoices
fraudCollection = db.fraud #collection to store fraud invoices
class CommodityPricing: #this class scrapes data of picing for all the commodities and stores it in a csv file
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
			
class Template: #template object stores location of different parts of the template to be parsed
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



def parseInvoice(path, templateID):  #parsing invoicing
	dictionary={}
	if(isinstance(path,str)):
		image = cv2.imread(path) #if a path is provided, load the corresponding image
	else:
		image = cv2.imdecode(np.fromstring(path.read(), np.uint8), 1) #if an image is provided, convert it to opencv compatible format
		#image = path
	image = cv2.resize(image, (image.shape[1]//2 , image.shape[0]//2 )) #resize it for uniformity
	template = templateCollection.find_one({'_id': ObjectId(templateID)}) #Obtain the template data from the templatecollection to parse invoice
	boxes =[] #location of template to be parsed
	names = [] #different labels for the location such as iron, copper, total, tax etc
	fraudList=[] #list of under-invoicing / overinvoicing
	fraud = False
	for i in template:
		if i !='_id': #parse only the data and not the primary key
			names.append(i)
			boxes.append(template[i])
	#print(names, boxes)
	for idx,i in enumerate(boxes):

		dictionary[names[idx]]= pytesseract.image_to_string(image[int(i[1]):int(i[1]+i[3]), int(i[0]):int(i[0]+i[2])]).strip().replace("$","").replace("," , "").replace("}","").replace("{","").replace("&" , "")
		#print(dictionary)
		print(dictionary)
		try:
			fraud = comparePrice(names[idx], float(dictionary[names[idx]])) #compare prices of commodities with the excel sheet
		except:
			pass
		if fraud == True:
			fraudList.append(names[idx])

	if len(fraudList) ==0: #no fraud if fraud list is empty
		fraud= False 
	else:
		fraud=True
	print("fraud Commodities: " , fraudList)
		


	if (invoiceCollection.find_one({'0':dictionary.get('0',None)})==None or invoiceCollection.find_one({'id':dictionary.get('id')})==None )and fraud==False: #verifies invoice based on duplication and fraud
		invoiceCollection.insert_one(dictionary)
		return True, dictionary, "Potential Fraud: "+str(fraudList)
	else: #no fraud and no duplication
		fraudCollection.insert_one(dictionary)
		return False, dictionary,"Potential Fraud: "+ str(fraudList)

def comparePrice(commodity, price):
	table = pd.read_csv("data/commodity-prices.csv")
	for i in table.keys(): #compares from the table
		if commodity in i and commodity!="id":
			commodity = i 
			break
	#print(commodity)

	if commodity not in table.keys():
		return False #if it is an unknown commodity, we cannot check
	marketPrice =table[commodity][len(table[commodity])-1]
	if marketPrice> 1.5* price or  marketPrice*1.5< price: 
		return True
	return False

def setTemplate(path): #this is to define the template which can be used to parse several invoices

	image = cv2.imread(path)
	image = cv2.resize(image, (image.shape[1]//2 , image.shape[0]//2 ))
	temp = Template(path)


	count = 0
	while(True):	
		
	
		box = cv2.selectROI("roi", image,False) #selecting the ROI for the different boxes
		
		if( box[2:]!=(0,0)):
			temp.addField(box, str(count))
			count+=1
			

		if cv2.waitKey(0) ==ord('q'): #close it by pressing q

			break

	root = tk.Tk()
	root.geometry("400x240")
	root.title("Enter the names of the boxes seperated by commas and then close") #obtain the labels for all the boxes we annotated such as Copper, Coffee, Tax , id etc
	
	def getTextInput(): #parse the text
	    result=textExample.get("1.0","end")
	    result = result.strip().split(",")
	    textExample.delete("1.0","end")
	    for idx, i in enumerate(result):
	    	temp.names[idx] = i.strip()
	    
	    
	  #  print(result)

	textExample=tk.Text(root, height=10)
	textExample.pack()
	btnRead=tk.Button(root, height=1, width=10, text="Read", 
	                    command=getTextInput)

	btnRead.pack()

	root.mainloop() #GUI
	templateCollection.insert_one(dict(zip(temp.names, temp.boxes))) 
	temp.ObjectId = ObjectId(templateCollection.find_one(dict(zip(temp.names, temp.boxes)))['_id']) #Set the template objects Object ID from the table. This Uniquely identifies it

	return temp



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  #Tesseract is our OCR parser 
if __name__ =="__main__":
	print("please enter image path")
	path  = input()
	path = path.strip()
	print("you have selected ", path)
	temp=setTemplate(path) #Uncomment and run this if you want to set the template
	print("your unique object ID is: ",temp.ObjectId)
	if 'archive' not in os.listdir(): #if the data for commodity pricing has not been scraped, please scrape it
		cp = CommodityPricing()
		cp.setup()
		cp.retrieve()
		cp.process()



