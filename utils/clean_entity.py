import numpy as np
from Levenshtein import distance as levenshtein_dist
import re
from datetime import datetime

def get_birthdatepalce(occ):
    birth_date  = None
    birth_place = None
    if occ != None:
        ttls = occ.split(', ')
        if len(ttls)>=2:
            birth_place = ttls[0]
            birth_date = extract_date(ttls[1])

        elif len(ttls)==1:
            birth_place = ttls[0]

        if birth_date == None:
            birth_date = extract_date(occ)

    if birth_place != None:
        birth_place = ''.join([i for i in birth_place if not i.isdigit()]).replace('-','').replace('.','').strip()
    return birth_date, birth_place 

def get_rtrw(occ):
    """
    Extract RTRW Number
    """
    if occ==None:
        return None
    occ = occ.strip()
    result = occ
    numbers = re.findall(r'\d{2}[0-9]', occ)
    if len(numbers)>=2: 
        result = numbers[-2]+' / '+numbers[-1]
    elif len(numbers)==1:
        ref_number = numbers[0]
        idx_left  = occ.find(ref_number)
        idx_right = idx_left+3
        if idx_left==0 and idx_right<len(occ):
            # search right
            back_string = occ[idx_right:]
            numbers = re.findall(r'[1-9]{1,2}', back_string)
            if len(numbers) == 0:
                result=ref_number + ' / ' + '000'
            else:
                result = ref_number + ' / ' + numbers[-1].zfill(3)
        if idx_right>=len(occ) and idx_left>0:
            # search left
            back_string = occ[0:idx_left]
            numbers = re.findall(r'[1-9]{1,2}', back_string)
            if len(numbers) == 0:
                result='000' + ' / ' + ref_number
            else:
                result =numbers[-1].zfill(3) + ' / ' + ref_number
    return result

def get_gender(ls_word):
    new_ls_word = np.asarray([word['label'].lower() for word in ls_word])

    d = [levenshtein_dist('laki-laki', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 3):
            return 'male'

    d = [levenshtein_dist('wanita', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 2):
            return 'female'

    d = [levenshtein_dist('perempuan', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 2):
            return 'female'

    d = [levenshtein_dist('pria', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 1):
            return 'male'

    d = [levenshtein_dist('laki', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 1):
            return 'male'

    return None

def extract_date(date_string):
    if(date_string == None):
        return None

    date = None
    try:
        regex = re.compile(r'(\d{1,2}-\d{1,2}-\d{1,4})')
        tgl = re.findall(regex, date_string)
        if(len(tgl)>0):
            date = datetime.strptime(tgl[0], '%d-%m-%Y')
        else:
            tgl = ''.join([n for n in date_string if n.isdigit()])
            if(len(tgl)==8):
                date = datetime.strptime(tgl[0:2]+'-'+tgl[2:4]+'-'+tgl[4:], '%d-%m-%Y')
    except ValueError:
        return None

    if(date==None):
        return None

    if((date.year < 1910) or (date.year > 2100)):
        return None

    return date

def get_gender(ls_word):
    new_ls_word = np.asarray([word['label'].lower() for word in ls_word])

    d = [levenshtein_dist('laki-laki', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 3):
            return 'male'

    d = [levenshtein_dist('wanita', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 2):
            return 'female'

    d = [levenshtein_dist('perempuan', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 2):
            return 'female'

    d = [levenshtein_dist('pria', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 1):
            return 'male'

    d = [levenshtein_dist('laki', word.lower()) for word in new_ls_word]
    if(len(d)>0 and min(d) <= 1):
            return 'male'

    return None

def get_maritalstatus(occ):
    if occ==None:
        return None
    ref_text = occ.lower()
    if levenshtein_dist('belum kawin', ref_text)<= 2 or 'belum kawin' in ref_text:
        result = 'single'
    elif levenshtein_dist('tidak kawin', ref_text) <= 2 or 'tidak kawin' in ref_text:
        result = 'single'
    elif levenshtein_dist('kawin', ref_text) <= 1:
        result = 'married'
    elif levenshtein_dist('janda', ref_text) <= 2:
        result = 'widowed'
    elif levenshtein_dist('duda', ref_text)  <= 2:
        result = 'widowed'
    elif levenshtein_dist('cerai', ref_text)  <= 2:
        result = 'widowed'
    else:
        result = None
    return result 

def get_occupation(occ):
    if occ==None:
        return None
    result = occ[0:40].split(' ')[0]
    if(levenshtein_dist('mengurus rumah tangga',occ.lower()) <= 6):
            result = 'Mengurus Rumah Tangga'
    if(levenshtein_dist('buruh harian lepas',occ.lower()) <= 6):
            result = 'Buruh Harian Lepas'
    if(levenshtein_dist('pegawai negeri sipil',occ.lower()) <= 5):
            result = 'Pegawai Negeri Sipil'
    if(levenshtein_dist('pelajar/mahasiswa',occ.lower()) <= 4):
            result = 'Pelajar/Mahasiswa'
    if(levenshtein_dist('pelajar/mhs',occ.lower()) <= 3):
            result = 'Pelajar/Mahasiswa'
    if(levenshtein_dist('belum/tidak bekerja',occ.lower()) <= 5):
            result = 'Belum/Tidak Bekerja'
    if(levenshtein_dist('karyawan swasta',occ.lower()) <= 4):
            result = 'Karyawan Swasta'
    if(levenshtein_dist('pegawai negeri',occ.lower()) <= 4):
            result = 'Pegawai Negeri'
    if(levenshtein_dist('wiraswasta',occ[0:10].lower()) <= 3):
            result = 'Wiraswasta'
    if(levenshtein_dist('peg negeri',occ.lower()) <= 3):
            result = 'Pegawai Negeri'
    if(levenshtein_dist('peg swasta',occ.lower()) <= 3):
            result = 'Pegawai Swasta'

    return result
