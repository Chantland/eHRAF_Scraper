
#### **Author** -- Eric Chantland (ericchantland@gmail.com)
#### **Created** -- October 2022


# NOTE: This is the behind the scenes python code for the eHRAF GUI which is designed to scrape document files from
# eHRAF based on the user's search selections. This should run nearly identical to the eHRAF_Scraper.ipynb albeit
# with more focus on making the GUI side work. If you are new to the project, I highly recommend checking out
# eHRAF_Scraper.ipynb as it contains a bit more description as to what the code is doing.



import pandas as pd                 # dataframe storing
from bs4 import BeautifulSoup       # parsing web content in a nice way
import os                           # Find where this file is located.
import re                           # regex for searching through strings
import time                         # for waiting for the page to load
import libpythonpro
from selenium import webdriver      # load and run the webpage dynamically.
from selenium.webdriver.chrome.options import Options

# for wait times
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper:
    def __init__(self, user=None, url=None, param_dict=None, headless=False):
        if url is not None:
            self.URL = url
        # if no inputs are received,set URL to the default Apple demo
        if url is None and param_dict is None:
            self.URL = r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF'
        if param_dict is not None:
            pass
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

        # Unless you want to change to location, make sure the chromedriver program is located within the same file folder that you run this application in.
        # You must have chrome (or download another browser driver and change the path). Download the chrome software here: https://chromedriver.chromium.org/downloads
        path = os.getcwd() + "/chromedriver"
        self.driver = webdriver.Chrome(executable_path=path, options=options)

        self.homeURL = "https://ehrafworldcultures.yale.edu/"
        searchTokens = self.URL.split('/')[-1]

        # Load the HTML page (note that this should be updated to allow for modular input)
        self.driver.get(self.homeURL + searchTokens)

    def region_scraper(self):

        # Find then click on each tab to reveal content for scraping
        # Elements must be individually clicked backwards. I do not know why this is a thing but my guess is each
        # clicked tab adds HTML pushing future tabs to a new location thereby making some indexing no longer point to a retrieved tab.
        # Loading backwards avoids this.
        country_tab = self.driver.find_elements_by_class_name('trad-overview__result')
        for ct_i in range(len(country_tab)-1,-1,-1):
            try:
                country_tab[ct_i].click()
            except:
                print(f"WARNING tab {ct_i} failed to be clicked")

        # Parse processed webpage with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")

        # extract the number of documents intended to be found
        self.document_count = soup.find_all("span", {'class':'found__results'})
        self.document_count = self.document_count[0].small.em.next_element
        self.document_count = int(self.document_count.split()[1])

        self.doc_URL_finder(soup=soup)

    def time_req(self):
        # estimate the time this will take
        import math
        time_sec = self.document_count/4.33
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
        # return f"This will scrape up to {self.document_count} documents and take roughly \n{time_hour}{time_min}{time_sec}"
        return f"This will scrape up to {self.document_count} documents and take roughly \n{time_hour}{time_min}{time_sec}"

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

            self.culture_dict[cultureName] = {"Region": region, "SubRegion": subRegion, "link": link, "Source_count": source_count, "Reloads": {"Source_reload": 0, "Doc_reload": 0}}
        # print(f"Number of cultures extracted {len(culture_dict)}")
    def doc_scraper(self):
        doc_count_total = 0

        # create dataframe to hold all the data
        df_eHRAF = pd.DataFrame({"Region":[], "SubRegion":[], "Culture":[], 'DocTitle':[], 'Year':[], "OCM":[], "OWC":[], "Passage":[]})



        # For each Culture, go to their webpage link then scrape the document data
        for key in self.culture_dict.keys():
            self.driver.get(self.homeURL + self.culture_dict[key]['link'])
            doc_count = 0

            # dataframe for each culture
            df_eHRAFCulture = pd.DataFrame({"Region":[], "SubRegion":[], "Culture":[], 'DocTitle':[], 'Year':[], "OCM":[], "OWC":[], "Passage":[]})

            # loop until every page containing a source tab is clicked
            source_total = self.culture_dict[key]['Source_count']
            while source_total > 0:
                # Try to make the program wait until the wepage is loaded
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "mdc-data-table__row")))
                #Click every source tab
                sourceTabs = self.driver.find_elements_by_class_name('mdc-data-table__row')
                for source_i in sourceTabs:
                    self.driver.execute_script("arguments[0].click();", source_i)

                #Log the source table's results number in order to know where to start and stop clicking.
                # Skip every 2 logs as they do not contain the information desired
                soup = BeautifulSoup(self.driver.page_source, features="html.parser")
                sourceCount = soup.find_all('td',{'class':'mdc-data-table__cell mdc-data-table__cell--numeric'})
                sourceCount_list = list(map(lambda x: int(x.text), sourceCount[0::3]))



                # WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "trad-data__results")))

                # wait to make sure the page is loaded. CHANGE to a higher time if it runs indefinately
                time.sleep(.1)

                #get the results tab(which is basically the source tab but contained within a different HTML element) for sub indexing sources
                resultsTabs = self.driver.find_elements_by_class_name('trad-data__results')
                # if the resultsTabs did not all load, reload as necessary
                reload_protect = 0
                while len(sourceCount_list) != len(resultsTabs) and reload_protect<=10:
                    time.sleep(.1)
                    resultsTabs = self.driver.find_elements_by_class_name('trad-data__results')
                    reload_protect += 1
                if reload_protect != 0:
                    self.culture_dict[key]["Reloads"]["Source_reload"] += reload_protect


                resultsTabs_count = len(resultsTabs) #For later reload checking

                # click and extract information from each document within the result/source tabs
                for i in range(len(resultsTabs)):
                    total = sourceCount_list[i]

                    # loop until the program can click and find every piece of information for each document (this is probably where things will break if times are off)
                    while True:
                        docTabs = resultsTabs[i].find_elements_by_class_name('sre-result__title')
                        #Click all the tabs within a source
                        for doc in docTabs:
                            self.driver.execute_script("arguments[0].click();", doc)
                            doc_count +=1


                        soup = BeautifulSoup(self.driver.page_source, features="html.parser")
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
                        # NOTE that we have to search for the resultsTabs again because the page refreshed and the points
                        # originally found above no longer point to the same location and therefore will not work
                        if total >0:
                            SourceTabFooter = resultsTabs[i].find_elements_by_class_name('trad-data__results--pagination')
                            buttons = SourceTabFooter[0].find_elements_by_class_name('rmwc-icon--ligature')
                            self.driver.execute_script("arguments[0].click();", buttons[-1])
                            time.sleep(.1)
                            resultsTabs = self.driver.find_elements_by_class_name('trad-data__results')
                            # in case .1 was not enough time, redo until the entire page is loaded again.
                            reload_protect = 0
                            while len(resultsTabs) < resultsTabs_count and reload_protect<=10:
                                time.sleep(.1)
                                resultsTabs = self.driver.find_elements_by_class_name('trad-data__results')
                                reload_protect += 1
                            # else:
                            #     raise Exception("failed to load all results tabs, please contact ericchantland@gmail.com for info on fixing the time waits")
                            if reload_protect != 0:
                                if reload_protect > 10:
                                    raise Exception("failed to load all results tabs, please contact ericchantland@gmail.com for info on fixing the time waits")
                                else:
                                    self.culture_dict[key]["Reloads"]["Doc_reload"] += reload_protect

                        else:
                            ## close sourcetab(this might save time in the long run)
                            ## NOTE: commented out because it will not work anymore with multi sources (sources with more than 10 passages).
                            ## If you want it to close the tabs, you could copy the above resultsTabs reload and put it right after this line of code then chnage docTabs = resultsTabs[i] above to docTabs = resultsTabs[0]
                            # driver.execute_script("arguments[0].click();", sourceTabs[i])
                            break
                # Run to the next page if necessary. Check to see if there are more source tabs left, if so, click the next page and continue scraping the page
                source_total -= len(resultsTabs)
                if source_total >0:
                    next_page = self.driver.find_element_by_xpath("//button[@title='Next Page']")
                    self.driver.execute_script("arguments[0].click();", next_page)



            df_eHRAFCulture[['Region','SubRegion',"Culture"]] = [self.culture_dict[key]['Region'], self.culture_dict[key]['SubRegion'], key ]
            df_eHRAF = pd.concat([df_eHRAF, df_eHRAFCulture], ignore_index=True)
            doc_count_total += doc_count
            if doc_count < sum(sourceCount_list):
                print(f"WARNING {doc_count} out of {sum(sourceCount_list)} documents loaded for {key}")

        self.save_file(df_eHRAF)
        self.web_close()
        print(f'{doc_count_total} documents out of a possible {self.document_count} loaded (also check dataframe)')


    def save_file(self, df):
        # get time and date that this program was run
        from datetime import datetime
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%m/%d/%y")

        # clean and strip the URL to be put into the excel document
        replace_dict = {'%28':'(', '%29':')', '%3A':'~', '%7C':'|', '%3B':';'}
        remove_list = [self.homeURL, 'search', '\?q=', 'fq=', '&', 'culture_level_samples']

        URL_name = self.URL

        for i in remove_list:
            URL_name = re.sub(i, '', URL_name)
        for key, val in replace_dict.items():
            URL_name = re.sub(key, val, URL_name)

        URL_name_nonPlussed = re.sub('\+', ' ', URL_name)
        df_eHRAF = df
        # place run information within the "run_info" column
        df_eHRAF['run_Info'] = None
        df_eHRAF.loc[0, 'run_Info'] = "User: " + self.user
        df_eHRAF.loc[1, 'run_Info'] = "Run Time: " + str(current_time)
        df_eHRAF.loc[2, 'run_Info'] = "Run Date: " + str(current_date)
        df_eHRAF.loc[3, 'run_Info'] = "Run Input: " + URL_name_nonPlussed
        df_eHRAF.loc[4, 'run_Info'] = "Run URL: " + self.URL


        try:
            df_eHRAF.to_excel('Data/' + URL_name + '_web_data.xlsx', index=False)
        except:
            print("Unable to save the title of the document, please rename it or risk overwriting")
            df_eHRAF.to_excel('Data/' + self.user + str(now.strftime("%m_%d_%y")) + '_web_data.xlsx', index=False)

    def web_close(self):
        # close the webpage
        self.driver.close()

    # if the class gets overwrittten,  remove the webpage
    def __del__(self):
        self.driver.close()

