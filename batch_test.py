import sys
from config import sideinfo as cfg
import ocr_extractor as ocr
import entity_extractor as extractor
import cv2
import json
import os
import pandas as pd
import time

def merge_process(bytes):
    ocr_text = ocr.bytes_to_text(bytes)
    df_result = extractor.process_extract_entities(ocr_text)
    return df_result, ocr_text

def rotate_image(frame, angle, scale=1.0):
    (h, w) = frame.shape[:2]
    center = (w / 2, h / 2) 
    M = cv2.getRotationMatrix2D(center, angle, scale)
    newframe = cv2.warpAffine(frame, M, (h, w))
    return newframe

def test_flow(img_path):
    img_name = img_path.split('/')[-1].split('.')[0]
    img_type = img_path.split('/')[-1].split('.')[1]
    bytes, frame = ocr.load_img(img_path)
    df_result, ocr_text = merge_process(bytes)    
    if df_result.iloc[0].state != 'ok':
        for angle in [180, 90, 270]:
            print('rotate image {}'.format(angle))
            rotated_frame = rotate_image(frame, angle)
            success, encoded_image = cv2.imencode('.'+img_type, rotated_frame)
            content_bytes = encoded_image.tobytes()
            df_result, ocr_text = merge_process(content_bytes)
            if df_result.iloc[0].state == 'ok':
                break
    df_result.at[0, 'samplename'] = img_name
    return df_result  

if __name__ == '__main__':
    dflist = []
    filenames = os.listdir("imgs")
    for idx, filename in enumerate(filenames):
        path = os.path.join("imgs", filename)
        df = test_flow(path)
        print(path)
        print(idx)
        dflist.append(df)
        if (idx+1) % 50 == 0:
            dffinal = pd.concat(dflist)
            dffinal.to_csv("{}samplesresult.csv".format(idx)) 
            time.sleep(10)        

    
    
    