
#### **Author** -- Eric Chantland (ericchantland@gmail.com)
#### **Created** -- October 2022


# NOTE: This is the behind the scenes python code for the eHRAF GUI which is designed to scrape document files from
# eHRAF based on the user's search selections. This should run nearly identical to the eHRAF_Scraper.ipynb albeit
# with more focus on making the GUI side work. If you are new to the project, I highly recommend checking out
# eHRAF_Scraper.ipynb as it contains a bit more description as to what the code is doing.

# TODO It appears that the tab which shows more passages (10 to 150) rveals every one of the sources. Perhaps make it the default at the start?


import pandas as pd                 # dataframe storing
from bs4 import BeautifulSoup       # parsing web content in a nice way
import os                           # Find where this file is located.
import sys                          # Also for finding file location (for saving)
import platform                     # for checking the platform
import re                           # regex for searching through strings
import time                         # for waiting for the page to load
import selenium                     #package for loading an autnomous browser
import webdriver_manager            # manager, I am not sure what it does in relation to selenium but it is important, perhaps this is used to avoid downloading chrome
from datetime import datetime
import concurrent.futures           # for multithreading

from selenium import webdriver      # load and run the webpage dynamically.
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# for wait times
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# # DEMO to test versions
# import sys
# print(sys.version)
# print(sys.executable)
# print(sys.path)

# driver = uc.Chrome()
class Scraper:
    def __init__(self, headless:bool=False, failureClose:bool=False, GuiInUse:bool=False):
        #optional close if failure
        self.failureClose = failureClose
        # The program may need to be saved multiple times, Make it so it only overwrites the input info once
        self.repeatSave = False
        # track if the GUI is running this command (likely to print out descriptions in real time)
        self.GuiInUse = GuiInUse 

        # (optional) iniate "headless" which stops chrome from showing itself when this is run,
        # switch headless to False if you want to see the webpage or True if you want it to run in the background
        options = Options()
        # options.page_load_strategy = 'eager' # make the webpage potentially the slightest bit faster (unproven here) if the load begins upon everything being interactable
        options.headless = headless
        #BETA: for not loading images
        options.add_experimental_option(
            "prefs", {
                # block image loading
                "profile.managed_default_content_settings.images": 2,
            }
        )

        # set up culture dict here to make sure later functions know it does not exist yet
        self.culture_dict = None
        # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) #Original chrome driver, this causes issues sometimes with not able to find the chromedriver
        #tentative chrome driver without using ChromeDriverManager().install()
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=options)

        # import undetected_chromedriver as uc
        # Initialize undetected ChromeDriver
        # driver = uc.Chrome()



        # here for later gui integration
        self.homeURL = "https://ehrafworldcultures.yale.edu/"

        # Change window size to account for irresponsive webpage sizes
        try:
            self.driver.set_window_size(1100,1100)
        except: #in case a computer cannot handle the set size (which it should but still)
            self.driver.fullscreen_window()

    def login(self): # if an initial login is required
        self.driver.get(self.homeURL) 

    # Reveal all the cultures relevant to your query then extarct URL links
    def region_scraper(self, url=None, user=None, rerun=False, cultureFiles= False, user_folder_name = False):

        if url is not None:
            self.URL = url
        # if no inputs are received,set URL to the default Apple demo
        if url is None:
            self.URL = r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF'
            print("No input given, Defaulting to Apple demo")
        if user is None:
            self.user = "No Name Specified"
        else:
            try:
                self.user = str(user)
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                raise
        # For saving individual culture files
        self.cultureFiles = cultureFiles

        #For when the altogether dataset exists but cultural files do not match (and the person wants a partial file save)
        self.skip_cultures_altogether = [] 

        # Get URL search tokens then navigate to the webpage for region scraping
        searchTokens = self.URL.split('/')[-1]
        self.driver.get(self.homeURL + searchTokens)

        #Create folder name if not supplied, otherwise use what the user desire
        folder_name = self.output_dir_cons() # Get folder name for saving in addition to setting up behind the scenes other text strings for the later excel file
        if user_folder_name is not False and isinstance(user_folder_name, str): # if the user supplied a folder name, use this instead (still need output_dir_cons() for other file working)
            folder_name = user_folder_name
        folder_name = self.folderNameClean(folder_name) #clean folder name of illegal characters
        assert len(folder_name) > 0, "ERROR, zero length folder name. Please supply Alphanumeric characters"
        self.createDataDir(folder_name) # Create a data directory for saving and partial file checking

        # if a partial file is already present, append to that file
        self.restartCrashedQuery = False
        self.crashed = False
        if rerun is False:
            if os.path.isfile(self.file_Path):
                print("File with the same search query found, skipping successfully scraped cultures")
                if self.file_length_warning is not None:
                    print("WARNING, due to the shortening of the file name, different search queries can be regarded as the same search query and cause the scraper to skip skip cultures it shouldn't. Check the the _Altogether_Dataset.xlsx to be sure")
                self.crashed = True
                self.restartCrashedQuery = True



        # Find then click on each tab to reveal content for scraping
        # Elements must be individually clicked backwards. I do not know why this is a thing but my guess is each
        # clicked tab adds HTML pushing future tabs to a new location thereby making some indexing no longer point to a retrieved tab.
        # Loading backwards avoids this.
        self.wait_webdriver(term="trad-overview__result", by=By.CLASS_NAME)
        country_tab = self.driver.find_elements(By.CLASS_NAME,"trad-overview__result")
        if len(country_tab) <1:
            return "No search results found, be sure you are not over filtering"
        for ct_i in range(len(country_tab)-1,-1,-1):
            try:
                # self.driver.execute_script("arguments[0].click();", country_tab[ct_i])
                country_tab[ct_i].click()
            except:
                print(f"WARNING region {ct_i+1} failed to be clicked, possibly because unrelated regions were initially found")
        # Parse processed webpage with BeautifulSoup (wait to make sure they are there first)
        self.wait_webdriver(term="mdc-data-table__row", by=By.CLASS_NAME)
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")

        # extract the number of passages in documents intended to be found
        self.intendPas_count = soup.find_all("span", {'class': 'found__results'})
        self.intendPas_count = self.intendPas_count[0].small.em.next_element
        self.intendPas_count = int(self.intendPas_count.split()[1])

        self.doc_URL_finder(soup=soup)

    # Estimate the time this will take (no longer accurate)
    def time_req(self):


        import math
        # # OLD calculation, current speeds are drastically slower for reasons I am not sure yet
        # # time estimate in seconds, larger scrapings should be faster so they get a log reduction.
        # if self.intendPas_count > 10000: 
        #     time_sec = math.log(self.intendPas_count,1.005) + len(self.culture_dict.keys())
        # else:
        #     # time of standard loading of each culture
        #     time_sec = (self.intendPas_count / 5) + len(self.culture_dict.keys())

        
        # time estimate in seconds, larger scrapings should be faster so they get a log reduction.
        time_sec = (self.intendPas_count) + len(self.culture_dict.keys())
        # NEW time of standard loading of each culture
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
        return f"This will scrape up to {self.intendPas_count} passages and take roughly \n{time_hour}{time_min}{time_sec}"
    
    # Get URL's for each culture about the be scraped
    def doc_URL_finder(self, soup):
        # Create a dictionary to store all cultures and their links for later use
        self.culture_dict = {}

        # find the tables containing the cultures then loop through them to extract their subregion, region, name, and the link to the passages
        # Note that if the ehraf website changes, this loop might need fixing by changing where the information is retrieved.
        # Also note that if the dynamic page is not loaded correctly, (a warning is given above), this may also fail.
        table_culture_links = soup.find_all('tr', {'class':'mdc-data-table__row'})

        # repeat in case the website took to long to load.
        loop_protect = 0
        while len(table_culture_links) == 0:
            time.sleep(.1)
            soup = BeautifulSoup(self.driver.page_source, features="html.parser")
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
            source_count = int(culture_list[-2].text)
            pas_count = int(culture_list[-1].text)

            self.culture_dict[cultureName] = {"Region": region, "SubRegion": subRegion, "link": link, "Source_count": source_count, "Pas_Count": pas_count,  "Reloads": {"source_reload": 0, "results_reload": 0}}
        # print(f"Number of cultures extracted {len(culture_dict)}")

    # Optionally reveal the number of passages per culture
    def cult_count(self, by:str=None):
        
        if by is None:
            return None
        # Check to make sure there is a dictionary to even run
        if self.culture_dict is None:
            raise Exception("Must initiate function region_scraper()")

        text = 'Passage counts for the following cultures:\n'
        if by == 'culture':
            myKeys = list(self.culture_dict.keys())
            myKeys.sort()
            self.culture_dict = {i: self.culture_dict[i] for i in myKeys}
        elif by == 'count':
            self.culture_dict = dict(sorted(self.culture_dict.items(), key=lambda item: item[1]['Pas_Count']))
        else:
            raise Exception("Not a valid input for 'by'")
        
        # go through each of the passage text within the keys and append it to the text
        lineLength = 26
        for key in self.culture_dict.keys():
            # get the spaces between the number and the cultural passage
            spaceBuffer = lineLength - len(key) - len(str(self.culture_dict[key]["Pas_Count"])) 
            # if space buffer is not large enough, try to refit
            if spaceBuffer <0:
                # split into individual words and create a textBuffer to make sure we do not overflow
                pasWord = key.split()
                textBuffer = ''
                for count, word in enumerate(pasWord):
                    # if there is no room start a new line
                    if len(textBuffer) + 1 + len(word) >= lineLength:
                        text += textBuffer.strip() + '\n' #remove the trailing white space and append to text
                        textBuffer = ''

                    # if the last word, append the number value, otherwise, just add the word
                    if count == len(pasWord)-1:
                        spaceBuffer = lineLength - len(textBuffer) - len(word) - len(str(self.culture_dict[key]["Pas_Count"]))
                        # if space buffer is not large enough for the number, make the number and the new word go to a different line otherwise include the word
                        if spaceBuffer <0:
                            text += textBuffer.strip() + '\n'
                            spaceBuffer = lineLength -  len(word) - len(str(self.culture_dict[key]["Pas_Count"]))
                            text += word + (spaceBuffer * ' ') + str(self.culture_dict[key]["Pas_Count"]) + '\n'
                        else:
                            text += textBuffer + word + (spaceBuffer * ' ') + str(self.culture_dict[key]["Pas_Count"]) + '\n'
                    else:
                        textBuffer += word + ' '
            else:
                text += key + (spaceBuffer * ' ') + str(self.culture_dict[key]["Pas_Count"]) + '\n'
        return text
   
    # click and set up for scraping (inside we will call the scraper function)
    def doc_scraper(self, saveRate:int=500, endClose:bool = True):

        #BETA DELETE
        # self.timer = {"block1":{"count":0,"time":[]},"block2":{"count":0,"time":[]},"block3":{"count":0,"time":[]},"block4":{"count":0,"time":[]}, "block5":{"count":0,"time":[]}, "block6":{"count":0,"time":[]},"block7":{"count":0,"time":[]},"block8":{"count":0,"time":[]}, "block9":{"count":0,"time":[]},}

        #Set the save rate up which automatically save the file every time x files are loaded. Made to protect for unforseen issues
        if not isinstance(saveRate, int) or saveRate <0 or saveRate is None:
            saveRate = None
            yield self.text_print("WARNING Not a valid interval for saving, Must supply a positive integer for saveRate, defaulting to None", color='yellow')
        elif saveRate == 0:
            saveRate = None
        else:
            saveRate_count = 0
            
        # If we have a partial file, load it, otherwise  create dataframe to hold all the data
        if self.restartCrashedQuery:
            crashSpotDetermined = self.partial_file_return()

            if crashSpotDetermined:
                yield self.text_print(f"{self.pas_count_total + len(self.unfPassage_dict['Region'])} passages loaded from partial file of which {len(self.unfPassage_dict['Region'])} are loaded from the unfinished culture {self.unfCulture}")
            else:
                yield self.text_print(f'{self.pas_count_total} passages loaded from partial file. Must continue from next or redone culture (if any)')
        else: #if no crash, initialize the counts back to default
            self.pas_count_total = 0
            self.df_ehraf = pd.DataFrame({"Region":[], "SubRegion":[], "Culture":[], 'DocTitle':[], 'Section':[], 'Author':[], 'Page':[], 'Year':[], "OCM":[], "OWC":[], "Passage":[]})
            self.unfCulture = None

        # For each Culture, go to their webpage link then scrape the document data
        for key in self.culture_dict.keys():
            self.currentCulture = key
            self.driver.get(self.homeURL + self.culture_dict[self.currentCulture]['link'])
            pas_count = 0
            

            #If for whatever reason, the unfinished culture is not the first one in the loop, skip it until we come across the culture. 

            if self.unfCulture:
                if self.unfCulture.lower() != self.currentCulture.lower():
                    self.restartCrashedQuery = False 
                else: 
                    self.restartCrashedQuery = True




            # # Preallocate space to save on speed (append a smaller dict if we need to start from a crash)

            if self.restartCrashedQuery:
                #Now make the unfinished passage and source count the official current ones
                self.pasNumInSource = self.unfPasNumInSource
                self.sourceNumInCulture = self.unfSourceNumInCulture
                #create a shorter passage_dict then append it to the real one
                self.passage_dict = self.unfPassage_dict
                populate_list = [0] * (self.culture_dict[self.currentCulture]['Pas_Count'] - len(self.passage_dict['Culture']))
                passageMini_dict = {'Region':[self.culture_dict[self.currentCulture]['Region']] * len(populate_list),
                    'SubRegion':[self.culture_dict[self.currentCulture]['SubRegion']] * len(populate_list),
                    'Culture':[self.currentCulture] * len(populate_list),
                    "DocTitle":populate_list.copy(), # copy is required to use unique ascriptions
                    "Section":populate_list.copy(),
                    "Author":populate_list.copy(), 
                    "Page":populate_list.copy(), 
                    "Year":populate_list.copy(), 
                    "OCM":populate_list.copy(), 
                    "OWC":populate_list.copy(),
                    "Passage":populate_list.copy()}
                for key, value in passageMini_dict.items():
                    self.passage_dict[key] += value
            else:
                self.sourceNumInCulture = 1 # For counting the number of sources ran through in case a crash appears 
                self.pasNumInSource = 1 # For counting the number of passages in a particular sourceran through in case a crash appears 
                populate_list = [0] * self.culture_dict[self.currentCulture]['Pas_Count']
                self.passage_dict = {'Region':[self.culture_dict[self.currentCulture]['Region']] * len(populate_list),
                    'SubRegion':[self.culture_dict[self.currentCulture]['SubRegion']] * len(populate_list),
                    'Culture':[self.currentCulture] * len(populate_list),
                    "DocTitle":populate_list.copy(),
                    "Section":populate_list.copy(),
                    "Author":populate_list.copy(), 
                    "Page":populate_list.copy(), 
                    "Year":populate_list.copy(), 
                    "OCM":populate_list.copy(), 
                    "OWC":populate_list.copy(),
                    "Passage":populate_list.copy()}




            # loop for every page within a culture
            sourcesRemaining = self.culture_dict[self.currentCulture]['Source_count']
            page_reload_count = 0 #for reload protection
            next_page_count = 0 # for counting the number of pages ran through in case we need to return to that page
            # source_count = 0 # May be vestigial code, potentially delete
            # Loop through Each Page


            # # Try to make the program wait until the webpage is loaded. This usually will only crash if you lose internet, but still try to save the data
            while page_reload_count <3:
                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "mdc-data-table__row")))
                except:
                    try: #try to reload the page, otherwise, pass
                        self.reload_page(self.currentCulture, next_page_count)
                    except:
                        pass
                    page_reload_count += 1
                else:
                    # page_reload_count += 1
                    break
            else:
                self.scraper_fail("failed to load all pages")

            while sourcesRemaining > 0:
                # try to determine the source count on the page
                # NOTE maximum sources per page at time of writing is 25. If this ever changes the code will break and you
                # will have to update this number or find a good way to systematically check if the new tabs are loaded (ans/or if we need to move onto the next page)
                sourceCount_page = sourcesRemaining
                maxSource_page = 25

                #Skip pages if we are restarting from a partial save and the source we need to find is on a later page
                if self.restartCrashedQuery is True and sourcesRemaining>maxSource_page and self.sourceNumInCulture >maxSource_page:
                    skipPages_num = self.sourceNumInCulture//maxSource_page
                    for skipPage_i in range(0,skipPages_num):
                        sourcesRemaining -= maxSource_page
                        #wait until we can start seeing the data

                        self.wait_webdriver(term="mdc-data-table__cell--numeric", by=By.CLASS_NAME)
                        WebDriverWait(self.driver, 10).until(lambda driver: self.wait_until_text_appears(self.driver)) #Wait until the text appears since the elements are loaded by the html but it takes some time for the html to see it.
                        #parse, extract then add the count for later finding the correct passages
                        soup = BeautifulSoup(self.driver.page_source, features="html.parser")
                        sourceCount_list = soup.find_all('td',{'class':'mdc-data-table__cell mdc-data-table__cell--numeric'})
                        sourceCount_list = list(map(lambda x: int(x.text), sourceCount_list[0::3]))
                        pas_count += sum(sourceCount_list)
                        # source_count += maxSource_page # May be vestigial code, potentially delete
                        self.nextPage()
                        next_page_count += 1 # here for potention need to restore to a page
                        self.unfSourceNumOnPage -= maxSource_page
                        assert self.unfSourceNumOnPage >0, "Error, there program is acting as if there are no sources left on the page"
                        assert sourcesRemaining >0, "Error, sources remaining should be above 0 if returning from a partial save on this culture"
                    continue # move onto next page while loop
                    # self.sourceNumInCulture % maxSource_page
                if sourceCount_page > maxSource_page:
                    sourceCount_page = maxSource_page

                # # Try to make the program wait until the webpage is loaded. This usually will only crash if you lose internet, but still try to save the data
                while page_reload_count <3:
                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "mdc-data-table__row")))
                    except:
                        try: #try to reload the page, otherwise, pass
                            self.reload_page(self.currentCulture, next_page_count)
                        except:
                            pass
                        page_reload_count += 1
                    else:
                        # page_reload_count += 1
                        break
                else:
                    self.scraper_fail("failed to load all pages")
                
                # find source tabs then assure that the source count intended to be on the page is accurate.
                sourceTabs = self.driver.find_elements(By.CLASS_NAME, 'mdc-data-table__row')


                if len(sourceTabs) != sourceCount_page:
                    try:
                        print(f"Error Correction: Source reload commencing for {self.currentCulture} on page {next_page_count+1}")
                        sourceTabs = self.reload_retry(sourceCount_page, 'mdc-data-table__row')
                    except RuntimeError:
                        self.scraper_fail("failed to load all sources upon webpage loading")


                #### Leftover for multithreading, DELETE
                # # We can use a with statement to ensure threads are cleaned up promptly
                # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                #     # Start the load operations and mark each future with its URL
                #     future_to_click = {executor.submit(self.argumentClick, source_i): source_i for source_i in sourceTabs}
                #     for future in concurrent.futures.as_completed(future_to_click):
                #         future_to_click[future]
                # # create a thread pool with 6 threads
                # pool = concurrent.futures.ThreadPoolExecutor(max_workers=6)              
                # # submit tasks to the pool
                # for source_i in sourceTabs:
                #     pool.submit(self.argumentClick, source_i)
                # # wait for all tasks to complete
                # pool.shutdown(wait=True)
                # print("Main thread continuing to run")


                if self.restartCrashedQuery: 
                    sourceTabs = sourceTabs[self.unfSourceNumOnPage-1:]
                    passagesNeededToSkip = 0 #used later for checking the passages are correctly skipped
                # Click every source tab
                for source_i in sourceTabs:
                    self.driver.execute_script("arguments[0].click();", source_i)
                    time.sleep(.1) #Sleep mainly so that we do not overdue the amount of requests at a time for the server (and get them angry)

                #Log the source table's results number in order to know where to start and stop clicking.
                # Skip every 2 logs as they do not contain the information desired
                soup = BeautifulSoup(self.driver.page_source, features="html.parser")
                sourceCount_list = soup.find_all('td',{'class':'mdc-data-table__cell mdc-data-table__cell--numeric'})
                sourceCount_list = list(map(lambda x: int(x.text), sourceCount_list[0::3]))

                
                if self.restartCrashedQuery: #If returning from partial save, skip x first sources supposedly already saved (then make sure to add them to the passage count)
                    skippedPassages = sourceCount_list[:self.unfSourceNumOnPage-1]
                    sourceCount_list = sourceCount_list[self.unfSourceNumOnPage-1:] #shorten the variable (note, this is to prevent multiple if statements in the source loop, we could easily keep this and just skip in the for loop)
                    pas_count += sum(skippedPassages) + self.pasNumInSource-1
                    if len(self.passage_dict["Passage"]) < pas_count:
                        self.scraper_fail("ERROR passage number larger than partial file. It is likely there is an error with the crash info. You may need to restart the scraping completely by either deleting the altogether excel file or selecting the option to rerun without using the partial save if you are using the GUI")
                    elif len(self.passage_dict["Passage"]) == pas_count:
                        yield self.text_print("Unexpectedly, the partial file appears to be actually complete. It could happen that the culture crashed right before completing. The scraper may be able to run but may add data erroneously. Caution is advised.")
                    elif pas_count > 0 and (self.passage_dict["Passage"][pas_count] != 0 or self.passage_dict["Passage"][pas_count -1] == 0):
                        self.scraper_fail("ERROR passage number incongruent with partial file. It is imprudent to continue as the file may become inaccurate. You may need to restart the scraping completely by either deleting the altogether excel file or selecting the option to rerun without using the partial save if you are using the GUI")

                resultsTabs_total = len(sourceCount_list)

                # loop through each source (unless we should skip) click and extract information from each passage within the result/source tabs
                for i in range(0, len(sourceCount_list)):
                    total = sourceCount_list[i]
                    tab_switch_count = 0
                    reload_page_save = 0
                    reload_tab_save = 0

                    # get the results tab(which is basically the source tab but contained within a different HTML element) for sub indexing sources
                    resultsTabs = self.driver.find_elements(By.CLASS_NAME, 'trad-data__results')

                    # If there are a lot of passages to run through, this may cause a problem with loading new sets of
                    # 10 passages (as the default is 10 at a time.) Therefore, expand to the greater number of passages if not already expanded
                    self.wait_webdriver(term="mdc-data-table__row", by=By.CLASS_NAME)
                    if max(sourceCount_list) > 10 and len(resultsTabs[i].find_elements(By.CLASS_NAME, 'trad-data__results--row')) == 10: 
                        # I think something jossles the webpage making it transition to a new dynamic webpage size and therefore changing the drop down list
                        # I am not sure why this would happen since we are just looking for the results tabs above but perhaps searching for them again upon a failure might help
                        try:
                            expander = resultsTabs[i].find_elements(By.CLASS_NAME, 'mdc-list-item')
                            self.driver.execute_script("arguments[0].click();", expander[0]) # Choose the first option, then choose the last (as for some reason, the webpage can sometimes say there is 150 but there actually isn't and therefore we must eset it)
                            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "trad-data__results")))
                            resultsTabs = self.driver.find_elements(By.CLASS_NAME, 'trad-data__results')
                            

                            expander = resultsTabs[i].find_elements(By.CLASS_NAME, 'mdc-list-item')
                            self.driver.execute_script("arguments[0].click();", expander[-1])
                        except:
                            self.scraper_fail("failed to extend frame (load longer list of passages)")

                    # in case was not enough time, redo until all the result tabs are loaded again.
                    # Otherwise, try clicking and reseting the tab to try again
                    if len(resultsTabs) != resultsTabs_total: #NOTE: due to changes to eHRAF, this is superfluous as resultTabs never changes, nevertheless this is unlikely to harm the program by leaving it in, just know that this is not a valid check anymore!
                        try:
                            resultsTabs = self.reload_retry(resultsTabs_total, 'trad-data__results')
                        except RuntimeError:
                            print("reload page save required")
                            # Attempt to save the run by resetting the tab
                            while reload_tab_save <= 2:
                                try:
                                    for j in range(0,resultsTabs_total):
                                        self.driver.execute_script("arguments[0].click();", sourceTabs[j])
                                        time.sleep(.1)  # Buffering time, just in case
                                        self.driver.execute_script("arguments[0].click();", sourceTabs[j])
                                    resultsTabs = self.reload_retry(resultsTabs_total, 'trad-data__results')
                                except RuntimeError:
                                    reload_tab_save += 1
                                    print("reload save:", reload_tab_save)
                                else:
                                    reload_tab_save += 1
                                    break
                            else:
                                self.scraper_fail("failed to load all results tabs")

                    # Loop through each tab (like 10 to 150 passages) for a single source and extract passage data for each
                    while True:
                        # retry finding the result tab as necessary

                        resultsTabs = self.driver.find_elements(By.CLASS_NAME, 'trad-data__results')

                    # self.sourceNumInCulture % maxSource_page
                        # in case there is not enough time, attempt to extract result tabs.
                        # IF the tabs will not load properly within the HTML ebpage, close them
                        # then re-open them then find where was left off.
                        if len(resultsTabs) != resultsTabs_total:   #NOTE: due to changes to eHRAF, this is superfluous as resultTabs never changes, nevertheless this is unlikely to harm the program by leaving it in, just know that this is not a valid check anymore!
                            try:
                                resultsTabs = self.reload_retry(resultsTabs_total, 
                                                                'trad-data__results')
                            except RuntimeError:
                                print("reload tab save required")
                                # try retry results tabs and run through the tabs
                                # It should repeat this loading until either it runs out of loops or it gets the correct results tab.
                                while reload_page_save <=2:
                                    try:
                                        self.driver.execute_script("arguments[0].click();", sourceTabs[i])
                                        time.sleep(1) #Buffering time, just in case
                                        self.driver.execute_script("arguments[0].click();", sourceTabs[i])
                                        resultsTabs = self.reload_retry(resultsTabs_total, 
                                                                        'trad-data__results')
                                        if sourceCount_list[i] > 10:
                                            expander = resultsTabs[i].find_elements(By.CLASS_NAME, 'mdc-list-item')
                                            self.driver.execute_script("arguments[0].click();", expander[-1])
                                        resultsTabs = self.reload_retry(resultsTabs_total,
                                                                        'trad-data__results')
                                        for j in range(tab_switch_count):
                                            SourceTabFooter = resultsTabs[i].find_elements(By.CLASS_NAME,'trad-data__results--pagination')
                                            buttons = SourceTabFooter[0].find_elements(By.CLASS_NAME, 'rmwc-icon--ligature')
                                            self.driver.execute_script("arguments[0].click();", buttons[-1])
                                            resultsTabs = self.reload_retry(resultsTabs_total,
                                                                            'trad-data__results')
                                    except RuntimeError:
                                        reload_page_save += 1
                                        
                                    else:
                                        reload_page_save += 1
                                        break
                                else:
                                    self.scraper_fail("failed to load all results tabs")
                        # explicitly wait until the doctabs can be seen (probably not necessary but can't hurt)
                        self.wait_webdriver(term='sre-result__title', target=resultsTabs[i], by=By.CLASS_NAME, text=f"Failed to load all documents after waiting for 10 seconds. It may be due to random webpage slowness" )
                    
                        pasTabs = resultsTabs[i].find_elements(By.CLASS_NAME, 'sre-result__title')
                        #Click all the passages within a source, skip passages which have already been extracted in a partial save
                        if self.restartCrashedQuery:
                            for pas in pasTabs:
                                if passagesNeededToSkip+1 < self.pasNumInSource: #If passage already extracted, skip but still count
                                    passagesNeededToSkip += 1
                                else:
                                    self.driver.execute_script("arguments[0].click();", pas)
                            if passagesNeededToSkip+1 == self.pasNumInSource:
                                self.restartCrashedQuery = False # once we have reached the part where it crashed before, we can stop relooping
                        else:
                            for pas in pasTabs:
                                self.driver.execute_script("arguments[0].click();", pas)
                                time.sleep(.05) #Sleep mainly so that we do not overdue the amount of requests at a time for the server (and get them angry)
                        #Scrape the data (the important part!)
                        try:
                            pas_count = self.dataScrape(pas_count, resultsTabs[i])
                        except:
                            self.scraper_fail(f"Scraping and extracting main data text has failed. This could be due to webpage changing or issue with the code")
                        # set remaining docs in a source tab (for clicking the "next" button if not all of them are shown)
                        total -= len(pasTabs)

                        # tab switch
                        # If there are more tabs hidden away, find the button, click it, and then refresh the results
                        # otherwise, end the loop and close the source tab to make search for information easier
                        if total >0:
                            SourceTabFooter = resultsTabs[i].find_elements(By.CLASS_NAME, 'trad-data__results--pagination')
                            buttons = SourceTabFooter[0].find_elements(By.CLASS_NAME, 'rmwc-icon--ligature')
                            self.driver.execute_script("arguments[0].click();", buttons[-1])
                            tab_switch_count += 1
                        else:
                            ## close sourcetab(this might save time in the long run)
                            self.driver.execute_script("arguments[0].click();", sourceTabs[i])
                            # resultsTabs_total -= 1 #NOTE commenting out as eHARF no longer changes counts but keeping it here in case things need to change back.
                            self.sourceNumInCulture +=1 #Source is finished, add one and continue to the next source
                            self.pasNumInSource =1 # reset back to 1 (this is for returning back to the passage you left off in case there is a crash.)
                            break #break from loop
                        
                # Run to the next page if necessary. Check to see if there are more source tabs left, if so, click the next page and continue scraping the page
                sourcesRemaining -= sourceCount_page
                if sourcesRemaining >0:
                    self.nextPage()
                    next_page_count += 1
                
            # append the attributes to the dataframe
            df_eHRAFCulture = pd.DataFrame(self.passage_dict)
            # df_eHRAFCulture[['Region','SubRegion',"Culture"]] = [self.culture_dict[self.currentCulture]['Region'], self.culture_dict[self.currentCulture]['SubRegion'], self.currentCulture ] #TODO add cultural, region, and subregion modifiers to the partial save
            # In the rare case that a person wants to create cultural files but an altogether dataset already exists, skip the scraped cultures being added to the altogether file.
            if self.currentCulture not in self.skip_cultures_altogether:
                self.df_ehraf = pd.concat([self.df_ehraf, df_eHRAFCulture], ignore_index=True)
                self.pas_count_total += pas_count # add pas_count to the total. The reason it is potetnially skipped is because in those circumstances, the altogether file should still have these passages and we do do not need to add the count again.
            # if the counts of the files scrapes does not match what should be scraped, pop up a warning
            if pas_count != self.culture_dict[self.currentCulture]['Pas_Count']:
                yield self.text_print(f"WARNING {pas_count} out of {self.culture_dict[self.currentCulture]['Pas_Count']} passages loaded for {self.currentCulture}")

            # Save Culture file if relevant
            if self.cultureFiles is True:
                self.save_file(df_eHRAFCulture, culture=self.currentCulture)
            # Save the file over a set interval in case there is an unforseen failure which did not allow partial saving
            # if the altogether dataset file is not meant to be appended (see above line) do not update the save.
            if saveRate is not None and self.currentCulture not in self.skip_cultures_altogether:
                saveRate_count += pas_count
                if saveRate_count >= saveRate:
                    self.save_file(self.df_ehraf, routine=True)
                    print(f'Routine partial saving has occurred, {self.pas_count_total} passages saved')
                    saveRate_count = 0
        self.save_file(self.df_ehraf)
        if endClose: # close the webbrowser unless otherwise said
            self.web_close()
        yield self.text_print(f'{self.pas_count_total} passages out of a possible {self.intendPas_count} saved (also check file/dataframe)')
        yield self.text_print('\n\nSCRAPING COMPLETE\n', color='blue')

    # function for executing clicks (used for multithreading.)
    def argumentClick(self, driver_query):
        print("Worker thread running")
        self.driver.execute_script("arguments[0].click();", driver_query)
        print("Worker thread complete")



    def dataScrape(self, pas_count, results):


        soup = BeautifulSoup(results.get_attribute('outerHTML'), features="html.parser") #get results just for the particular results tab
        soupDocs = soup.find_all('section',{'class':'sre-result__sre-result'})

        for soupDoc in soupDocs:
            passage = soupDoc.find('div',{'class':'sre-result__sre-content'}).text


            soupOCM = soupDoc.find_all('div',{'class':'sre-result__ocms'})
            # OCMs
            # find all direct children a tags then extract the text
            ocmTags = soupOCM[0].find_all('a', recursive=False)
            OCM_list = []
            for ocmTag in ocmTags:
                OCM_list.append(int(ocmTag.span.text))
            # OWC
            OWC = soupOCM[1].a['name']
            
            # Document title
            docMetadata = soupDoc.find('div',{'class':'sre-result__sre-content-metadata'})
            docTitle = docMetadata.div.text
            docTitle = re.sub('\s+', ' ', docTitle) #for removing extra spaces and new line characters
            # Search document's title for the document's Year of creation
            year = re.search('\(([0-9]{0,4})\)', docTitle)
            if year is not None:
                # remove the date then strip white space at the end and start to give the document's title
                docTitle = re.sub(f'\({year.group()}\)', '', docTitle).strip()
                # get the Year without the parenthesis
                year = int(year.group()[1:-1])

            # search document's title for section
            section = re.search('Section:(.*)', docTitle)
            if section is not None: #if a section exists and can be scraped, then put it into the list for the dataframe and remove it from the document's title
                section = section.group(1).strip() #extract the match
                docTitle = re.sub('Section:.*', '',docTitle).strip() #remove the section text

            # extract Author
            author = docMetadata.span.text
            author = re.search('By:(.*)', author)
            if author is not None:
                author = author.group(1).strip() #extract the match
                # sometimes the self.author has a Year attributed to them at the end

            # extract page
            pageNum = docMetadata.span.next_sibling.text
            pageNum = re.search('Page:(.*)', pageNum)
            if pageNum is not None:
                pageNum = pageNum.group(1).strip() #extract the match

            # # Added failure on purpose REMOVE in actual scraper
            # try:
            #     inducedCrashNum = self.inducedCrashNum
            # except:
            #     inducedCrashNum = -9999
            # inducedCrashNum = 5
            # if self.crashed is False and self.pas_count_total + pas_count == inducedCrashNum:
            #     assert self.pas_count_total < -9999, "PURPOSEFUL FAILURE FOR TEST, REMOVE THIS IF IT IS STILL HERE"

            #Ascribe to dictionary (this is done at the end with local variables rather than using a dictionary throughout the scraping as this way appears cleaner even if it is potentially slower)
            self.passage_dict['Passage'][pas_count] = passage
            self.passage_dict['DocTitle'][pas_count] =docTitle 
            self.passage_dict['Section'][pas_count] =section
            self.passage_dict['Author'][pas_count] =author
            self.passage_dict['Page'][pas_count] =pageNum
            self.passage_dict['Year'][pas_count] =year
            self.passage_dict['OCM'][pas_count] =OCM_list
            self.passage_dict['OWC'][pas_count] = OWC

            self.pasNumInSource +=1 #recording the passage place inside the source for potential later crashes


            pas_count += 1
        return pas_count

    def reload_retry(self, idealCount, searchText):
        reload_protect = 0
        reloadTab = self.driver.find_elements(By.CLASS_NAME, searchText)
        while idealCount != len(reloadTab) and reload_protect <= 100:
            time.sleep(.1)
            reloadTab = self.driver.find_elements(By.CLASS_NAME, searchText)
            reload_protect += 1
        if reload_protect > 100:
            raise RuntimeError("Too many reloads")
        return reloadTab
    def scraper_fail(self, text):
        # create fail and exception text variables in order to be able to be referenced outside the program
        self.fail_text = ""
        df_eHRAFCulture = pd.DataFrame(self.passage_dict)
        df_eHRAFCulture = df_eHRAFCulture.loc[df_eHRAFCulture["Passage"]!=0] #remove blanks
        self.df_ehraf = pd.concat([self.df_ehraf, df_eHRAFCulture])
        if len(self.df_ehraf) < 1 or self.df_ehraf is None:
            self.fail_text += "Not enough data to create a save file\n\n"
        else:
            self.save_file(self.df_ehraf, crashed=True)
            if self.failureClose: #if desired to close on failure
                self.web_close()
            self.fail_text += "Partial saving has occurred, please rerun the program to restart at the culture left off\n\n"
            self.fail_text += f'{self.pas_count_total + len(df_eHRAFCulture)} passages out of a possible {self.intendPas_count} saved (also check file/dataframe)\n\n' 
        self.restartCrashedQuery = True
        self.crashed = True
        print(self.fail_text)
        self.exception_text= f"{text}, consider checking terminal for more info"
        self.logCrash(self.exception_text)
        print(f"Crashed at:\nCulture: {self.currentCulture}\nSource Number (in Culture): {self.sourceNumInCulture}\nPassage Number (in Source): {self.pasNumInSource}")
        raise Exception(self.exception_text)
    def logCrash(self, exception_text=None):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%m/%d/%y")

        currentCulture = "NA"
        sourceNumInCulture = "NA"
        pasNumInSource = "NA"
        # Get the crash stats if available
        try:
            if exception_text is None:
                exception_text = self.exception_text
            currentCulture = self.currentCulture
            sourceNumInCulture = self.sourceNumInCulture
            pasNumInSource = self.pasNumInSource
        except:
            pass

        df_crash = pd.DataFrame({"date":[current_date], "time":[current_time], "input_URL":[self.URL], "crashed_text":[exception_text], "crashed_culture":[currentCulture], "crashed_source":[sourceNumInCulture], "crashed_passage":[pasNumInSource]})

        if os.path.isfile("crash_log.csv"):
            df_crashFile = pd.read_csv("crash_log.csv", index_col=0)
            df_crashFile = pd.concat([df_crashFile,df_crash]).reset_index(drop=True)
        else:
            df_crashFile = df_crash
        df_crashFile.to_csv("crash_log.csv")

    def reload_page(self, key, next_page_count): #reload the page and try to start at the page number left off for the culture
        self.driver.get(self.homeURL + self.culture_dict[key]['link'])
        # return to the page where this failed originally
        if next_page_count >0:
            next_page_count_loop = next_page_count
            while next_page_count_loop >0:
                self.nextPage()
                next_page_count_loop -= 1 
    def nextPage(self): # Go to next page
        self.wait_webdriver(term="//button[@title='Next Page']",  by=By.XPATH, text=f"Unable to go to the next page" )
        next_page = self.driver.find_element(By.XPATH, "//button[@title='Next Page']")
        self.driver.execute_script("arguments[0].click();", next_page)
        self.wait_webdriver(term="//td[@class='mdc-data-table__cell mdc-data-table__cell--numeric']",  by=By.XPATH)#wait until page is loaded (as of writing this, it is not waiting long enough.)
    def output_dir_cons(self):# Clean URL to use as a file name and to put it into the excel file as data
        replace_dict = {'%28':'(', '%29':')', '%3A':':', '%7C':'|', '%3B':';', '%22':'\"', '%27':'\'', '\+':' '}
        remove_list = [self.homeURL, 'search', '\?q='] #some characters are redundantly changed above so that it is easier to see what the characters mean (like %7C)

        folder_name = self.URL

        # replace HTML characters with their corresponding characters
        for key, val in replace_dict.items():
            folder_name = re.sub(key, val, folder_name)
        #remove common undesirable characters 
        for i in remove_list:
            folder_name = re.sub(i, '', folder_name)

        self.input_name = folder_name #save a copy before extra filtering as this will be used later in the file
        self.input_filters = 'No filters'

        # regex for finding filters if they are there
        reg = re.findall('.*&fq=(.*)', folder_name)
        # if filters are present, reshape and beautify
        if len(reg) >0:
            self.input_name = re.sub('&fq='+re.escape(reg[0]),'',self.input_name)
            self.input_filters = reg[0]

            folderFilter = ''
            # # second regex for finding the filter types and names, producing a smaller filter name than before
            # filterNames = ["".join(x) for x in re.findall('\|(.*?);|\|(.*?)$', reg[0])] #old way to get the names and erasing the unneeded tuple
            reg2 = re.findall('[^\|;]+', reg[0]) #extract filter types and names
            filterTypes_set = set()
            for filterName, filterType in zip(reg2[1::2], reg2[0::2]):
                if filterType in filterTypes_set:
                    folderFilter += f',{filterName}'
                else:
                    folderFilter += f')-{filterType}({filterName}'
                    filterTypes_set.add(filterType)
            folderFilter = folderFilter[2:] + ')' #erase the first paranthesis
            # subsitute space for underscores
            folderFilter = re.sub(' ','_',folderFilter)


            # Give a space between input filters for readability (and maybe splitting later)
            self.input_filters = re.sub(';', ';\n', self.input_filters)
            self.input_filters = re.sub('_', ' ', self.input_filters)


            # now add the corrected filters back to the URL file name,
            folder_name = re.sub(re.escape(reg[0]), folderFilter, folder_name)
        return folder_name
    def folderNameClean(self, folder_name):    # remove and replace the characters not good for a file name
        replace_dict_file = {'fq=':'_FILTERS-', ':':'-', ' ':'_'}
        remove_list_file = ['\"', '\'', ':','|','&', '\\', '/', '?', '!', '*', '^', '%', '$', '{', '}', '@', '#', '=', '+', ' ']
        # replace illegal characters
        for key, val in replace_dict_file.items():
            folder_name = re.sub(key, val, folder_name)
        for i in remove_list_file:
            folder_name = re.sub(re.escape(i), '', folder_name)

        #Simply check to make sure the file name is a good length, otherwise snip it off
        self.file_length_warning = None
        if len(folder_name) > 240:
            folder_name = folder_name[:240]
            self.file_length_warning = "WARNING, file name is too big and has been cut off, this can cause overwriting and/or use of same named queries"
            print(self.file_length_warning)
            # # remove filters (Old, currently just snipping off the ends of files)
            # reg2 = re.findall('_FILTERS.*', folder_name)
            # if len(reg2) > 0:
            #     folder_name = re.sub(reg2, '', folder_name)
            # # if file is still too long, go into basic cutting
            # if len(folder_name) > 240:
        return folder_name     
    def createDataDir(self, folder_name:str):    # Create the dat directory, this is also used for the other functions to see if a partial file is already present
        # output directory
        output_dir = "Data"  

        # Find path
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            # # # allow users to access the data folder
            app_dir = os.path.dirname(sys.executable)
            self.application_path = os.path.join(app_dir)
        else:
            self.application_path = os.path.dirname(__file__)

        output_dir_path = self.application_path + '/' + output_dir  # output directory path
        os.makedirs(output_dir_path, exist_ok=True)  # make Data folder if it does not exist
        self.folder_path = output_dir_path + '/' + folder_name   #find where the folder should be locate
        self.file_Path = self.folder_path + '/_Altogether_Dataset.xlsx' #find where the altogether dataset should be located
    def partial_file_return(self):# if there already exists a file that contains this specific search pattern, then load the data

        self.df_ehraf = pd.read_excel(self.file_Path, index_col=0)
        try:
            crash_text = self.df_ehraf.iloc[6]['run_Info']
        except:
            crash_text = None
        crashSpotDetermined = False

        if isinstance(crash_text, str):
            if re.match("^Crashed", crash_text):
                try:
                    regx = re.findall("CULTURE:(.*)", crash_text)
                    self.unfCulture = regx[0]
                    regx = re.findall("SOURCE NUMBER:(\w*)", crash_text)
                    self.unfSourceNumInCulture = int(regx[0])
                    regx = re.findall("PASSAGE NUMBER:(\w*)", crash_text)
                    self.unfPasNumInSource = int(regx[0])
                    self.unfSourceNumOnPage = self.unfSourceNumInCulture
                    # store the unfinished culture and remove it from the altogether dataframe
                    self.unfPassage_dict =  dict(self.df_ehraf.loc[self.df_ehraf["Culture"]==self.unfCulture])
                    self.df_ehraf = self.df_ehraf.loc[self.df_ehraf["Culture"]!=self.unfCulture]
                    self.df_ehraf = self.df_ehraf.dropna()
                    self.unfPassage_dict.pop('run_Info', None) #Remove run_Info column just to make sure we do not have any later concatination problems
                    for key in self.unfPassage_dict.keys(): # the dictionary is a series so we will turn it back to a list for ease
                        self.unfPassage_dict[key] = list(self.unfPassage_dict[key])
                    crashSpotDetermined = True
                except:
                    print("WARNING unable to determine all the last states of the file. This scraping will NOT start where you left off and instead skip to the next culture")
                    crashSpotDetermined = False
            elif re.match("^FINISHED SCRAPING", crash_text):
                print("WARNING The scraping has been marked as finished, and no more files will be scraped")
            else:
                print("WARNING unidentified state of partial file. This may be due to a legacy partial file being ran in new scraping system. The file will not finish any partial cultures that have been left unfinished")
        else:
            print("WARNING unidentified state of partial file. This may be due to a legacy partial file being ran in new scraping system. The file will not finish any partial cultures that have been left unfinished")
        # If we cannot find where it crashed, attempt to redo any partially completed cultures by removing the partial cultures from the dataframe (this will make the program attempt to do them again)
        if crashSpotDetermined == False:
            disparityCult_list = []
            self.unfCulture = None
            self.restartCrashedQuery = False #Since we are no longer skipping passages and starting from the begining, set this to False
            for uniqueCult in self.df_ehraf["Culture"].unique():
                if len(self.df_ehraf.loc[self.df_ehraf["Culture"]==uniqueCult]) != self.culture_dict[uniqueCult]['Pas_Count']:
                    disparityCult_list += [uniqueCult]
            if len(disparityCult_list) == 1:
                self.df_ehraf = self.df_ehraf.loc[self.df_ehraf["Culture"]!=disparityCult_list[0]] #Remove unfinished culture from DF so it can be redone
                print(f"{disparityCult_list[0]} will be redone as it is partially finished but a crash point was not determined")
            elif len(disparityCult_list) >1:
                print("WARNING, more than one unfinished culture found, this is unlikely and could mean a separate problem or there was editting of the file")
                for cult in disparityCult_list:
                    self.df_ehraf = self.df_ehraf.loc[self.df_ehraf["Culture"]!=cult]
                    print(f"{cult} will be redone as it is partially finished but a crash point was not determined")


        self.pas_count_total = sum(~self.df_ehraf['Region'].isna())
        if "run_Info" in self.df_ehraf.columns: # drop run_Info to make sure there are no later concatination problems
            self.df_ehraf = self.df_ehraf.drop('run_Info', axis=1)

        # If you are creating individual culture files, skipped cultures are determined by if the actual file already exists.
        # Otherwise find skipped files via the altogether dataset
        if self.cultureFiles is True:
            xlsx_files = [f for f in os.listdir(self.folder_path) if f.endswith('.xlsx')] #get all files with '.xlsx
            skip_cultures = [i.split('.')[0] for i in xlsx_files] #as we get "culture.xlsx" files back, split at the '.' and only take the "culture" putting it into a list. This will also include "_Altogether_Dataset but this should not matter"
            self.skip_cultures_altogether = set(self.df_ehraf["Culture"]) #Skip cultures which are assumedly in the altogether file but not made as individual cultural files
        else:
            skip_cultures = set(self.df_ehraf["Culture"])

        # delete cultures in the dictionary already present (probably could rewrite reduce the for loop by 1 but this is probably okay)
        delete_key_list = []
        for key in self.culture_dict.keys():
            if key in skip_cultures:
                delete_key_list.append(key)
        for key in delete_key_list:
            del self.culture_dict[key]

        return crashSpotDetermined
    def wait_webdriver(self, term, target=None, time=10, by=By.CLASS_NAME, text = None):
        try:
            if target == None:
                target = self.driver
            WebDriverWait(target, time).until(EC.presence_of_element_located((by, term)))
        except:
            if text == None:
                text = f"Web scraper unable to find {term} in a reasonable set time frame"
            self.scraper_fail(text)
    def save_file(self, df, routine = False, culture=None, crashed=False):
      

        # only add run info to the dataframe if saving an idividual culture or (saving for the first time and not starting from a partial file).
        if culture is not None or (self.repeatSave is False):
            # get time and date that this program was run
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%m/%d/%y")

            # place run information within the "run_Info" column
            # df['run_Info'] = None
            df = df.reset_index(drop=True)
            df.loc[0,'run_Info'] = "User: " + self.user
            df.loc[1,'run_Info'] = "Run Time: " + str(current_time)
            df.loc[2,'run_Info'] = "Run Date: " + str(current_date)
            df.loc[3,'run_Info'] = "Run Input: " + self.input_name
            df.loc[4,'run_Info'] = "Filter:\n" + self.input_filters
            df.loc[5,'run_Info'] = "Run URL: " + self.URL

            if crashed: #If finished, indicate we are done, otherwise, indicate the culture, source and passage that failed it so we can reset it back
                df.loc[6,'run_Info'] = f"Crashed or terminated on {str(current_date)} at {str(current_time)}. The file is incomplete.\nCrashed at:\nCULTURE:{self.currentCulture}\nSOURCE NUMBER:{self.sourceNumInCulture}\nPASSAGE NUMBER:{self.pasNumInSource}\nPlease rerun the program. DO NOT ALTER THIS CELL"
            else:
                if routine:
                    df.loc[6,'run_Info'] = f"Routine save, please continue as the scraping is unfinished. last culture scraped was {self.currentCulture}"
                else:
                    assert self.pas_count_total == self.intendPas_count, f"SCRAPING EXPECTED COUNTS DO NOT LINE UP: Passage total already logged: {self.pas_count_total}, Passage total intended to be logged: {self.intendPas_count} "
                    df.loc[6,'run_Info'] = f"FINISHED SCRAPING {self.pas_count_total} of {self.intendPas_count}"

        # Use the normal file path unless we are saving to individual cultures
        if culture is None:
            save_file_path = self.file_Path
        else:
            save_file_path = self.folder_path + '/' + culture + '.xlsx'

        df.index += 1
        os.makedirs(self.folder_path, exist_ok=True)  # make dataset folder if it does not exist
        try:
            df.to_excel(save_file_path, index=True, index_label = "Passage Number")
        except:
            raise Exception('unable to save to file, make sure the file is not currently open')
        if routine is False:
            print(f'Saved to {self.folder_path}')

    # Simple function which just both prints and returns the text
    def text_print(self, text, color=None): 
        print(text)
        if self.GuiInUse:
            if color is not None:
                text = f"<font color='{color}'>{text}</font>"
            return text
        else:
            return ""

    def wait_until_text_appears(self, driver): # annoying wait for partial save return
        try:
            elements = driver.find_elements(By.CLASS_NAME, "mdc-data-table__cell--numeric")
            return any(td.text.strip() for td in elements)
        except:
            return False  # Keeps retrying if stale element error occurs
    def web_close(self):
        # close the webpage
        try:
            self.driver.close()
        except:
            print("driver attempted to close but failed. Likely due to webpage already closed")
    def __del__(self): # if the class gets overwrittten,  remove the webpage
        try:
            self.driver.close()
        except:
            pass

