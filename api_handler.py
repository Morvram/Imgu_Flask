import requests
from requests_oauthlib import OAuth1
import json
import os
import api_keys
import base64

clientID = api_keys.imgurClient

headers={
    "Authorization": "Client-ID " + clientID
}

#TODO maybe make it so that if the access key has expired, it will be overwritten - to do this, we'll have to store the access key in a txt file and keep the refresh key in api_keys.
os.environ['API_KEY'] = api_keys.imgurKey

def getFromImgur (url):
    if url.find("https://"):
        url = url.rsplit("/", 1)[1]
    getUrl = "https://api.imgur.com/3/image/" + url
    print(getUrl)
    print("Fetching the image...")
    status = requests.get(getUrl, headers=headers)
    data = status.json()
    if data['status'] == 200:
        print("Fetched successfully.")
        z = data['data']['link']
        z = z.replace("i.imgur", "imgur")
        return z
    else:
        print("Failed to upload.")
        return "-1"

def getImageSize (image):
    image = image.rsplit("/", 1)[1]
    image = image.split(".", 1)[0]
    getUrl = "https://api.imgur.com/3/image/" + image
    print(getUrl)
    print("Fetching the image's json...")
    status = requests.get(getUrl, headers=headers)
    data = status.json()
    print(data)
    if data['status'] == 200:
        return data['data']['size']
    else:
        print("Something went wrong fetching the image's size!")
        return -1


def uploadToImgur (image): 
    #If it doesn't work after a few days, ask for help
    url = "https://api.imgur.com/3/upload"
    print("Uploading your image...")
    status = requests.post(url + "?Client-ID=" + clientID, headers=headers, files={'image': open(image, 'rb')})
    data = status.json()
    print(data)
    if data['status'] == 200:
        print("Uploaded successfully.")
        print("Link to your image is: " + data['data']['link'])
        z = data['data']['link']
        z = z.replace("i.imgur", "imgur")
        return z
    else:
        print("Failed to upload.")
        return "-1"

#print(os.environ.get('API_KEY'))

#testImg = "IMG_3744.jpg"
#x = base64.b64encode(open(testImg, 'rb').read())
#status = requests.post("https://api.imgur.com/3/upload?Client-ID=" + clientID, headers=headers, data={"image": x})
#print(status.json())
#uploadToImgur(testImg)

#print(getImageSize("https://i.imgur.com/VATIiUX.jpg"))