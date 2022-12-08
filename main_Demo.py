import eHRAF_Scraper
from eHRAF_Scraper import Scraper
#
# #
# from importlib import reload
# Scraper = reload(eHRAF_Scraper)
# from eHRAF_Scraper import Scraper

# Scraper1 = Scraper(url=r"https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Hawaiians%22+AND+%28subjects%3A%22spirits+and+gods%22+AND+text%3AApple%29") #Rapid 4 doc test
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Serbs%22+AND+text%3AApple')
Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3A%28Apple+OR+pear+OR+banana%29&fq=culture_level_samples%7CPSF') #medium scraping (11 minutes!)
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Trobriands%22+AND+text%3A%28Apple+OR+pear+OR+banana%29') #long test for next page
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Navajo%22+AND+text%3A%28Apple+OR+pear+OR+banana%29') #Quick test for next page
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF') #standard Apple
Scraper1.region_scraper()
print(Scraper1.time_req())
Scraper1.doc_scraper()
# Scraper1.web_close()

