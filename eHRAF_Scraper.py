
#### **Author** -- Eric Chantland (ericchantland@gmail.com)
#### **Created** -- October 2022


# NOTE: This is the behind the scenes python code for the eHRAF GUI which is designed to scrape document files from
# eHRAF based on the user's search selections. This should run nearly identical to the eHRAF_Scraper.ipynb albeit
# with more focus on making the GUI side work. If you are new to the project, I highly recommend checking out
# eHRAF_Scraper.ipynb as it contains a bit more description as to what the code is doing.



import pandas as pd                 # dataframe storing
from bs4 import BeautifulSoup       # parsing web content in a nice way
import os                           # Find where this file is located.
import sys                          # Also for finding file location (for saving)
import re                           # regex for searching through strings
import time                         # for waiting for the page to load
import selenium
import webdriver_manager


from selenium import webdriver      # load and run the webpage dynamically.
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# for wait times
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper:
    def __init__(self, url=None, user=None, rerun=False, headless=False):
        if url is not None:
            self.URL = url
        # if no inputs are received,set URL to the default Apple demo
        if url is None:
            self.URL = r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF'
        if user is None:
            self.user = "No Name Specified"
        else:
            try:
                self.user = str(user)
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                raise
        

        # (optional) iniate "headless" which stops chrome from showing itself when this is run,
        # switch headless to False if you want to see the webpage or True if you want it to run in the background
        options = Options()
        options.headless = headless


        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # here for later gui integration
        self.homeURL = "https://ehrafworldcultures.yale.edu/"
        searchTokens = self.URL.split('/')[-1]

        # Load the HTML page and make it full screen to account for responsive webpage sizes
        self.driver.get(self.homeURL + searchTokens)
        try:
            self.driver.set_window_size(1100,1100)
        except: #in case a computer cannot handle the set size (which it should but still)
            self.driver.fullscreen_window()
        # if a partial file is already present, append to that file
        self.querySkipper = False
        self.output_dir_path()
        if rerun is False:
            if os.path.isfile(self.file_Path):
                print("File with the same search query found, skipping successfully scraped cultures")
                self.querySkipper = True

    def region_scraper(self):

        # Find then click on each tab to reveal content for scraping
        # Elements must be individually clicked backwards. I do not know why this is a thing but my guess is each
        # clicked tab adds HTML pushing future tabs to a new location thereby making some indexing no longer point to a retrieved tab.
        # Loading backwards avoids this.
        country_tab = self.driver.find_elements(By.CLASS_NAME,"trad-overview__result")
        if len(country_tab) <1:
            return "No search results found, be sure you are not over filtering"
        for ct_i in range(len(country_tab)-1,-1,-1):
            try:
                # self.driver.execute_script("arguments[0].click();", country_tab[ct_i])
                country_tab[ct_i].click()
            except:
                print(f"WARNING region {ct_i} failed to be clicked, possibly because unrelated regions were initially found")
        # Parse processed webpage with BeautifulSoup (wait to make sure they are there first)
        WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'mdc-data-table__row')))
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")

        # extract the number of passages in documents intended to be found
        self.pas_count = soup.find_all("span", {'class': 'found__results'})
        self.pas_count = self.pas_count[0].small.em.next_element
        self.pas_count = int(self.pas_count.split()[1])

        self.doc_URL_finder(soup=soup)
    def time_req(self):
        # estimate the time this will take
        import math
        time_sec = self.pas_count / 4.33
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
        return f"This will scrape up to {self.pas_count} passages and take roughly \n{time_hour}{time_min}{time_sec}"

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
            doc_count = int(culture_list[-1].text)

            self.culture_dict[cultureName] = {"Region": region, "SubRegion": subRegion, "link": link, "Source_count": source_count, "Doc_Count": doc_count,  "Reloads": {"source_reload": 0, "results_reload": 0}}
        # print(f"Number of cultures extracted {len(culture_dict)}")
    def doc_scraper(self):

        # If we have a partial file, load it, otherwise  create dataframe to hold all the data
        if self.querySkipper:
            df_eHRAF, pas_count_total = self.partial_file_return()
        else:
            pas_count_total = 0
            df_eHRAF = pd.DataFrame({"Region":[], "SubRegion":[], "Culture":[], 'DocTitle':[], 'Year':[], "OCM":[], "OWC":[], "Passage":[]})

        # For each Culture, go to their webpage link then scrape the document data
        for key in self.culture_dict.keys():
            self.driver.get(self.homeURL + self.culture_dict[key]['link'])
            pas_count = 0

            # Preallocate space to save on speed
            Year = list(i for i in range(self.culture_dict[key]['Doc_Count']))
            docPassage = Year.copy()
            DocTitle = Year.copy()
            OCM_list = Year.copy()
            OWC = Year.copy()
            # loop for every page within a culture
            source_total = self.culture_dict[key]['Source_count']
            while source_total > 0:
                # try to determine the source count on the page
                # NOTE maximum page number at time of writing is 25. If this ever changes the code will break and you
                # will have to update this number or find a good way to systematiclaly check if the new tabs are loaded
                sourceCount_page = source_total
                if sourceCount_page > 25:
                    sourceCount_page = 25

                # # Try to make the program wait until the webpage is loaded (outdated)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "mdc-data-table__row")))
                # reload until the "correct" number of source tabs are retrived
                sourceTabs = self.driver.find_elements(By.CLASS_NAME, 'mdc-data-table__row')
                if len(sourceTabs) != sourceCount_page:
                    try:
                        sourceTabs = self.reload_retry(sourceCount_page, 'mdc-data-table__row')
                    except RuntimeError:
                        self.reload_fail(df_eHRAF, pas_count_total, "Sources")

                # Click every source tab
                for source_i in sourceTabs:
                    self.driver.execute_script("arguments[0].click();", source_i)

                #Log the source table's results number in order to know where to start and stop clicking.
                # Skip every 2 logs as they do not contain the information desired
                soup = BeautifulSoup(self.driver.page_source, features="html.parser")
                sourceCount = soup.find_all('td',{'class':'mdc-data-table__cell mdc-data-table__cell--numeric'})
                sourceCount_list = list(map(lambda x: int(x.text), sourceCount[0::3]))
                resultsTabs_total = len(sourceCount_list)
                # click and extract information from each passage within the result/source tabs
                for i in range(0, len(sourceCount_list)):
                    total = sourceCount_list[i]
                    tab_switch_count = 0
                    reload_page_save = 0
                    reload_tab_save = 0
                    # get the results tab(which is basically the source tab but contained within a different HTML element) for sub indexing sources
                    resultsTabs = self.driver.find_elements(By.CLASS_NAME, 'trad-data__results')
                    # in case was not enough time, redo until all the result tabs are loaded again.
                    # Otherwise, try clicking and reseting the tab to try again
                    if len(resultsTabs) != resultsTabs_total:
                        try:
                            resultsTabs = self.reload_retry(resultsTabs_total, 'trad-data__results')
                        except RuntimeError:
                            # Attempt to save the run by resetting the tab
                            while reload_tab_save <= 2:
                                try:
                                    self.driver.execute_script("arguments[0].click();", sourceTabs[i])
                                    time.sleep(1)  # Buffering time, just in case
                                    self.driver.execute_script("arguments[0].click();", sourceTabs[i])
                                    resultsTabs = self.reload_retry(resultsTabs_total, 'trad-data__results')
                                except RuntimeError:
                                    reload_tab_save += 1
                                else:
                                    reload_tab_save += 1
                                    break
                            else:
                                self.reload_fail(df_eHRAF, pas_count_total, "results")

                    # If there are a lot of passages to run through, this may cause a problem with loading new sets of
                    # 10 passages (as the default is 10 at a time.) Therefore, expand to the greater number of passages
                    if sourceCount_list[i] > 10:
                        expander = resultsTabs[0].find_elements(By.CLASS_NAME, 'mdc-list-item')
                        self.driver.execute_script("arguments[0].click();", expander[-1])

                    # loop until the program can click and find every piece of information for each passage (this is probably where things will break if times are off)
                    while True:
                        # reload the result tab as necessary
                        resultsTabs = self.driver.find_elements(By.CLASS_NAME, 'trad-data__results')
                        # in case there is not enough time, attempt to extract result tabs.
                        # IF the tabs will not load properly within the HTML ebpage, close them
                        # then re-open them then find where was left off.
                        if len(resultsTabs) != resultsTabs_total:
                            try:
                                resultsTabs = self.reload_retry(resultsTabs_total,
                                                                'trad-data__results')
                            except RuntimeError:
                                # try reloading the page and run through the tabs
                                # It should repeat this loading until either it runs out of loops or it gets the correct results tab.
                                while reload_page_save <=2:
                                    try:
                                        self.driver.execute_script("arguments[0].click();", sourceTabs[i])
                                        time.sleep(1) #Buffering time, just in case
                                        self.driver.execute_script("arguments[0].click();", sourceTabs[i])
                                        resultsTabs = self.reload_retry(resultsTabs_total,
                                                                        'trad-data__results')
                                        if sourceCount_list[i] > 10:
                                            expander = resultsTabs[0].find_elements(By.CLASS_NAME, 'mdc-list-item')
                                            self.driver.execute_script("arguments[0].click();", expander[-1])
                                        resultsTabs = self.reload_retry(resultsTabs_total,
                                                                        'trad-data__results')
                                        for j in range(tab_switch_count):
                                            SourceTabFooter = resultsTabs[0].find_elements(By.CLASS_NAME,'trad-data__results--pagination')
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
                                    self.reload_fail(df_eHRAF, pas_count_total, "results")
                        # explicitly wait until the doctabs can be seen (probably not necessary but can't hurt)
                        try:
                            WebDriverWait(resultsTabs[0], 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'sre-result__title')))
                        except:
                            self.reload_fail(df_eHRAF, pas_count_total, "document")
                        docTabs = resultsTabs[0].find_elements(By.CLASS_NAME, 'sre-result__title')
                        #Click all the tabs within a source
                        for doc in docTabs:
                            self.driver.execute_script("arguments[0].click();", doc)
                        soup = BeautifulSoup(self.driver.page_source, features="html.parser")

                        #Extract the passage INFO here
                        soupDocs = soup.find_all('section',{'class':'sre-result__sre-result'}, limit=len(docTabs))
                        for soupDoc in soupDocs:
                            docPassage[pas_count] = soupDoc.find('div',{'class':'sre-result__sre-content'}).text

                            soupOCM = soupDoc.find_all('div',{'class':'sre-result__ocms'})
                            # OCMs
                            # find all direct children a tags then extract the text
                            ocmTags = soupOCM[0].find_all('a', recursive=False)
                            OCM_list[pas_count] = []
                            for ocmTag in ocmTags:
                                OCM_list[pas_count].append(int(ocmTag.span.text))
                            # OWC
                            OWC[pas_count] = soupOCM[1].a['name']

                            DocTitle[pas_count] = soupDoc.find('div',{'class':'sre-result__sre-content-metadata'})
                            DocTitle[pas_count] = DocTitle[pas_count].div.text
                            # Search for the document's year of creation
                            Year[pas_count] = re.search('\(([0-9]{0,4})\)', DocTitle[pas_count])
                            if Year[pas_count] is not None:
                                # remove the date then strip white space at the end and start to give the document's title
                                DocTitle[pas_count] = re.sub(f'\({Year[pas_count].group()}\)', '', DocTitle[pas_count]).strip()
                                # get the year without the parenthesis
                                Year[pas_count] = int(Year[pas_count].group()[1:-1])
                            pas_count += 1
                            # df_eHRAFCulture = pd.concat([df_eHRAFCulture, df_Doc], ignore_index=True)
                        # set remaining docs in a source tab (for clicking the "next" button if not all of them are shown)
                        total -= len(docTabs)

                        # tab switch
                        # If there are more tabs hidden away, find the button, click it, and then refresh the results
                        # otherwise, end the loop and close the source tab to make search for information easier
                        if total >0:
                            SourceTabFooter = resultsTabs[0].find_elements(By.CLASS_NAME, 'trad-data__results--pagination')
                            buttons = SourceTabFooter[0].find_elements(By.CLASS_NAME, 'rmwc-icon--ligature')
                            self.driver.execute_script("arguments[0].click();", buttons[-1])
                            tab_switch_count += 1
                        else:
                            ## close sourcetab(this might save time in the long run)
                            self.driver.execute_script("arguments[0].click();", sourceTabs[i])
                            resultsTabs_total -= 1
                            break #break from loop
                # Run to the next page if necessary. Check to see if there are more source tabs left, if so, click the next page and continue scraping the page
                source_total -= len(sourceCount_list)
                if source_total >0:
                    next_page = self.driver.find_element(By.XPATH, "//button[@title='Next Page']")
                    self.driver.execute_script("arguments[0].click();", next_page)

            # append the attributes to the dataframe
            df_eHRAFCulture = pd.DataFrame({'DocTitle': DocTitle, 'Year': Year, "OCM": OCM_list,
                                            "OWC": OWC, "Passage": docPassage})
            df_eHRAFCulture[['Region','SubRegion',"Culture"]] = [self.culture_dict[key]['Region'], self.culture_dict[key]['SubRegion'], key ]
            df_eHRAF = pd.concat([df_eHRAF, df_eHRAFCulture], ignore_index=True)
            pas_count_total += pas_count
            if pas_count != self.culture_dict[key]['Doc_Count']:
                print(f"WARNING {pas_count} out of {self.culture_dict[key]['Doc_Count']} passages loaded for {key}")

        self.save_file(df_eHRAF)
        self.web_close()
        print(f'{pas_count_total} passages out of a possible {self.pas_count} loaded (also check dataframe)')

    # if there already exists a file that contains this specific search pattern, then reload the data
    def partial_file_return(self):
        df_eHRAF = pd.read_excel(self.file_Path)
        pas_count_total = len(df_eHRAF)
        skip_cultures = set(df_eHRAF["Culture"])

        # delete cultures in the dictionary already present
        delete_key_list = []
        for key in self.culture_dict.keys():
            if key in skip_cultures:
                delete_key_list.append(key)
        for key in delete_key_list:
            del self.culture_dict[key]


        return df_eHRAF, pas_count_total
    def reload_retry(self, idealCount, searchText):
        reload_protect = 0
        reloadTab = self.driver.find_elements(By.CLASS_NAME, searchText)
        while idealCount != len(reloadTab) and reload_protect <= 150:
            time.sleep(.1)
            reloadTab = self.driver.find_elements(By.CLASS_NAME, searchText)
            reload_protect += 1
        if reload_protect > 150:
            raise RuntimeError("Too many reloads")
        return reloadTab
    def reload_fail(self, df, pas_count_total, text):
        if len(df) < 1 or df is None:
            print("Not enough data to create a saved file")
        else:
            self.save_file(df)
            self.web_close()
            print("Partial saving has occurred, please rerun the program to restart at the culture left off")
            print(
                f'{pas_count_total} passages out of a possible {self.pas_count} loaded (also check dataframe)')
        raise Exception(
            f"failed to load all {text} tabs, please contact ericchantland@gmail.com for info on fixing the time waits")
    def output_dir_path(self):
        # clean and strip the URL to be put into the excel document
        replace_dict = {'%28':'(', '%29':')', '%3A':'~', '%7C':'|', '%3B':';'}
        remove_list = [self.homeURL, 'search', '\?q=', 'fq=', '\&', '\|', 'culture_level_samples'] #some characters are redundantly changed above so that it is easier to see what the characters mean (like %7C)

        URL_name = self.URL

        for key, val in replace_dict.items():
            URL_name = re.sub(key, val, URL_name)
        for i in remove_list:
            URL_name = re.sub(i, '', URL_name)
        

        self.URL_name_nonPlussed = re.sub('\+', ' ', URL_name)

        # Find path
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        else:
            raise Exception("Unable to find application path. Potentially neither script file nor frozen file")

        self.output_dir = "Data"  # output directory
        self.output_dir_path = application_path + '/' + self.output_dir  # output directory path
        os.makedirs(self.output_dir_path, exist_ok=True)  # make Data folder if it does not exist

        self.file_Path = self.output_dir_path + '/' + URL_name + '_web_data.xlsx'
    def save_file(self, df):
        # get time and date that this program was run
        from datetime import datetime
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%m/%d/%y")


        df_eHRAF = df
        if self.querySkipper is False:
            # place run information within the "run_info" column
            df_eHRAF['run_Info'] = None
            df_eHRAF.loc[0, 'run_Info'] = "User: " + self.user
            df_eHRAF.loc[1, 'run_Info'] = "Run Time: " + str(current_time)
            df_eHRAF.loc[2, 'run_Info'] = "Run Date: " + str(current_date)
            df_eHRAF.loc[3, 'run_Info'] = "Run Input: " + self.URL_name_nonPlussed
            df_eHRAF.loc[4, 'run_Info'] = "Run URL: " + self.URL

        df_eHRAF.to_excel(self.file_Path, index=False)
        return f'saved to {self.output_dir_path}'
    def web_close(self):
        # close the webpage
        self.driver.close()
    # if the class gets overwrittten,  remove the webpage
    def __del__(self):
        try:
            self.driver.close()
        except:
            pass

