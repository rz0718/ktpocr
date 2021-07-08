import numpy as np
from Levenshtein import distance as levenshtein_dist
import re


def filter_word(value_words, ref_words=['gol.', 'darah']):
    value_words = [val for val in value_words if len(val['label'].replace(' ','').replace(':',''))>0]
    clean_value_words = []
    for val in value_words:
        check_word = str(val['label']).lower()
        remove_status = False
        for ref_word in ref_words:
            if levenshtein_dist(ref_word, check_word)<=1:
                remove_status = True
                break
        if not remove_status:
            clean_value_words.append(val)
    return clean_value_words


def post_parse(value_words, field_name, field_keywords):
    """
    Case by Case Analysis
    """
    value_words = filter_word(value_words)
    if field_name == 'kota':
        field_value = ""
        for val in value_words:
            field_value = field_value + ' '+ str(val['label'])
        field_value = field_value.lstrip()

        if(field_keywords == 'kabupaten'):
            return 'KABUPATEN '+field_value
        else:
            return 'KOTA '+field_value

    if field_name == 'ttl':
            d = [levenshtein_dist('lahir', str(val['label']).lower()) for val in value_words]
            if(len(d)>0 and min(d) <= 2):
                idx = np.argmin(d)
                value_words.pop(idx)

    field_value = ""
    for val in value_words:
        field_value = field_value + ' '+ str(val['label'])
    field_value = field_value.lstrip()
    if field_value == "":
        return None
    return field_value
