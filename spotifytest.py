import requests
from requests_oauthlib import OAuth1
import json
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

db = SQL("postgres://ldrthfhaqyelpx:3350e790b7910d24ff94ec98eb5633d54b50e00d1864c7c162209e063676d04b@ec2-52-22-216-69.compute-1.amazonaws.com:5432/d96punflgs6a2d")

rows = db.execute("SELECT * FROM users")
print(rows)

username="BOB"
password="BobsPassword"


db.execute("INSERT INTO users (id, username, hash) VALUES (:userHash, :username, :hash)", userHash=generate_password_hash(username), username=username, hash=generate_password_hash(password))
rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
print(rows)