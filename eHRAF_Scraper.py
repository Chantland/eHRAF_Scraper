# %% [markdown]
# # Webscraper
# 
# #### **Author** -- Eric Chantland (ericchantland@gmail.com)
# #### **Created** -- October 2022
# 
# 
# <p>The objective of this program is to webscrap the eHRAF database for various text passages in order to explore misery and how it relates with folk/wild traditions. To run this program, merely press play and enter in the URL and your name. To obtain the URL, progress through ehRAF website and enter in your search terms in the "advanced search" boxes and the filters. When you have successfully filtered the searches (so the region list) but BEFORE you actually look at any of the culture's links, copy the URL that it gives you into this program. This program seeks to scrape the webpage for texts and OCM's. It is therefore very susceptible to the eHRAF webpage changing, loading slow/fast, and/or not providing standardized information. If this program fails, it is likely due to one of these three.<p>
# 
# <p> To run this program, you can go individually or just run all the cells at once. However, this autonomous webpage (chrome) must be running for the rest of the webscraper to work. Therefore, if you run into an issue, just rerurn the whole program. If that does not fix it, then there must be a different issue. <p>
# 
# <p> If the program stalls for whatever reason, then webpage may have loaded too slow and the scraper was not able to catch that this happened resulting in an infinite loop. The program needs to be updated for its sleep timer. <b>Stop the program and contact me.<b> <p>
# 

# %%
import pandas as pd                 # dataframe storing
from bs4 import BeautifulSoup       # parsing web content in a nice way
import ssl                          # MAY BE UNNECESSARY: provides access to the security socket layer (ssl) https://docs.python.org/3/library/ssl.html
import urllib                       # MAY BE UNNECESSARY: open and navigate URL's
import os                           # Find where this file is located.
import time                         # for pausing the program in order for it to load the webpage
import re                           # regex for searching through strings


from selenium import webdriver      # load and run the webpage dynamically.
from selenium.webdriver.chrome.options import Options

# for wait times
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# %% [markdown]
# For each of these search variables, input the text "any", "none", or "all" before a list of the desired keywords. This is excluding "culture" which only contains "any" and "none"
# 
# For each of the query variables, just input a list as they are always "Any"
# 
# Alternatively, you can copy and paste the hyperlink and get the same results 
# 

# %% [markdown]
# 

# %% [markdown]
# ### URL
# On eHRAF homepage, you may put in various search terms and queries using their GUI (their menu) once you are happy with the saerch terms, Copy and paste the URL into the parenthesis of the Variable below:
# For example, to get the search for all documents containing "apple" and through the PSF, I got a hyperlink like this:
# https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF

# %%
# make sure the hyperlink goes within quotes!
URL = input("Please enter in an eHRAF URL, otherwise enter nothing for a demo\n")
user = input("What is your name?\n")

# %% [markdown]
# <!-- <img src="Hyperlink-Example.png"> -->
# ![alt text](Hyperlink-Example.png "Title")

# %%
# Use a autonomous Chrome page to dynamically load the page for scraping. 
# Requires webdriver to be downloaded and then its path directed to.

# iniate "headless" which stops chrome from showing itself when this is run, 
# switch headless to False if you want to see the webpage or True if you want it to run in the background
options = Options()
options.headless = False


# Unless you want to change to location, make sure the chromedriver program is located within the same file folder that you run this application in.
# You must have chrome (or download another browser driver and change the path). Download the chrome software here: https://chromedriver.chromium.org/downloads
path = os.getcwd() + "/chromedriver"
driver = webdriver.Chrome(executable_path = path, options=options)
# driver.maximize_window()

# Demo if there is no URL entered
if URL == '':
    URL = r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF'

homeURL = "https://ehrafworldcultures.yale.edu/"
searchTokens = URL.split('/')[-1]

# Load the HTML page (note that this should be updated to allow for modular input)
driver.get(homeURL + searchTokens)

# Find then click on each tab to reveal content for scraping
# Elements must be individually clicked backwards. I do not know why this is a thing but my guess is each 
# clicked tab adds HTML pushing future tabs to a new location thereby making some indexing no longer point to a retrieved tab. 
# Loading backwards avoids this.
country_tab = driver.find_elements_by_class_name('trad-overview__result')
for i in range(len(country_tab)-1,-1,-1):
    try:
        #Note: this clicking should work for each of the Regions. However, technically, trad-overview__result is not the actual 
        # element that should be clicked on. It is just good enough for simplicity sake. If this give you trouble, consider putting in
        # driver.execute_script("arguments[0].click();", country_tab[i]) and changing the above drive.find to a button element or whatever is the true clickable drop down, 
        # although this will take a bit more indexing so beware.
        country_tab[i].click()
        
    except:
        print(f"WARNING tab {i} failed to be clicked")

# Parse processed webpage with BeautifulSoup
soup = BeautifulSoup(driver.page_source)

# extract the number of documents intended to be found
document_count = soup.find_all("span", {'class':'found__results'})
document_count = document_count[0].small.em.next_element
document_count = int(document_count.split()[1])
# estimate the time this will take
import math
time_sec = document_count/4.33
time_min = ""
time_hour = ""
if time_sec > 3600:
    time_hour = math.floor(time_sec/3600)
    time_sec -= time_hour*3600
    time_hour = f"{time_hour} hour(s), "
if time_sec > 60:
    time_min = math.floor(time_sec/60)
    time_sec -= time_min*60
    time_min = f"{time_min} minute(s), and "

time_sec = f"{math.floor(time_sec)} second(s)"


print(f"This will scrape up to {document_count} documents and take roughly \n{time_hour}{time_min}{time_sec}")

# %%
import time

# Create a dictionary to store all cultures and their links for later use
culture_dict = {}

# find the tables containing the cultures then loop through them to extract their subregion, region, name, and the link to the passages
# Note that if the ehraf website changes, this loop might need fixing by changing where the information is retrieved.
# Also note that if the dynamic page is not loaded correctly, (a warning is given above), this may also fail.
table_culture_links = soup.find_all('tr', {'class':'mdc-data-table__row'})

# repeat in case the website took to long to load.
loop_protect = 0
while len(table_culture_links) == 0:
    time.sleep(.1)
    soup = BeautifulSoup(driver.page_source)
    table_culture_links = soup.find_all('tr', {'class':'mdc-data-table__row'})
    loop_protect += 1
    if loop_protect > 5:
        raise Exception(f"Repeated loading {loop_protect-1} times but did not find links")
for culture_i in table_culture_links:
    culture_list = list(culture_i.children)

    subRegion = culture_list[0].text
    cultureName = culture_list[1].a.text
    link = culture_list[1].a.attrs['href']
    region = culture_i.findParent('table', {'role':'region'}).attrs['id']
    # 
    culture_dict[cultureName] = {"Region":region, "SubRegion":subRegion, "link":link}
print(f"Number of cultures extracted {len(culture_dict)}")

# %% [markdown]
# ## Main Scraper

# %%

doc_count_total = 0

# create dataframe to hold all the data
df_eHRAF = pd.DataFrame({"Region":[], "SubRegion":[], "Culture":[], 'DocTitle':[], 'Year':[], "OCM":[], "OWC":[], "Passage":[]})

# For each Culture, go to their webpage link then scrape the document data
for key in culture_dict.keys():
    driver.get(homeURL + culture_dict[key]['link'])
    # driver.get(homeURL + culture_dict['Azande']['link'])
    # driver.get(homeURL + culture_dict[key]['link'])
    doc_count = 0
    
    # dataframe for each culture
    df_eHRAFCulture = pd.DataFrame({"Region":[], "SubRegion":[], "Culture":[], 'DocTitle':[], 'Year':[], "OCM":[], "OWC":[], "Passage":[]})
   
    # Try to make the program wait until the wepage is loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "mdc-data-table__row")))
    #Click every source tab
    sourceTabs = driver.find_elements_by_class_name('mdc-data-table__row')
    for source_i in sourceTabs:
        driver.execute_script("arguments[0].click();", source_i)

    #Log the source table's results number in order to know where to start and stop clicking.
    # Skip every 2 logs as they do not contain the information desired
    soup = BeautifulSoup(driver.page_source)
    sourceCount = soup.find_all('td',{'class':'mdc-data-table__cell mdc-data-table__cell--numeric'})
    sourceCount_list = list(map(lambda x: int(x.text), sourceCount[0::3]))


    
    # WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "trad-data__results")))

    # wait to make sure the page is loaded. CHANGE to a higher time if it runs indefinately
    time.sleep(.1)

    #get the results tab(which is basically the source tab but contained within a different HTML element) for sub indexing sources
    resultsTabs = driver.find_elements_by_class_name('trad-data__results')
    # if the resultsTabs did not all load, reload as necessary
    reload_protect = 0
    while len(sourceCount_list) != len(resultsTabs) or reload_protect>10:
        time.sleep(.1)
        resultsTabs = driver.find_elements_by_class_name('trad-data__results')
        reload_protect += 1
    

    resultsTabs_count = len(resultsTabs) #For later reload checking

    for i in range(len(resultsTabs)):
        total = sourceCount_list[i]
        
        #While total is > 0
        while True:
            docTabs = resultsTabs[i].find_elements_by_class_name('sre-result__title')
            #Click all the tabs within a source
            for doc in docTabs:
                driver.execute_script("arguments[0].click();", doc)
                doc_count +=1


            soup = BeautifulSoup(driver.page_source)
            #Extract the document INFO here
            soupDocs = soup.find_all('section',{'class':'sre-result__sre-result'}, limit=total)
            for soupDoc in soupDocs:
                docPassage = soupDoc.find('div',{'class':'sre-result__sre-content'}).text
                
                soupOCM = soupDoc.find_all('div',{'class':'sre-result__ocms'})
                # OCMs
                # find all direct children a tags then extract the text
                ocmTags = soupOCM[0].find_all('a', recursive=False)
                OCM_list = []
                for ocmTag in ocmTags:
                    OCM_list.append(int(ocmTag.span.text))
                # OWC
                OWC = soupOCM[1].a['name']

                DocTitle = soupDoc.find('div',{'class':'sre-result__sre-content-metadata'})
                DocTitle = DocTitle.div.text
                # Search for the document's year of creation 
                Year = re.search('\(([0-9]{0,4})\)', DocTitle)
                if Year is not None:
                    # remove the date then strip white space at the end and start to give the document's title
                    DocTitle = re.sub(f'\({Year.group()}\)', '', DocTitle).strip()
                    # get the year without the parenthesis
                    Year = int(Year.group()[1:-1])
                
                # dataframe for each document
                df_Doc = pd.DataFrame({'OCM':[OCM_list], 'OWC':[OWC], 'DocTitle':[DocTitle], 'Year':[Year],  'Passage':[docPassage]})
                df_eHRAFCulture = pd.concat([df_eHRAFCulture, df_Doc], ignore_index=True)
            # set remaining docs in a source tab (for clicking the "next" button if not all of them are shown)
            total -= len(docTabs)

            # If there are more tabs hidden away, find the button, click it, and then refresh the results
            # otherwise, end the loop and close the source tab to make search for information easier
            if total >0:
                SourceTabFooter = resultsTabs[i].find_elements_by_class_name('trad-data__results--pagination')
                buttons = SourceTabFooter[0].find_elements_by_class_name('rmwc-icon--ligature')
                driver.execute_script("arguments[0].click();", buttons[-1])
                time.sleep(.1)
                resultsTabs = driver.find_elements_by_class_name('trad-data__results')
                # in case .1 was not enough time, redo until the entire page is loaded again.
                reload_protect = 0
                while len(resultsTabs) < resultsTabs_count or reload_protect>10:
                    time.sleep(.1)
                    resultsTabs = driver.find_elements_by_class_name('trad-data__results')
                    reload_protect += 1
            else:
                # close sourcetab(this might save time in the long run)
                driver.execute_script("arguments[0].click();", sourceTabs[i])
                break


    df_eHRAFCulture[['Region','SubRegion',"Culture"]] = [culture_dict[key]['Region'], culture_dict[key]['SubRegion'], key ]    
    df_eHRAF = pd.concat([df_eHRAF, df_eHRAFCulture], ignore_index=True)
    doc_count_total += doc_count
    if doc_count < sum(sourceCount_list):
        print(f"WARNING {doc_count} out of {sum(sourceCount_list)} documents loaded for {key}")

print(f'{doc_count_total} documents out of a possible {document_count} loaded (also check dataframe)')


# %%
# close the webpage
driver.close()

# %%
# Any null values?
if df_eHRAF.isnull().values.any():
    print('Some null values found:')
    for col in df_eHRAF.columns:
        print(f"{col}: {df_eHRAF[col].isnull().sum()}")
else: 
    print("no null values found")


# %%
# get time and date that this program was run
from datetime import date, datetime
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%m/%d/%y")



# %%
# clean and strip the URL to be put into the excel document

replace_dict = {'%28':'(', '%29':')', '%3A':'~', '%7C':'|', '%3B':';'}
remove_list = [homeURL, 'search', '\?q=', 'fq=', '&', 'culture_level_samples']

URL_name = URL

for i in remove_list:
    URL_name = re.sub(i, '', URL_name)
# print(URL_name)
for key, val in replace_dict.items():
    URL_name = re.sub(key, val, URL_name)
# print(URL_name)


URL_name_nonPlussed = re.sub('\+', ' ', URL_name)
URL_name_nonPlussed = re.sub('\~', ':', URL_name)
URL_name_nonPlussed



# %%
# place run information within the "run_info" column
df_eHRAF['run_Info'] = None
df_eHRAF.loc[0, 'run_Info'] = "User: " + user
df_eHRAF.loc[1, 'run_Info'] = "Run Time: " + str(current_time)
df_eHRAF.loc[2, 'run_Info'] = "Run Date: " + str(current_date)
df_eHRAF.loc[3, 'run_Info'] = "Run Input: " + URL_name_nonPlussed
df_eHRAF.loc[4, 'run_Info'] = "Run URL: " + URL
df_eHRAF

# %%
try:
    df_eHRAF.to_excel('Data/' + URL_name + '_web_data.xlsx', index=False)
except:
    print("Unable to save the title of the document, please rename it or risk overwriting")
    df_eHRAF.to_excel('Data/' + user + str(now.strftime("%m_%d_%y")) + '_web_data.xlsx', index=False)


