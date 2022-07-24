import pytz
from pytz import timezone
import calendar
import datetime
import os
import uuid
import boto3
from flask import request, redirect
from dotenv import load_dotenv
load_dotenv()

# Check for valid image file types
def allowed_image(filename):
    allowed_ext = ["PNG", "JPG", "JPEG"]
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in allowed_ext:
        return True
    else:
        return False

# Add uploaded/saved image files to S3 bucket
def add_to_s3(image_file, filepath):
    s3_resource = boto3.resource('s3')
    # get bucket name from .env
    img_bucket_name = os.getenv('S3_IMAGE_BUCKET') # 'elasticbeanstalk-us-east-2-613733681899'

    # Looping through files to upload into S3 bucket
    s3_resource.Object(img_bucket_name, 
                        image_file).upload_file(
                        Filename=filepath)

# Upload file from UI button in jinja template
def file_upload():
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    data = {"image_files": ["", ""]}
    s3_path =  os.getenv('S3_IMAGE_PATH')      #  https://rxid-rekog.s3.us-east-2.amazonaws.com/

    print(APP_ROOT)
    target = os.path.join(APP_ROOT, 'images')
    print(target)

    # making "image" directory if does not exist
    if not os.path.isdir(target):
        os.mkdir(target)
        print("Made new 'image' directory")

    image_list = request.files.getlist("image")
    # making sure we only get upto 2 images
    if len(image_list) > 2: 
        # cutting number images to just 2
        image_list = image_list[:2] 
    print(f'Image list: {len(image_list)}')

    i=0 # index to replace "" in data dict for S3 url
    for image in image_list:
        print(f"image: {image}")
        filename = image.filename      
        # if file does not have a name
        if filename == "":
            print("Image file must have a filename")
            return redirect(request.url)          
        # if it's not an image file with expected extension
        if not allowed_image(filename):
            print("Your image has a file extension that is not allowed")
            return redirect(request.url)
        else:
            # file extension
            ext = filename.rsplit(".", 1)[1] 
            # new unique file name
            new_filename = str(uuid.uuid4()) + "." + str(ext) 
            destination = "/".join([target, new_filename])
            image.save(destination)
            print(f"Destination: {destination}")
            # ___ upload "destination" file to S3 bucket ____
            # print("---->>> Should have added to S3")
            # add_to_s3(new_filename, destination) 
            # data["image_locations"][i] = s3_path + new_filename
            data["image_files"][i] = destination
            i = i + 1
    print(data)
    return data


# _________ Parse API input string for parameters _________________
#  input->  sample API input string(s)-> /indentify/param1=Red&param2=Pill
#  ouputs -->  
def parse_input(s):
    weekday, hour = day_hour()
    # parse input string for model input values
    weather_str = ''
    weather_loc = s.find("weather=") # returns -1 if not found
    if weather_loc > 0:
        weather_str = s[s.find("weather=")+8:s.find("&",weather_loc)]

    day_str = ''
    day_loc = s.find("day=")
    if day_loc > 0:
        day_str = s[day_loc+4:s.find("&",day_loc)]

    month_num = 1
    month_loc = s.find("month=")
    if month_loc > 0:
        month_str = s[month_loc+7:s.find("&",month_loc)]
        month_str = s.find()
        month_num = 1
        month_dict = dict((v,k) for k,v in enumerate(calendar.month_name))
        for key, value in month_dict.items():
            if key == month_str:
                month_num = value

# _______ chromedriver test __________
def chromedriver_test():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.youtube.com/")
    element_text = driver.find_element_by_id("title").text
    return element_text

# _______ GET CURRENT DAY AND HOUR __________
def day_hour():
    # get current time in pacific timezone
    utc = pytz.utc
    utc.zone
    pacific = timezone('US/Pacific')
    #  bin the current hour
    time = datetime.datetime.today().astimezone(pacific)    
    hour = (time.hour)
    if hour <= 4:
        hour = 1
    elif 4 > hour <= 8:
        hour = 2
    elif 8 > hour <= 12:
        hour = 3
    elif 12 > hour <= 16:
        hour = 4
    elif 16 > hour <= 20:
        hour = 5
    else:
        hour = 6
    # Day of the week
    weekday = time.isoweekday()
    d = {1: 'MONDAY', 2: 'TUESDAY', 3: 'WEDNESDAY', 4: 'THURSDAY', 
        5: 'FRIDAY', 6: 'SATURDAY', 7: 'SUNDAY'}
    for key, value in d.items():
        if key == weekday:
            weekday = value
    return weekday, hour
