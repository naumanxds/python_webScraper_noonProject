import requests
import urllib.request
import time
import csv

from datetime import datetime
from bs4 import BeautifulSoup

# constants used in code
BASE_URL = 'https://www.noon.com'
START_PAGE_NO = 1
NOT_FOUND = 'None'
INCREMENT_ONE = 1
SLEEP_SEC = 1

# create file with time attached to it for safty purposes
fHandle = open('csvFileCreatedAt-' + datetime.now().strftime("%H-%M-%S") + '.csv', 'w')

# write in file
def writeFile(data):
	csvWriter = csv.writer(fHandle)
	csvWriter.writerow(data)

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
		subHtml = getHtml(BASE_URL + l.get('href'))
		img = subHtml.find('img', {"alt":"noon-now"})
		# check for now badge
		if str(img) == NOT_FOUND:
			now = ''
		else:
			now = 'Now'

		p = subHtml.find('p', {"class":"sellerName"})
		sellerWithLink = p.findChild('a').get_text()
		priceWithLink = subHtml.find('span', {"class":"sellingPrice"}).get_text()

		subHtml = getHtml(BASE_URL + l.get('href').split('?')[0])
		p = subHtml.find('p', {"class":"sellerName"})
		sellerWithoutLink = p.findChild('a').get_text()
		priceWithoutLink = subHtml.find('span', {"class":"sellingPrice"}).get_text()

		writeFile([sku, sellerWithLink, priceWithLink, sellerWithoutLink, priceWithoutLink, now])

# input for user
startUrl = input('Please Enter Starting Point for Scrapper: ')
print('=== Starting Scrapping ===')
count = START_PAGE_NO
while count <= 50:
	# stop if error before 50 iterations
	productsPage = getHtml(startUrl + '?&page=' + str(count))
	if str(productsPage.find('p', {"class":"heading"})) != NOT_FOUND:
		break

	iterateLinks(productsPage.find_all('a', {"class":"product"}))
	count += INCREMENT_ONE
	time.sleep(SLEEP_SEC)

# close file
fHandle.close()
print('=== Scrapping Finished ===')
