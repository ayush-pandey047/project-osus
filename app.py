from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
import string
from datetime import datetime, timedelta


load_dotenv()

app = Flask(__name__)
client = MongoClient(os.getenv('MONGO_PATH'), int(os.getenv('MONGO_PORT')))

# MongoDB Database Access
database = client.ShortUrlDatabase
ShortUrlDatabase = database.URLData


# Functions
def generate_random_string(length=5):
    '''
    This function gives a combination of lowercase and uppercase letters of k length
    '''
    print('generating a random keyword')
    letters = string.ascii_letters
    random_string = ''.join(random.choices(letters, k=length))
    print('keyword generated: '+str(random_string))
    return random_string


def is_keyword_present(keyword):
    '''
    Function to check if the current keyword is present in the DB or not
    '''
    print('Fetching if keyword is present in DB: '+str(keyword))
    present = 0
    for item in ShortUrlDatabase.find():
        if (item['keyword'] == keyword):
            print('keyword present in DB: '+str(keyword))
            present = 1
    print('keyword not present in DB: '+str(keyword))
    return present

# Routes


@app.route('/')
def home():
    '''
    Index page for URL Shortener (Project OSUS (Open Source URL Shortener))
    '''
    print('Home Page API Called, rendering template')
    return render_template('index.html')

@app.route('/documentation')
def documentation():          
    return render_template('documentation.html')

@app.route('/getURL')
def currentURl():
    '''
    This function will return the current working URL, something like 'http://127.0.0.1:5000/'
    '''
    print('getURL API Called')
    current_url = request.host_url
    print('Current URL: '+str(current_url))
    return f'The app is running on {current_url}'


@app.route('/shorten', methods=['POST'])
def shortenAPI():
    '''
    This method will shorten the link and give the short URL
    '''
    # Logic
    # This end point should check if that URL is already present in the DB or not
    # This end point should take only POST calls and return the shortened version of the URL
    # do: Handle Get cases
    print('URL Shorten Called')
    print('Mongo Connection: '+str(os.getenv('MONGO_PATH')[:6]))
    
    if request.method == 'POST':
        longUrl = request.json.get("longUrl")
        keyword = request.json.get("keyword")
        expiration_date_time = request.json.get("expirationDateTime") # added expiry time

        # Logs  
        print('Long URL Received: ' + str(longUrl))
        print('Keyword Received: '+str(keyword))

        if keyword == '':
            keyword = generate_random_string()
            print('New keyword generated:' + str(keyword))


            
        expiration_timestamp = None
        if expiration_date_time:
            expiration_timestamp = datetime.fromisoformat(expiration_date_time)  # Parse ISO format datetime

        if is_keyword_present(keyword) == 0:
            ShortUrlDatabase.insert_one(
               {'keyword': keyword, 'url': longUrl, 'clicks': 0, 'expiryTime': expiration_timestamp})
            print('DB insert successful')
        else:
            return jsonify({'error': 'The Keyword Already Exists, Choose a Different One'}), 400

    if request.method == 'GET':
        print('Called get method on shorten end-point, throwing error')
        return "GET Method Not Allowed On This End Point"

    return jsonify({'shortUrl': str(request.host_url)+str(keyword)})


@app.route('/analytics', methods=['GET', 'POST'])
def analyticsAPI():
    # No Authentication to check the analytics of the URL as of now
    '''
    This end point will take URL and will provide the analytics for that URL, since we don\'t have authentication we\'ll be asking just for the keyword and we\'ll give the analytics for the URL as of now '''
    print('Analytics API Called')
    return 'Under Development'


@app.route('/heartbeat')
def hearBeat():
    '''
    This end point should do all the checks/ add dummy data to DB if required and respond saying the website is UP
    '''
    print('heartbeat API called')
    return 'The website is up'

@app.route('/<keyword>')
def reroute(keyword):
    print('Clicked on shortURL')
    if keyword == 'favicon.ico':
        return ''
    link_status = 0
    current_time = datetime.now()
    print(current_time,"=====")
    print('Finding the URL Keyword')
    print('Mongo Connection: '+str(os.getenv('MONGO_PATH')[:6]))
    for item in ShortUrlDatabase.find():
        if (item['keyword'] == keyword):
            expiry_time = item.get('expiryTime')
            if expiry_time and current_time > expiry_time:
                return render_template('expired.html', keyword=keyword)
            redirection = item['url']
            # Write Logs Here
            print('Short URL <> Long URL mapping found in DB')
            link_status = 1
    if (link_status == 0):
        print('Link Not Found in DB')
        return "Link Not Found"
    print('Redirecting to long url: '+str(redirection))
    return redirect(redirection, code=302)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
