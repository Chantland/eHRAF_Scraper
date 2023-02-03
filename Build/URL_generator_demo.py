
import URL_Generator as ug

from importlib import reload
ug = reload(ug)
from URL_Generator import URL_Generator as ug

# all 3
# cult and Subj
# cult and key
# subj and key
# cult
# subj
# key
# none

# preset all 3 used
# URL = URL_generator(cultures, cult_conj, subjects, subjects_conj,concat_conj, keywords, keywords_conj)
# cultures = ["Mao, AzAnde", "Mao", "fake,cult, Rhade, GaRo", "", "Azande", "", "", "douas"]
# cult_conj =  [1,0,1,1,0,1,0,1]
# subjects = ["spirits and gods, joiks, 750, 9999, PoppYnESS", "729", "", "750, 750, 729", "idj", "729", "", "ksduf"]
# subjects_conj = [1,0,2,2,1,0,2,1]
# concat_conj = [1,0,1,2,1,2,1,2]
# keywords = ["apple, grandma, pear", "", "apple", "pear, apple, grandma", "", "", "apple, pear", ""]
# keywords_conj = [1,2,0,2,1,2,1,0]
# cultural_level_samples = ['EA', 'SRS']


cultures = ["Mao, AzAnde, tiko, ti, Tikopia", "AzAnde, Mao, Tikopia", "AzAnde, shee, Tikopia, Mao", "Tikopia, Mao, mao, Azande", "Tikopia, AzAnde, Mao", "Mao, Tikopia, AzAnde", "Mao"]
cult_conj =  [1,1,1,1,1,1,1]
subjects = ["spirits and gods, bop, joiks, 750, 9999, 640", "750, 9999, spirits and gods, joiks, 640", "750, 9999, joiks, 640, spirits and gods", "640, 750, 9999, joiks,schenee, go,  spirits and gods", "640,  spirits and gods, 750, 9999, joiks", "spirits and gods, 640, 9999, joiks, 750", "750"]
subjects_conj = [1,1,1,1,1,1,1]
concat_conj = [1,1,1,1,1,1,1]
keywords = ["apple, grandma, pear", "apple, pear, grandma", "pear, grandma, apple", "pear, apple, grandma","Grandma, apple, PEaR", "Grandma, Pear, apple", "apple, pear"]
keywords_conj = [1,1,1,1,1,1,1]
cultural_level_samples = []


# subjects = ["spirits and gods, joiks, 750, 9999, 640", "750, 9999, spirits and gods, joiks, 640", "750, 9999, joiks, 640, spirits and gods", "640, 750, 9999, joiks, spirits and gods", "640,  spirits and gods, 750, 9999, joiks", "spirits and gods, 640, 9999, joiks, 750", "750"]
# subjects_conj = [1,1,1,1,1,1,1]
# concat_conj = [1,1,1,1,1,1,1]
# keywords = ["apple, grandma, pear", "apple, pear, grandma", "pear, grandma, apple", "pear, apple, grandma","Grandma, apple, PEaR", "Grandma, Pear, apple", "apple, pear"]
# keywords_conj = [1,1,1,1,1,1,1]
# cultural_level_samples = []



# 0 None
# 1 any
# 2 all
final_phrase_check = []
for i in range(len(cultures)):
    URL_gen = ug()
    URL = URL_gen.URL_generator(cultures=cultures[i],
                           cult_conj=cult_conj[i],
                           subjects=subjects[i],
                           subjects_conj=subjects_conj[i],
                           concat_conj= concat_conj[i],
                           keywords= keywords[i],
                           keywords_conj= keywords_conj[i],
                           cultural_level_samples= cultural_level_samples)
    final_phrase = URL_gen.final_phrase
    invalid = URL_gen.invalid_inputs()
    # invalid_search =
    print(i, final_phrase, '\n', URL, '\n', invalid, '\n\n\n')
    final_phrase_check.append(final_phrase)
for i in final_phrase_check:
    print(i)
print(all(y == final_phrase_check[0] for y in final_phrase_check[0:-1]))