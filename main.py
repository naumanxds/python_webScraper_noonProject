import requests
import urllib.request
import time
import csv

from datetime import datetime
from bs4 import BeautifulSoup

# constants used in code
BASE_URL = 'https://www.noon.com'
NOT_FOUND = 'None'
INCREMENT_ONE = 1
SLEEP_SEC = 1

# create file with time attached to it for safty purposes
fHandle = open('csvFileCreatedAt-' + datetime.now().strftime('%H-%M-%S') + '.csv', 'w', encoding="utf-8")

# write in file
def writeFile(data, url = ''):
	try:
		csvWriter = csv.writer(fHandle)
		csvWriter.writerow(data)
	except Exception as e:
		print('		>> Error in Writing Data into the file = ' + url)
		print(' 	========================================')
		print('		>> ERRROR => ' + format(e))

# get html of the provided url page
def getHtml(url):
	try:
		response = requests.get(url)
	except Exception as e:
		print('Oops! Something went worng fetching the link - ' + format(e))
	return BeautifulSoup(response.text, 'html.parser')

# iterate through the fetched links get price and place in the file
def iterateLinks(subLinks):
	for l in subLinks:
		sku = l.get('href').split('/')[-2]
		try:
			subHtml = getHtml(BASE_URL + l.get('href'))
			img = subHtml.find('img', {'alt':'noon-express'})
			# check for express badge
			if str(img) == NOT_FOUND:
				express = ''
			else:
				express = 'Express'

			# getting my offer
			myOffer = subHtml.find('span', {'class':'sellingPrice'}).get_text()
			myOffer = float(myOffer.split('AED ')[1])
			# getting other offer
			otherOffer = subHtml.find('span', {'class':'lowestPrice'})
			if str(otherOffer) != NOT_FOUND:
				otherOffer = myOffer - float((otherOffer.get_text()).split('AED ')[1])
			else:
				otherOffer = myOffer
				
			# creating link for buybox product
			subHtml = getHtml(BASE_URL + l.get('href').split('?')[0])
			# getting buybox seller name
			p = subHtml.find('p', {'class':'sellerName'})
			buyboxStoreName = p.findChild('a').get_text()
			# getting buy box seller price
			buyboxPrice = subHtml.find('span', {'class':'sellingPrice'}).get_text()
			buyboxPrice = float(buyboxPrice.split('AED ')[1])
			# writing data in file
			writeFile(
				[sku, myOffer, buyboxStoreName, buyboxPrice, myOffer - buyboxPrice, otherOffer, express],
				BASE_URL + l.get('href')
			)
		except:
			print('		>> Entry missed due to some error for Product SKU => ' + sku)

# input for user
eteredUrl = input('Please Enter Starting Point for Scrapper: ')
startUrl = eteredUrl.split('page=')[0]
try:
	count = int(eteredUrl.split('page=')[1])
except:
	count = 1
print('=== Starting Scrapping ===')
writeFile([
	'SKU',
	'Our Offer',
	'BuyBox Seller Store Name',
	'BuyBox Seller Offer',
	'Difference with BuyBox Seller',
	'Difference with Other Offer',
	'Express Field',
])
while count <= 50:
	# stop if error before 50 iterations
	productsPage = getHtml(startUrl + '?&page=' + str(count))
	if str(productsPage.find('p', {'class':'heading'})) != NOT_FOUND or productsPage.find_all('a', {'class':'product'}) == NOT_FOUND:
		break

	iterateLinks(productsPage.find_all('a', {'class':'product'}))
	print(str(count) + ' == Pages Done')
	count += INCREMENT_ONE
	time.sleep(SLEEP_SEC)

# close file
fHandle.close()
print('=== Scrapping Finished ===')
