from google.cloud import vision
from google.protobuf.json_format import MessageToDict
import sys
from config import sideinfo as cfg
import cv2
client = vision.ImageAnnotatorClient.from_service_account_file(cfg.gcv_api_key_path)

def load_img(path):
    """
    Arguments: path: the directory for the image
    Return:    google vision api results
    """
    frame = cv2.imread(path)
    img_name = path.split('/')[-1].split('.')[0]
    img_type = path.split('/')[-1].split('.')[1]
    success, encoded_image = cv2.imencode('.'+img_type, frame)
    content_bytes = encoded_image.tobytes()
    return content_bytes, frame   
    
def bytes_to_text(content_bytes):
    """
    Extract the OCR text
    Return the text in dictionary
    """
    image = vision.Image(content=content_bytes)
    text_response = client.text_detection(image=image)
    text_response = MessageToDict(text_response._pb)
    return text_response

def detect_angle(content_bytes):
    """
    Call face detection api to get the angle of the face
    """
    image = vision.Image(content=content_bytes)
    text_response = client.face_detection(image=image)
    text_response = MessageToDict(text_response._pb)
    return text_response['faceAnnotations'][0]['rollAngle']
   
if __name__ == '__main__':
    if(len(sys.argv) > 1):
        # input: image path
        img_path = sys.argv[1]
        print('OCR processing '+img_path)
        bytes, frame = load_img(img_path)
        ocr_result  = bytes_to_text(bytes)
    else:
        print('argument is missing: image path')
