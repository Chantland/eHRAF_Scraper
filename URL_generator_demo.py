
import URL_generator as ug

from importlib import reload
ug = reload(ug)
from URL_generator import URL_generator as ug

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
cultures = ["Mao, AzAnde", "Mao", "fake,cult, Rhade, GaRo", "", "Azande", "", "", "douas"]
cult_conj =  [1,0,1,1,0,1,0,1]
subjects = ["spirits and gods, joiks, 750, 9999, PoppYnESS", "729", "", "750, 750, 729", "idj", "729", "", "ksduf"]
subjects_conj = [1,0,2,2,1,0,2,1]
concat_conj = [1,0,1,2,1,2,1,2]
keywords = ["apple, pear", "", "apple", "apple, pear", "", "", "apple, pear", ""]
keywords_conj = [1,2,0,2,1,2,1,0]
cultural_level_samples = ['EA', 'SRS']



# 0 None
# 1 any
# 2 all

for i in range(8):
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