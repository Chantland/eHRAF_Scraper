# URL generator
import re
import pandas as pd
import os
import sys
from unidecode import unidecode

class URL_Generator:
    def __init__(self):
        self.Search_dict = {'culture': {'valid': set(), 'invalid': set(), 'phrase': ''},
                        'subject': {'valid': set(), 'invalid': set(), 'phrase': ''},
                        'keyword': {'valid': set(), 'invalid': set(), 'phrase': ''}, 
                        'exClause_subject': {'valid': set(), 'invalid': set(), 'phrase': ''},
                        'exClause_keyword': {'valid': set(), 'invalid': set(), 'phrase': ''}, }
        self.final_phrase = ''
        # # set up application path for files
        # if getattr(sys, 'frozen', False):
        #     self.application_path = os.path.dirname(sys.executable)
        # elif __file__:
        #     self.application_path = os.path.dirname(__file__)
        # else:
        #     raise Exception("Unable to find application path. Potentially neither script file nor frozen file")
    
    def word_strip(self, query:str): # extract the comma sepaarted queries and clean
        query_list = [x.lower().strip() for x in query.split(",")] #split the text at commas and make the text lower case then erase blank spaces at the end and beginning
        for i, query in enumerate(query_list): #remove extra quotes
            query_list[i] = re.sub("\"|\'", '', query)
        query_list = [i.strip() for i in query_list if i !=''] #remove blanks and strip again in case the "" did not encompass everything
        return query_list
    def culture_valid_extractor(self, query_list:list):
            df = pd.read_excel(resource_path("Resources/Culture_Names.xlsx"))
            for culture in query_list:
                # add valid found Cultures from the dataframe, otherwise add to invalid dictionary. 
                if culture in df['Culture'].unique():
                    found_culture = df[df['Culture'].isin([culture])]
                    self.Search_dict['culture']['valid'].add(found_culture['Culture'].values[0]) #could be one line but split to reduce confusion
                else:
                    self.Search_dict['culture']['invalid'].add(str(culture))
            self.Search_dict['culture']['valid'] = sorted(self.Search_dict['culture']['valid']) #sort the inputs/values
    def OCM_valid_extractor(self, name:str, query_list:list):
            # Match OCM codes with meanings and return back a list of ones that worked and ones that didn't
            df = pd.read_excel(resource_path("Resources/OCM_Codes.xlsx"))
            for subject in query_list:
                # turn OCMs into meanings, or search for if the meanings exist
                if subject.isnumeric():
                    col = 'OCM'
                    sub = int(subject)
                else:
                    col = 'Meaning'
                    sub = subject
                if sub in df[col].unique():
                    meaning = df[df[col].isin([sub])]
                    self.Search_dict[name]['valid'].add(meaning['Meaning'].values[0]) #could be one line but split to reduce confusion
                else:
                    self.Search_dict[name]['invalid'].add(str(sub))
            self.Search_dict[name]['valid'] = sorted(self.Search_dict[name]['valid']) #sort the inputs/values
    def phrase_creator(self, name:str, conj:int, search_param:str, quotes:bool=True): 
        conj_list = [" ", " OR ", " AND "]
        # create phrase for query (will be combined with the rest and then turned in a URL
        if len(self.Search_dict[name]['valid']) > 0:
            self.Search_dict[name]['phrase'] += search_param+':(' #TODO: fix this name as it does not create the query correctly.
            multi_term = False
            for search_i in self.Search_dict[name]['valid']:
                # Add a conjunction if there are more than 1 search terms
                if multi_term is True:
                    self.Search_dict[name]['phrase'] += conj_list[conj]
                else:
                    multi_term = True
                # if NONE is selected for cultures, add a -
                if conj == 0:
                    self.Search_dict[name]['phrase'] += ' -'
                # if quotes are desired around the query, use them, otherwise don't (keywords do not use quotes)
                if quotes:
                    self.Search_dict[name]['phrase'] += '\"' + search_i + '\"'
                else:
                    self.Search_dict[name]['phrase'] += search_i
            self.Search_dict[name]['phrase'] += ')'
    def URL_generator(self, 
                    cultures:str = '', # Culture query
                    cult_conj:int = 1, # Culture conjunction between queries  
                    subjects:str = '',  # Subject query
                    subjects_conj:int = 1,  # Subject conjunction between queries  
                    concat_conj:int = 1, # Conjunction between primary clause subject and culture
                    keywords:str = '',  # Keyword query
                    keywords_conj:int = 1, # Keyword conjunction between queries  
                    exClause_conj:int = 1, # Extra Clause Conjunction between primary clause and extra clause
                    exClause_subjects:str = '', # Extra Clause Subject query
                    exClause_subjects_conj:int = 1, # Extra Clause Subject conjunction between queries  
                    exClause_concat_conj:int = 1,  # Conjunction between extra clause subject and culture
                    exClause_keywords:str = '', # Extra Clause Keyword query
                    exClause_keywords_conj:int = 1, # Extra Clause Keyword conjunction between queries 
                    filters:dict = {}): # filter dictionary for adding those sweet filters



        
        # create search phrase chunks which will be later combined and used for the URL
        if cultures != '':
            unidecode(cultures) #remove accented characters
            culture_list = self.word_strip(cultures)
            # Match cultures with the cultures that eHRAF uses
            self.culture_valid_extractor(culture_list)
            # create the actual phrase
            self.phrase_creator('culture', cult_conj, "cultures")

        if subjects != '':
            OCM_list = self.word_strip(subjects)
            # Match OCMs with the OCM's that eHRAF uses
            self.OCM_valid_extractor(name="subject", query_list=OCM_list)
            # create the actual phrase
            self.phrase_creator('subject', subjects_conj, "subjects" )

        if keywords != '':
            keyword_list = self.word_strip(keywords)
            self.Search_dict['keyword']['valid'] = set(keyword_list)
            self.phrase_creator('keyword', keywords_conj, "text", False)

        # EXTRA CLAUSE: for optional addition to 
        if exClause_subjects != '':
            OCM_list = self.word_strip(exClause_subjects)
            # Match OCMs with the OCM's that eHRAF uses
            self.OCM_valid_extractor(name='exClause_subject', query_list=OCM_list)
            # create the actual phrase
            self.phrase_creator('exClause_subject', exClause_subjects_conj, "subjects")

        if exClause_keywords != '':
            keyword_list = self.word_strip(exClause_keywords)
            self.Search_dict['exClause_keyword']['valid'] = set(keyword_list)
            self.phrase_creator('exClause_keyword', exClause_keywords_conj, "text", False)

        # if there are no valid inputs, return a blank text
        for val in self.Search_dict.values():
            if val['phrase'] == '':
                continue
            else:
                break
        else:
            return ''




        #### Construct the passage ####
        
        conj_list = [" ", " OR ", " AND "] # eHRAF currently uses double quotes for "not" queries
        finalPhrase = ''
        # combine subject and keywords together by using a conjunction specified. Otherwise get one or the other (or neither)
        if self.Search_dict['subject']['phrase'] != '' and self.Search_dict['keyword']['phrase'] != '':
            finalPhrase = '(' + self.Search_dict['subject']['phrase'] + conj_list[concat_conj] + self.Search_dict['keyword']['phrase'] + ')'
        else: # else combine the blank subject/keyword with the real text (if it is also not blank)
            finalPhrase = self.Search_dict['subject']['phrase'] + self.Search_dict['keyword']['phrase']

        # if either search queries in the extra clause exists, append it the first subject/keyword clause (unless it doesn't exist)
        if self.Search_dict['exClause_subject']['phrase'] != '' or self.Search_dict['exClause_keyword']['phrase'] != '':
            extraClause_phrase = ''
            if self.Search_dict['exClause_subject']['phrase'] != '' and self.Search_dict['exClause_keyword']['phrase'] != '':
                extraClause_phrase = '(' + self.Search_dict['exClause_subject']['phrase'] + conj_list[exClause_concat_conj] + self.Search_dict['exClause_keyword']['phrase'] + ')'
            else:
                extraClause_phrase = self.Search_dict['exClause_subject']['phrase'] + self.Search_dict['exClause_keyword']['phrase']
            #add extra clause to the potential primary clause if it exists
            if finalPhrase != '':
                if exClause_conj == 0: #this is the only NOT that does not us " -" but instead uses the actual word
                    finalPhrase = '(' + finalPhrase + " NOT " + extraClause_phrase + ')'
                else:
                    finalPhrase = '(' + finalPhrase + conj_list[exClause_conj] + extraClause_phrase + ')'
            else:
                finalPhrase = extraClause_phrase

        # culture
        if self.Search_dict['culture']['phrase'] != '':
            # if either clause for subject and/or keyword are present, add a conjunction and combine
            if finalPhrase != '':
                finalPhrase = self.Search_dict['culture']['phrase'] + conj_list[2] + finalPhrase
            else:
                finalPhrase = self.Search_dict['culture']['phrase']

        # # ADD FILTERS
        # sort the filter dictionary (potentially not necessary but I want to avoid similar filter queries being scrampled so they look different to the partial-file-saver in eHRAF_Scraper.py)
        filters = dict(sorted(filters.items()))
        # Add each filter
        filter_str = ''
        if sum(len(val) for val in filters.values()) > 0: #check if there are actually any filters at all
            filter_str += '&fq='
            semiColon = False #determine if a semicolon is needed between items (only used the first time)
            for filterType, filterVals in filters.items(): #take the filter type (culture_level_samples)
                # run through the list of filter values and append to URL
                for val in filterVals:
                    if semiColon is False:
                        semiColon = True
                    else:
                        filter_str += '%3B'
                    filter_str += f'{filterType}%7C{val}'
        
        # construct URL and give it initialized http address
        URL = r'https://ehrafworldcultures.yale.edu/search?q='

        # replace characters with their URL counterparts then add phrase and filter to  URL
        URL_PhraseFilter = finalPhrase + filter_str
        replace_dict = {'\(':'%28', '\)':'%29', '\:':'%3A', '\|':'%7C', '\;':'%3B', ' ':'+', '\"':'%22'}
        for key, val in replace_dict.items():
            URL_PhraseFilter = re.sub(key, val, URL_PhraseFilter)
        URL += URL_PhraseFilter

        # Allow phrase and dictionary to be accessed through the class
        self.final_phrase = finalPhrase
        self.Search_dict = self.Search_dict
        return URL

    # if there are any invalid inputs, create a paragraph which displays every invalid one
    def invalid_inputs(self):
        # If there are no invalid values, return, otherwise continue and catalog the values
        for val in self.Search_dict.values():
            if len(val['invalid']) < 1:
                continue
            else:
                break
        else:
            return "All inputs are valid"

        # create a single paragraph with invalid culture, subject and keyword as necessary
        invalidParagraph = 'The following inputs could not be searched:\n'
        invalidQuery_list = ["Culture: ", "Subject: ", "Keyword: ", "Extra Clause Subject: ", "Extra Clause Keyword"]
        for index, val in enumerate(self.Search_dict.values()):
            if len(val['invalid']) >= 1:
                invalidParagraph += invalidQuery_list[index]
                comma_flip = False
                for word in val['invalid']:
                    if comma_flip is False:
                        comma_flip = True
                    else:
                        invalidParagraph += ', '
                    invalidParagraph += word
                invalidParagraph += '\n'
        return invalidParagraph

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)