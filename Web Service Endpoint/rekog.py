'''
Detect imprinted text on pill images using AWS Rekognition.

print(cv2.getBuildInformation())
'''
import re
import boto3
from dotenv import load_dotenv
import os
import cv2

load_dotenv()

client = boto3.client('rekognition', 
                    region_name=os.getenv("AWS_DEFAULT_REGION"),
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))


# ____  Filter to increase image contrast  ______
def add_contrast(image_path):
    print('add_contrast: started :', image_path)
    #-----Reading the image-----------------------------------------------------
    img = cv2.imread(image_path)
    print('add_contrast: image read :', image_path)
            
    #-----Converting image to LAB Color model----------------------------------- 
    lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    print('add_contrast: converted to LAB :', image_path)

    #-----Splitting the LAB image to different channels-------------------------
    l, a, b = cv2.split(lab)
    print('add_contrast: LAB image split :', image_path)

    #-----Applying CLAHE to L-channel-------------------------------------------
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    print('add_contrast: clahe instantiated :', image_path)

    cl = clahe.apply(l)
    print('add_contrast: clahe applied :', image_path)

    #-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
    limg = cv2.merge((cl,a,b))
    print('add_contrast: clahe merged :', image_path)

    #-----Converting image from LAB Color model to RGB model--------------------
    image_contrast = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    print('add_contrast: converted to RGB :', image_path)

    return image_contrast


# ____________ Text Detection Functions ______________
def post_rekog_with_filter(pic_json, con_fidence=70):
    imageURL_list = pic_json.get("image_files")   #  Get list of image file names
    all_text = []        # store text from image(s)
    all_filter_text = [] # store text from enhanced image
    ctr = 0
    for imageURL in imageURL_list:
        if imageURL != "":
            # ------------- Detecting text from original image ------------
            imageFile = imageURL
            with open(imageFile, 'rb') as image:
                # !!!!!!  WRAP THIS IN A TRY / CATCH !!!!!!!!!
                print('detect started', imageFile)
                response = client.detect_text(Image={'Bytes': image.read()})
                print('detect completed', imageFile)
            textDetections = response['TextDetections'] #  Detected Text (List of Dicts)
            #  ______ Parse through & create set of detected text ______
            text_found = []
            for text in textDetections:
                if text['Confidence'] > con_fidence:
                    text_found.append(text['DetectedText'])
            text_set = list(set(text_found))
            # _______ Append detected text to "all_text" list ___
            all_text.append(text_set) 
            print('parsed text :', all_text)
           
            # _________ create enhanced image _____________
            print('image enhance started :', imageFile)
            filtered_img = add_contrast(imageFile)
            print('image enhance completed :', imageFile)
            ctr += 1
            temp_img = "filtered" + str(ctr) + ".jpg"
            cv2.imwrite(temp_img, filtered_img)
            imageFile2 = temp_img
            print('enhanced image:', imageFile2)
            # ___ Detecting text from enhanced image __
            with open(imageFile2, 'rb') as image:
                # !!!!!!  WRAP THIS IN A TRY / CATCH !!!!!!!!!
                print('start detecting enhanced image:', imageFile2)
                response2 = client.detect_text(Image={'Bytes': image.read()}) 
                print('detect complete - enhanced image:', imageFile2)
            textDetections2 = response2['TextDetections']    # LIST OF DICTS
            #  ______ Parse through & create set of detected text ______
            text_found2 = []
            for text in textDetections2:
                if text['Confidence'] > con_fidence:
                    text_found2.append(text['DetectedText'])
            text_set2 = list(set(text_found2))
            # ____ Appending detected text in image to "all_filter_text" list ______
            all_filter_text.append(text_set2)

            # ___ remove temp images ___
            os.remove(imageFile)
            os.remove(imageFile2)
        else:
            continue
    
    # ------------- Flattening 'all_text' (list of lists) into 1 list -------------
    text_list = [text for sublist in all_text for text in sublist]
    text_list = list(set(text_list))
    text_list2 = [text for sublist in all_filter_text for text in sublist]
    text_list2 = list(set(text_list2))
    # ------------- Splitting any text blob that may have digits and numbers together ----
    unique_list = []
    for each in text_list:
        num_split = re.findall(r'[A-Za-z]+|\d+', each)
        unique_list.append(num_split)
    unique_list2 = []
    for each in text_list2:
        num_split = re.findall(r'[A-Za-z]+|\d+', each)
        unique_list2.append(num_split)
    # ------------- Flattening again into one list with just unique values -------------
    unique_list = [text for sublist in unique_list for text in sublist]
    unique_list = list(set(unique_list))
    unique_list2 = [text for sublist in unique_list for text in sublist]
    unique_list2 = list(set(unique_list))
    # ------------- Return 'final_list' -------------
    final_list = set(unique_list + unique_list2)
    # If 'final_list' is empty, return empty set
    if len(final_list) == 0:
        return {}
    return final_list


def post_rekog(pic_json, con_fidence=70):
    imageURL_list = pic_json.get("image_files")   # Get list of image file names
    all_text = []  # store text from uploaded image(s)
    # Looping through image(s)
    for imageURL in imageURL_list:
        print(imageURL)
        if imageURL != "":
            imageFile = imageURL
            # ___ Detecting text from original image ___
            with open(imageFile, 'rb') as image:
                # !!!!!!  WRAP THIS IN A TRY / CATCH !!!!!!!!!
                print('detect started', imageFile)
                response = client.detect_text(Image={'Bytes': image.read()})
                print('detect completed', imageFile)
            textDetections = response['TextDetections']  #(List of Dictionaries)
            # Parse through and create set of Detected Text
            text_found = []
            for text in textDetections:
                if text['Confidence'] > con_fidence:
                    text_found.append(text['DetectedText'])
            text_set = list(set(text_found))
            all_text.append(text_set)   # Append detected text to "all_text" list
            os.remove(imageFile)  # remove uploaded images
        else:
            continue
            
    # Flattening 'all_text' (list of lists) into 1 list
    text_list = [text for sublist in all_text for text in sublist]
    text_list = list(set(text_list))
    # Splitting any text blob that may have digits and numbers together
    unique_list = []
    for each in text_list:
        num_split = re.findall(r'[A-Za-z]+|\d+', each)
        unique_list.append(num_split)
    # Flattening again into one list with just unique values
    unique_list = [text for sublist in unique_list for text in sublist]
    unique_list = list(set(unique_list))
    # Return 'final_list'
    final_list = set(unique_list)
    # If 'final_list' is empty return empty set
    if len(final_list) == 0:
        return {}
    return final_list

# __________ M A I N ________________________
if __name__ == '__main__':
    # data = {"image_locations": ["https://s3.us-east-2.amazonaws.com/firstpythonbucketac60bb97-95e1-43e5-98e6-0ca294ec9aad/adderall.jpg", ""]}
    data = {"image_locations": ["https://raw.githubusercontent.com/ed-chin-git/ed-chin-git.github.io/master/sample_pill_image.jpg", ""]}
    # data = {"image_locations": ["https://s3.us-east-2.amazonaws.com/firstpythonbucketac60bb97-95e1-43e5-98e6-0ca294ec9aad/img2b.JPG",
    #                            "https://s3.us-east-2.amazonaws.com/firstpythonbucketac60bb97-95e1-43e5-98e6-0ca294ec9aad/img2b.JPG"]}
    print(post_rekog(data))
    print(post_rekog_with_filter(data))
