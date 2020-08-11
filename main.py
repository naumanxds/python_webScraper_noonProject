import requests
import urllib.request
import time
import csv

from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# constants used in code
BASE_URL = 'https://www.noon.com'
NOT_FOUND = 'None'
INCREMENT_ONE = 1

# create file with time attached to it for safty purposes
fHandle = open('csvFileCreatedAt-' + datetime.now().strftime('%H-%M-%S') + '.csv', 'w', encoding="utf-8")

# create browser instance
browserOptions = Options()
browserOptions.add_argument("--headless")
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=browserOptions)
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())

# write in file
def writeFile(data, url = ''):
	try:
		csvWriter = csv.writer(fHandle)
		csvWriter.writerow(data)
	except Exception as e:
		print('		>> Error in Writing Data into the file = ' + url)
		print(' 	========================================')
		print('		>> ERRROR => ' + format(e))

# get html of the provided page url
def getHtml(url):
    try:
        driver.get(url)
        driver.execute_script('return document.documentElement.outerHTML')
        return BeautifulSoup(driver.page_source, 'html.parser')

    except Exception as e:
        print('     >> Error in Fetching HTML from Url => ' + url)
        print('     >> ERRROR => ' + format(e))

    return False

# iterate through the fetched links get price and place in the file
def iterateLinks(subLinks):
	for l in subLinks:
		try:
			sku = l.get('href').split('/')[-2]
			subHtml = getHtml(BASE_URL + l.get('href'))
			time.sleep(3)

			# check for express badge
			div = subHtml.find('div', {'class':'jsx-2234420881 bottomRow'})
			img = div.find('img', {'alt':'noon-express'})
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

			# brand name
			brandName = subHtml.find('a', {'class' : 'jsx-2771165322 brand'})
			if str(brandName) != NOT_FOUND:
				brandName = brandName.get_text()
			else:
				brandName = 'Brand Name Not Found'

			# model number
			modelNum = subHtml.find('p', {'class' : 'jsx-2771165322 modelNumber'})
			if str(modelNum) != NOT_FOUND:
				modelNum = modelNum.get_text()
			else:
				modelNum = 'Model Not Found'

			# writing data in file
			writeFile(
				[sku, myOffer, buyboxStoreName, buyboxPrice, myOffer - buyboxPrice, otherOffer, express, brandName, modelNum],
				BASE_URL + l.get('href')
			)
		except Exception as e:
			print(' >> Entry missed due to missing data >> url >> ' + BASE_URL + l.get('href'))

# initiaget the code
if __name__ == '__main__':
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
		'Brand Name',
		'Model Number'
	])
	while count <= 50:
		# stop if error before 50 iterations
		productsPage = getHtml(startUrl + '?&page=' + str(count))
		if str(productsPage.find('p', {'class':'heading'})) != NOT_FOUND or productsPage.find_all('a', {'class':'product'}) == NOT_FOUND:
			break

		iterateLinks(productsPage.find_all('a', {'class':'product'}))
		print(str(count) + ' == Pages Done')
		count += INCREMENT_ONE

	# close file
	fHandle.close()
	driver.quit()
	print('=== Scrapping Finished ===')
