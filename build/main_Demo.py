

# # Scraper inputs:
# url =         <string: eHRAF URL>
# user =        <string: your name>
# rerun =       <bool: disregard any previously ran files (True) or try to start from last crashed (False). Default is False>
# headless =    <bool: do not show the scraped chrome browser (True) or show the scxraped Chrome Browser (False). Default is False>


# # Doc_Scraper inputs:
# saveRate =    	<int: iteration of files scraped before a routine "safety save" occurs. Default is 5000>


import time




import eHRAF_Scraper
from eHRAF_Scraper import Scraper

# for reloading the scraper module
from importlib import reload
Scraper = reload(eHRAF_Scraper)
from eHRAF_Scraper import Scraper


t1 = time.time()
Scraper1 = Scraper(headless=False)

# Scraper1.region_scraper(url=r"https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Hawaiians%22+AND+%28subjects%3A%22spirits+and+gods%22+AND+text%3AApple%29") #Rapid 4 doc test
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3A%28Apple+OR+pear+OR+banana%29&fq=culture_level_samples%7CPSF') #medium scraping (11 minutes!)
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Trobriands%22+AND+text%3A%28Apple+OR+pear+OR+banana%29') #long test for next page
Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Navajo%22+AND+text%3A%28Apple+OR+pear+OR+banana%29', rerun = True) #Quick test for next page
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF') #standard Apple
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Serbs%22+AND+text%3AApple') #standard Apple one culture
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22%29&fq=culture_level_samples%7CPSF') # Demo scraper for 750 (actually does 750-759)
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22+OR+%22preventive+medicine%22+OR+%22bodily+injuries%22+OR+%22sorcery%22%29&fq=culture_level_samples%7CPSF')#Actual scraping, 2.6 hours for OCM's 750-754
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22+AND+%22preventive+medicine%22+OR+%22bodily+injuries%22+OR+%22theory+of+disease%22+OR+%22sorcery%22%29&fq=culture_level_samples%7CPSF',rerun=True) #750-754 but test to see the use of "AND"
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=+-text%3AGallyhow') #simply to extract each culture and region DO NOT ACTUALLY RUN THE WHOLE THING
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3A%28apple+AND+grandma+AND+pear%29', rerun=False)#single scraping
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3A%28apple+AND+grandma%29&fq=culture_level_samples%7CSCCS%3Bculture_level_samples%7CSRS', rerun=True)# rapid 7 doc text with filters
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22preventive+medicine%22+OR+%22theory+of+disease%22%29&fq=culture_level_samples%7CPSF') # check OCM 751 and 753 with PSF filter
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22preventive+medicine%22+OR+%22theory+of+disease%22%29') # check OCM 751 and 753 without PSF filter
# Scraper1.region_scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22preventive+medicine%22+AND+%22sorcery%22+AND+%22theory+of+disease%22%29&fq=culture_level_samples%7CPSF')


print(Scraper1.time_req()) #return the time required (optional)
print(Scraper1.cult_count(by='culture'))
Scraper1.doc_scraper(saveRate=50) #scrape the documents taken from the region
t2 = time.time()
print("Time taken",str(int(t2-t1)), "seconds")