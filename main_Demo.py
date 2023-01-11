
# If you are loading this for the first time (AND THE VENV IS MISSING), you will need the packages used in the file. The best way is to use a virtual environment or use anaconda (which might save on space but some package may not be available through there). For a virtual environment (venv) type into the terminal:

#         python - m venv venv
        
# When venv is created, select it as your prefered kernal (in VS code, it should give you a prompt to do so, otherwise, select it in the to right corner). Then create a new terminal (should be able to do so at the top of the mac screen under "terminal"). Each line in your terminal should start with "venv" or whatever you named the environment if you called it something else. Now you can install the requirments in the terminal using:

#         pip install -r requirements.txt -v
        
# NOTE: It is likely the requirements file is bloated with packages you do not need. I have not tried to slim it down so feel free to just install packages as you see fit with

#         pip install <your package name>


# # Scraper inputs:
# url =         <string: eHRAF URL>
# user =        <string: your name>
# rerun =       <bool: disregard any previously ran files (TRUE) or try to start from last crashed (FALSE)>
# headless =    <bool: do not show the scraped chrome browser (TRUE) or show the scxraped Chrome Browser (FALSE)>









import eHRAF_Scraper
from eHRAF_Scraper import Scraper

# for reloading the scraper module
from importlib import reload
Scraper = reload(eHRAF_Scraper)
from eHRAF_Scraper import Scraper


# Scraper1 = Scraper(url=r"https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Hawaiians%22+AND+%28subjects%3A%22spirits+and+gods%22+AND+text%3AApple%29", rerun=True, user="Eric") #Rapid 4 doc test
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3A%28Apple+OR+pear+OR+banana%29&fq=culture_level_samples%7CPSF') #medium scraping (11 minutes!)
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Trobriands%22+AND+text%3A%28Apple+OR+pear+OR+banana%29') #long test for next page
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Navajo%22+AND+text%3A%28Apple+OR+pear+OR+banana%29', rerun = True) #Quick test for next page
Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF', rerun=True) #standard Apple
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=cultures%3A%22Serbs%22+AND+text%3AApple', rerun=True) #standard Apple one culture
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22%29&fq=culture_level_samples%7CPSF', rerun=True) # Demo scraper for 750 (actually does 750-759)
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22+OR+%22preventive+medicine%22+OR+%22bodily+injuries%22+OR+%22sorcery%22%29&fq=culture_level_samples%7CPSF')#Actual scraping, 2.6 hours for OCM's 750-754
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=subjects%3A%28%22sickness%22+AND+%22preventive+medicine%22+OR+%22bodily+injuries%22+OR+%22theory+of+disease%22+OR+%22sorcery%22%29&fq=culture_level_samples%7CPSF',rerun=True) #750-754 but test to see the use of "AND"
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=+-text%3AGallyhow') #simply to extract each culture and region DO NOT ACTUALLY RUN THE WHOLE THING
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3A%28apple+AND+grandma+AND+pear%29', rerun=False)#single scraping
# Scraper1 = Scraper(url=r'https://ehrafworldcultures.yale.edu/search?q=text%3A%28apple+AND+grandma%29&fq=culture_level_samples%7CSCCS%3Bculture_level_samples%7CSRS', rerun=True, headless=False)# rapid 7 doc text with filters
# #
print(Scraper1.region_scraper())   # Scrape the region
print(Scraper1.time_req())  #Scrape
Scraper1.doc_scraper()



# #BETA TESTING 

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



# Used for saving all the cultures found the the list, use with  url=r'https://ehrafworldcultures.yale.edu/search?q=+-text%3AGallyhow' but COMMENT OUT SOME OF THE ABOVE LINES SO IT DOES NOT RUN FOR 5 DAYS
# import pandas as pd
# culture_list =[]
# regn_list = []
# subregion_list = []
# for key, val in Scraper1.culture_dict.items():
#     culture_list.append(key.lower())
#     regn_list.append(val["Region"].lower())
#     subregion_list.append(val["SubRegion"].lower())

# df = pd.DataFrame({"Region":regn_list, "SubRegion":subregion_list,  "Culture":culture_list})
# df.to_excel("Resources/Culture_Names.xlsx", index=None)
