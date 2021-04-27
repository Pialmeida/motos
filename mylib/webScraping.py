from bs4 import BeautifulSoup as bs
import requests, concurrent.futures, pandas as pd
import re
import sqlite3
import pandas as pd
import numpy
import os, sys, json


class WebScraper:
	os.chdir("..")
	with open('config.json','r') as f:
		CONFIG = json.load(f)

	def __init__(self):
		self._headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

		self._PATH_TO_DB = WebScraper.CONFIG['PATH']['DATA']

		self.states = WebScraper.CONFIG['WEBSCRAPE']['STATES'].split(',')

		print(self.states)

		self.initSession()
		self.initSQLConnection()

	def initSQLConnection(self):
		self.conn = sqlite3.connect(self._PATH_TO_DB)
		self.curon = self.conn.cursor()

	def initSession(self):
		from requests.adapters import HTTPAdapter
		from requests.packages.urllib3.util.retry import Retry

		self.session = requests.Session()
		retry_strategy = Retry(
			total=5,
			status_forcelist=[429, 500, 502, 503, 504],
			method_whitelist=['HEAD', 'GET', 'Options'],
			backoff_factor=1
		)
		adapter = HTTPAdapter(max_retries=retry_strategy)
		self.session.mount('https://', adapter)
		self.session.mount('http://', adapter)

	def getPageUrls(self):
		def _format_search_url(state,pageNumber):
			return f'https://{state}.olx.com.br/autos-e-pecas/motos?o={pageNumber}&q=motos'

		return [_format_search_url(state, pageNumber) for state in self.states for pageNumber in range(1,101)]

	def getBikeUrls(self, url):
		return [x['href'] for x in bs(self.session.get(url, headers=self._headers).text, "html.parser").find_all("a", class_="fnmrjs-0 fyjObc", href=True)]

	def getUrlGenerator(self):
		with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
			results = executor.map(self.getBikeUrls, self.getPageUrls())

		yield from [url for urlList in results for url in urlList]

	def webScrapeWebsite(self):
		with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
			data = executor.map(self.getBikeDetails, self.getUrlGenerator())

		return pd.DataFrame(data)

	def getBikeDetails(self, url):
		soup = bs(self.session.get(url, headers=self._headers).text, "html.parser")

		description = soup.find_all("div", class_="sc-hmzhuo sc-1f2ug0x-3 ONRJp sc-jTzLTM iwtnNi")

		model = getBikeModel(description, url)
		year = getBikeYear(description, url)
		km = getBikeKM(description, url)
		cil = getBikeCil(description, url)
		price = getBikePrice(soup, url)
		cod = getBikeCod(url)
	
		return [cod, model, price, year, cil, km, url]

	def getBikeModel(description, url):
		try:
			return re.search(r'Modelo(.*)',description[1].text).group(1)
		except Exception:
			print(f'No model: {url}')
			return '?'

	def getBikeYear(description, url):
		try:
			return re.search(r'Ano(.*)',description[2].text).group(1)
		except Exception:
			print(f'No year: {url}')
			return '?'

	def getBikeKM(description, url):
		try:
			return re.search(r'Quilometragem(.*)',description[3].text).group(1)
		except Exception:
			print(f'No km: {url}')
			return '?'

	def getBikeCil(description, url):
		try:
			return re.search(r'Cilindrada(.*)',description[4].text).group(1)
		except Exception:
			print(f'No cil: {url}')
			return '?'

	def getBikePrice(soup, url):
		try:
			return float(re.search(r'([\d\.]+)', soup.h2.text).group(1).replace('.',''))
		except Exception:
			print(f'No price: {url}')
			return '?'

	def getBikeCod(url):
		return re.search(r'.*\-(\d+)', url).group(1) if not isErrorRegex(re.search, r'.*\-(\d+)', url) else '?'


	def test(self):
		url = r'https://sp.olx.com.br/sao-paulo-e-regiao/autos-e-pecas/motos/motos-827126855'

		soup = bs(self.session.get(url, headers=self._headers).text, "html.parser")

		model = re.search(r'Modelo(.*)',soup.find_all("div", class_="sc-hmzhuo sc-1f2ug0x-3 ONRJp sc-jTzLTM iwtnNi")[1].text).group(1)
		year = re.search(r'Ano(.*)',soup.find_all("div", class_="sc-hmzhuo sc-1f2ug0x-3 ONRJp sc-jTzLTM iwtnNi")[2].text).group(1)
		km = soup.find_all("div", class_="sc-hmzhuo sc-1f2ug0x-3 ONRJp sc-jTzLTM iwtnNi")[3].text
		cil = soup.find_all("div", class_="sc-hmzhuo sc-1f2ug0x-3 ONRJp sc-jTzLTM iwtnNi")[4].text
		price = float(re.search(r'[\d\.]+', soup.h2.text).group(0).replace('.',''))
		cod = re.search(r'\d+', soup.find("span", class_="sc-16iz3i7-0 qJvUT sc-ifAKCX fizSrB").text).group(0)
		desc = soup.find("span", class_="sc-1sj3nln-1 eOSweo sc-ifAKCX cmFKIN").text

		print(year)

if __name__ == '__main__':
	ws = WebScraper()