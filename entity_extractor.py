import pandas as pd
import numpy as np
from config import sideinfo as cfg
from config.entities import fields_ktp
from Levenshtein import distance as levenshtein_dist
from utils.postprocess import post_parse
from utils.clean_entity import get_birthdatepalce, get_rtrw
from utils.clean_entity import get_gender, get_occupation, get_maritalstatus
from utils.geometry import calDeg
import re 
import sys

def parse_response(text_response):
    """
    Given those returned text boxes, labels and points of the rounding box are extracted. 
    """
    ls_word = []
    if ('textAnnotations' in text_response):
        for text in text_response['textAnnotations']:
            boxes = {}
            boxes['label'] = text['description']
            boxes['x1'] = text['boundingPoly']['vertices'][0].get('x',0)
            boxes['y1'] = text['boundingPoly']['vertices'][0].get('y',0)
            boxes['x2'] = text['boundingPoly']['vertices'][1].get('x',0)
            boxes['y2'] = text['boundingPoly']['vertices'][1].get('y',0)
            boxes['x3'] = text['boundingPoly']['vertices'][2].get('x',0)
            boxes['y3'] = text['boundingPoly']['vertices'][2].get('y',0)
            boxes['x4'] = text['boundingPoly']['vertices'][3].get('x',0)
            boxes['y4'] = text['boundingPoly']['vertices'][3].get('y',0)
            boxes['w'] = boxes['x3'] - boxes['x1']
            boxes['h'] = boxes['y3'] - boxes['y1']
            ls_word.append(boxes)
    return ls_word

def get_attribute_ktp(ls_word, field_name, field_keywords, typo_tolerance, debug_mode=False):
    """
    Extract entities 
    """
    if(len(ls_word)==0):
        return None
    if(field_name == 'nama'):
        ls_word = np.asarray([word for word in ls_word if word['label'].lower() not in ['jawa','nusa'] ])

    new_ls_word = np.asarray([word['label'].lower() for word in ls_word])

    ls_dist = [levenshtein_dist(field_keywords, word.lower()) for word in new_ls_word]
    if np.min(ls_dist) > typo_tolerance:

        if(field_name == 'kota' and field_keywords!='kota'):
            a = get_attribute_ktp(ls_word,field_name,'kota',1, debug_mode)  #pronvice may have different types of names such as kota and etc
            return a
        return None
    index = np.argmin(ls_dist)
    #The Anchor Position
    if debug_mode:
        print("field name")
        print(ls_word[index])    
    x, y = ls_word[index]['x1'], ls_word[index]['y1']
    w = ls_word[index]['w']
    degree = calDeg(ls_word[index]['x1'],ls_word[index]['y1'],ls_word[index]['x2'],ls_word[index]['y2'])
    ls_y = np.asarray([np.abs(y-word['y1'])<300 for word in ls_word])
    value_words = [ww for ww, val in zip(ls_word,ls_y) if (val and np.abs(calDeg(x,y,ww['x1'],ww['y1'])-degree)<3)]
    if debug_mode:
        print("extracted entity value")
        print(value_words)
    field_value = post_parse(value_words, field_name, field_keywords)
    return field_value


def extract_ktp_data(text_response, debug_mode=False):

    df_ktp  = pd.DataFrame(columns=['fullname', 'identity_number', 'birth_place',
                                    'birth_date', 'city', 'rt_rw',
                                    'address', 'kel_desa', 'province', 
                                    'kecamatan',  'occupation', 'religion', 
                                    'blood_type', 'gender', 'marital_status', 
                                    'expired_date', 'nationality', 'state'])

    attributes = {}
    textboxes = parse_response(text_response)
    if(len(textboxes)==0):
        attributes['state'] = "rejected"
        df_ktp = df_ktp.append(attributes, ignore_index=True)
        return df_ktp

    raw_result = {}

    for field in fields_ktp:
        field_value = get_attribute_ktp(textboxes,
                                        field['field_name'],
                                        field['keywords'],
                                        field['typo_tolerance'],
                                        debug_mode)
        if(field_value != None):
            field_value = str(field_value).replace(': ', '').replace(':','')
        raw_result[field['field_name']] = field_value
    #fine-tune those results
    attributes['state'] = 'ok'
    attributes['identity_number'] = raw_result['nik']
    if(attributes['identity_number'] != None):
        attributes['identity_number'] = ''.join([i for i in raw_result['nik'] if i.isdigit()])
    if(attributes['identity_number'] == None):
        try:
            attributes['identity_number']  = re.findall(r"\D(\d{16})\D", textboxes[0]['label'])[0]
        except:
            attributes['state'] = "rejected"
            df_ktp = df_ktp.append(attributes,ignore_index=True)
            return df_ktp

    attributes['fullname'] = raw_result['nama']
    if(raw_result['nama'] != None):
        attributes['fullname'] = ''.join([i for i in raw_result['nama'] if not i.isdigit()]).replace('-','').strip()
    occ = raw_result['ttl'] 
    attributes['birth_date'], attributes['birth_place'] = get_birthdatepalce(occ)
    attributes['province'] = raw_result['provinsi']
    if raw_result['kota'] == None and raw_result['provinsi'] is not None:
        try: #maybe jakarta
            for row in textboxes[0]['label'].split('\n'):
                firstword = row.strip().split(' ')[0]
                if levenshtein_dist(firstword.lower(), "jakarta")<=2:
                    raw_result['kota'] = row
                    break
        except:
            raw_result['kota'] = None
    attributes['city'] = raw_result['kota']
    attributes['address'] = raw_result['alamat']
    attributes['rt_rw'] = get_rtrw(raw_result['rt_rw'])
    attributes['kel_desa'] = raw_result['kel_desa']
    attributes['kecamatan'] = raw_result['kecamatan']
    attributes['marital_status'] = get_maritalstatus(raw_result['status_perkawinan'])
    attributes['occupation'] = get_occupation(raw_result['pekerjaan'])
    attributes['religion'] = raw_result['agama']
    attributes['expired_date'] = raw_result['berlaku_hingga']
    attributes['nationality'] = raw_result['kewarganegaraan']
    if attributes['nationality'] is not None:
        if "WNI" in attributes['nationality']:
            attributes['nationality'] = 'INDONESIA'
        else:
            attributes['nationality'] = None
    if attributes['expired_date'] is not None:
        if "SEUMUR HIDUP" in attributes['expired_date']:
            attributes['expired_date'] = 'SEUMUR HIDUP'
        if(raw_result['jenis_kelamin'] == 'LAKI-LAKI'):
            attributes['gender'] = 'male'
        elif(raw_result['jenis_kelamin'] in ['WANITA','PEREMPUAN']):
            attributes['gender'] = 'female'
        else:
            attributes['gender'] = get_gender(textboxes)
    if(raw_result['gol_darah'] != None):
        attributes['blood_type'] = ''.join([i for i in raw_result['gol_darah'] if not i.isdigit()]).strip()
        if(attributes['blood_type'].lower() not in ['a','b','ab','o']):
            attributes['blood_type'] = None
    else:
        attributes['blood_type'] = None

    df_ktp = df_ktp.append(attributes,ignore_index=True)
    return df_ktp

def process_extract_entities(text_response):
        ktp_extract = extract_ktp_data(text_response)
        if ktp_extract.isnull().sum().sum()>=cfg.rejected_threshold:
            ktp_extract.at[0, 'state'] = 'rejected'
        return ktp_extract

if __name__ == '__main__':
    if(len(sys.argv) > 1):
        # input: ocr file path
        ocr_path = sys.argv[1]
        print('Extracting data from '+ocr_path)
        process_extract_entities(ocr_path)
    else:
        print('argument is missing: ocr output file path')
