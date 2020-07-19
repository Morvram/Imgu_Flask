import requests
from requests_oauthlib import OAuth1
import json

artist="Miracle of Sound"

url = "https://api.spotify.com/v1/artists/" + artist.replace(" ", "%20")

auth="BQDDf7I5ojrzmX1O6J5p3H-NuYSezepzzmg9PUW8BKQ7NMl7wSxhGe2e6051ETZBINDt3KbAu3QqqezfMydedjTi_Tm_Yb9CwM0rNe-McW-_ykQo9unb9dhzDt8RANKbZD6y7GzN-x3pH8I"

content_type = "application/json"

params={
    "Authorization": "Bearer " + auth,
    "Accept": content_type,
    "Content-Type": content_type
}

r = requests.get(url, headers=params)

print(r.text)

responseItem = r.json()
