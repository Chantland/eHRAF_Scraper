# URL generator
import re
import pandas as pd
import os
import sys

class URL_Generator:
    def __init__(self):
        self.Search_dict = {'culture': {'valid': set(), 'invalid': set(), 'phrase': ''},
                       'subject': {'valid': set(), 'invalid': set(), 'phrase': ''},
                       'keyword': {'valid': set(), 'invalid': set(), 'phrase': ''}, }
        self.final_phrase = ''
        # set up application path for files
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        elif __file__:
            self.application_path = os.path.dirname(__file__)
        else:
            raise Exception("Unable to find application path. Potentially neither script file nor frozen file")
    def word_strip(self, string:str):
        string_list = [x.lower().strip() for x in string.split(",")]
        for i, string in enumerate(string_list): #remove extra quotes
            string_list[i] = re.sub("\"|\'", '', string)
        string_list = [i for i in string_list if i !=''] #remove blanks
        return string_list
    def URL_generator(self, 
                    cultures:str = '', 
                    cult_conj:int = 1, 
                    subjects:str = '', 
                    subjects_conj:int = 1,
                    concat_conj:int = 1, 
                    keywords:str = '', 
                    keywords_conj:int = 1, 
                    cultural_level_samples:list = []):

        conj_list = ["  ", " OR ", " AND "]
        Search_dict = {'culture': {'valid':set(), 'invalid':set(), 'phrase':''},
                       'subject': {'valid':set(), 'invalid':set(), 'phrase':''},
                       'keyword': {'valid':set(), 'invalid':set(), 'phrase':''},}
        # create search phrase chunks which will be later combined and used for the URL
        if cultures != '':
            culture_list = self.word_strip(cultures)
            # Match cultures with the cultures that eHRAF uses
            df_Culture = pd.read_excel(self.application_path + '/Resources/Culture_Names.xlsx')
            for culture in culture_list:
                if culture in df_Culture['Culture'].unique():
                    found_culture = df_Culture[df_Culture['Culture'].isin([culture])]
                    Search_dict['culture']['valid'].add(found_culture['Culture'].values[0]) #could be one line but split to reduce confusion
                else:
                    Search_dict['culture']['invalid'].add(str(culture))
            Search_dict['culture']['valid'] = sorted(Search_dict['culture']['valid']) #sort the inputs/values
            # create phrase for culture (will be combined with the rest and then turned in a URL
            if len(Search_dict['culture']['valid']) > 0:
                Search_dict['culture']['phrase'] += 'cultures:('
                multi_term = False
                for search_i in Search_dict['culture']['valid']:
                    # Add a conjunction if there are more than 1 search terms
                    if multi_term is True:
                        Search_dict['culture']['phrase'] += conj_list[cult_conj]
                    else:
                        multi_term = True
                    # if NONE is selected for cultures, add a -
                    if cult_conj == 0:
                        Search_dict['culture']['phrase'] += '-'
                    Search_dict['culture']['phrase'] += '\"' + search_i + '\"'
                Search_dict['culture']['phrase'] += ')'


        if subjects != '':
            subjects_list = self.word_strip(subjects)
            # Match OCM codes with meanings and return back a list of ones that worked and ones that didn't
            df_OCM_Codes = pd.read_excel(self.application_path + '/Resources/OCM_Codes.xlsx')
            for subject in subjects_list:
                # turn OCMs into meanings, or search for if the meanings exist
                if subject.isnumeric():
                    col = 'OCM'
                    sub = int(subject)
                else:
                    col = 'Meaning'
                    sub = subject
                if sub in df_OCM_Codes[col].unique():
                    meaning = df_OCM_Codes[df_OCM_Codes[col].isin([sub])]
                    Search_dict['subject']['valid'].add(meaning['Meaning'].values[0]) #could be one line but split to reduce confusion
                else:
                    Search_dict['subject']['invalid'].add(str(sub))
            Search_dict['subject']['valid'] = sorted(Search_dict['subject']['valid']) #sort the inputs/values
            if len(Search_dict['subject']['valid']) > 0:
                Search_dict['subject']['phrase'] += 'subjects:('
                multi_term = False
                for search_i in Search_dict['subject']['valid']:
                    # Add a conjunction if there are more than 1 search terms
                    if multi_term is True:
                        Search_dict['subject']['phrase'] += conj_list[subjects_conj]
                    else:
                        multi_term = True
                    # if NONE is selected for subject, add a -
                    if subjects_conj == 0:
                        Search_dict['subject']['phrase'] += '-'
                    Search_dict['subject']['phrase'] += '\"' + search_i + '\"'
                Search_dict['subject']['phrase'] += ')'

        if keywords != '':
            keyword_list = self.word_strip(keywords)
            Search_dict['keyword']['valid'] = set(keyword_list)
            Search_dict['keyword']['valid'] = sorted(Search_dict['keyword']['valid']) #sort the inputs/values
            #At this point, I am not sure what would be an invalid keword.
            if len(Search_dict['keyword']['valid']) > 0:
                Search_dict['keyword']['phrase'] += 'text:('
                multi_term = False
                for search_i in Search_dict['keyword']['valid']:
                    # Add a conjunction if there are more than 1 search terms
                    if multi_term is True:
                        Search_dict['keyword']['phrase'] += conj_list[keywords_conj]
                    else:
                        multi_term = True
                    # if NONE is selected for subject, add a -
                    if keywords_conj == 0:
                        Search_dict['keyword']['phrase'] += '-'
                    Search_dict['keyword']['phrase'] += search_i
                Search_dict['keyword']['phrase'] += ')'



        if Search_dict['culture']['phrase'] == '' and Search_dict['subject']['phrase'] == '' and Search_dict['keyword']['phrase'] == '':
            return ''

        # Construct the passage
        final_phrase = ''
        # combine subject and keywords together by using a conjunction specified. Otherwise get one or the other (or neither)
        if Search_dict['subject']['phrase'] != '' and Search_dict['keyword']['phrase'] != '':
            final_phrase += '(' + Search_dict['subject']['phrase'] + conj_list[concat_conj] + Search_dict['keyword']['phrase'] + ')'
        else: # else combine the blank subject/keyword with the real text (if it is also not blank)
            final_phrase += Search_dict['subject']['phrase'] + Search_dict['keyword']['phrase']
        if Search_dict['culture']['phrase'] != '':
            # if either are subject or keword are present, add a conjunction and combine
            if Search_dict['subject']['phrase'] != '' or Search_dict['keyword']['phrase'] != '':
                final_phrase = Search_dict['culture']['phrase'] + conj_list[2] + final_phrase
            else:
                final_phrase = Search_dict['culture']['phrase']



        # construct URL from phrase
        URL= r'https://ehrafworldcultures.yale.edu/search?q='
        URL_final_phrase = final_phrase
        replace_dict = {'\(':'%28', '\)':'%29', '\:':'%3A', '\|':'%7C', '\;':'%3B', ' ':'+', '\"':'%22'}


        for key, val in replace_dict.items():
            URL_final_phrase = re.sub(key, val, URL_final_phrase)
        URL += URL_final_phrase

        #Add in optional filters like cultural level camples
        # &fq=culture_level_samples%7CEA%3Bculture_level_samples%7CPSF%3Bculture_level_samples%7CSCCS%3Bculture_level_samples%7CSRS.

        # cultureSamplesText_list = ['EA', 'SCCS', 'PSF', 'SRS']
        # filteredCST_list = [i for (i, v) in zip(cultureSamplesText_list, cultural_level_samples) if v]
        if len(cultural_level_samples) > 0:
            URL += '&fq='
            semiColon = False #determine if a semicolon is needed between items
            for CST in cultural_level_samples:
                if semiColon is False:
                    semiColon = True
                else:
                    URL += '%3B'
                URL += 'culture_level_samples%7C' + CST


        # Allow phrase and dictionary to be accessed through the class
        self.final_phrase = final_phrase
        self.Search_dict = Search_dict
        return URL

    # if there are any invalid inputs, create a paragraph which displays every invalid one
    def invalid_inputs(self):
        if len(self.Search_dict['culture']['invalid']) + \
                len(self.Search_dict['subject']['invalid']) + \
                len(self.Search_dict['keyword']['invalid']) <1:
            return "All inputs are valid"
        # create a single paragraph with invalid culture, subject and keyword as necessary
        invalidParagraph = 'The following inputs could not be searched:\n'
        if len(self.Search_dict['culture']['invalid']) >= 1:
            invalidParagraph += "Culture: "
            comma_flip = False
            for var in self.Search_dict['culture']['invalid']:
                if comma_flip is False:
                    comma_flip = True
                else:
                    invalidParagraph += ', '
                invalidParagraph += var
            invalidParagraph += '\n'
        if len(self.Search_dict['subject']['invalid']) >= 1:
            invalidParagraph += "Subject: "
            comma_flip = False
            for var in self.Search_dict['subject']['invalid']:
                if comma_flip is False:
                    comma_flip = True
                else:
                    invalidParagraph += ', '
                invalidParagraph += var
            invalidParagraph += '\n'
        if len(self.Search_dict['keyword']['invalid']) >= 1:
            invalidParagraph += "Keyword: "
            comma_flip = False
            for var in self.Search_dict['keyword']['invalid']:
                if comma_flip is False:
                    comma_flip = True
                else:
                    invalidParagraph += ', '
                invalidParagraph += var
            invalidParagraph += '\n'
        return invalidParagraph

