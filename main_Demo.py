import eHRAF_Scraper
from eHRAF_Scraper import Scraper
#
# #
# from importlib import reload
# Scraper = reload(eHRAF_Scraper)
# from eHRAF_Scraper import Scraper

Scraper1 = Scraper(url=r"https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Hawaiians%22+AND+%28subjects%3A%22spirits+and+gods%22+AND+text%3AApple%29")
Scraper1.region_scraper()
print(Scraper1.time_req())
Scraper1.doc_scraper()
# Scraper1.web_close()

