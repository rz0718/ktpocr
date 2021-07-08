import sys
from config import sideinfo as cfg
import ocr_extractor as ocr
import entity_extractor as extractor
import cv2
import json

def merge_process(bytes):
    """
    Input: Bytes for images
    Output: Extracted entity in DF, the raw extracted ocr text
    """
    ocr_text = ocr.bytes_to_text(bytes)
    df_result = extractor.process_extract_entities(ocr_text)
    return df_result, ocr_text

def rotate_image(frame, angle, scale=1.0):
    """
    Inputs: Image numpy matrix,  angle is the degree to rotate
    Output: the rotated image
    """
    (h, w) = frame.shape[:2]
    center = (w / 2, h / 2) 
    M = cv2.getRotationMatrix2D(center, angle, scale)
    newframe = cv2.warpAffine(frame, M, (h, w))
    return newframe


if __name__ == '__main__':
    if(len(sys.argv) > 1):
        # input: image path
        img_path = sys.argv[1]
        print('OCR processing '+img_path)
        img_name = img_path.split('/')[-1].split('.')[0]
        img_type = img_path.split('/')[-1].split('.')[1]
        output_name  = cfg.output_loc+'result_'+img_name+'.csv'
        ocrtxt_name  = cfg.json_loc+img_name+'.txt'
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
        print(df_result.iloc[0])
        df_result.to_csv(output_name,index=False)
        with open(ocrtxt_name, 'w') as outfile:
            json.dump(ocr_text, outfile)
                        
    else:
        print('argument is missing: image path')
        
    