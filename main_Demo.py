import eHRAF_Scraper
from eHRAF_Scraper import Scraper
#
# #
# from importlib import reload
# Scraper = reload(eHRAF_Scraper)
# from eHRAF_Scraper import Scraper

# Scraper1 = Scraper(url=r"https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Hawaiians%22+AND+%28subjects%3A%22spirits+and+gods%22+AND+text%3AApple%29", user="Eric") #Rapid 4 doc test
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3A%28Apple+OR+pear+OR+banana%29&fq=culture_level_samples%7CPSF') #medium scraping (11 minutes!)
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Trobriands%22+AND+text%3A%28Apple+OR+pear+OR+banana%29') #long test for next page
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Navajo%22+AND+text%3A%28Apple+OR+pear+OR+banana%29', rerun = True) #Quick test for next page
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF', rerun=True) #standard Apple
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Serbs%22+AND+text%3AApple', rerun=True) #standard Apple one culture
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22%29&fq=culture_level_samples%7CPSF', rerun=True) # Demo scraper for 750 (actually does 750-759)
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22+OR+%22preventive+medicine%22+OR+%22bodily+injuries%22+OR+%22sorcery%22%29&fq=culture_level_samples%7CPSF')#Actual scraping, 2.6 hours for OCM's 750-754
Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22+AND+%22preventive+medicine%22+OR+%22bodily+injuries%22+OR+%22theory+of+disease%22+OR+%22sorcery%22%29&fq=culture_level_samples%7CPSF',rerun=True) #750-754 but test to see the use of "AND"
# #
Scraper1.region_scraper()
print(Scraper1.time_req())
Scraper1.doc_scraper()


# import time
# # URL = r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF'
# # URL = r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Serbs%22+AND+text%3AApple'
# # URL = r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Navajo%22+AND+text%3A%28Apple+OR+pear+OR+banana%29'
# time_list = []
# for i in range(0,5):
#     t0 = time.time()
#     Scraper1 = Scraper(url=URL, rerun=True)
#     Scraper1.region_scraper()
#     print(Scraper1.time_req())
#     Scraper1.doc_scraper()
#     # Scraper1.web_close()
#     t1 = time.time()
#     time_list.append(t1-t0)
# print(sum(time_list)/len(time_list))
