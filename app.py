import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_caching import Cache


DAY = timedelta(days=1)


app = Flask(__name__)
cache = Cache(app)


@app.route('/isitbandcampfriday')
def is_it_bandcamp_friday():
    response = requests.get('https://isitbandcampfriday.com')
    soup = BeautifulSoup(response.content, 'html.parser')
    bandcamp_friday_vm = soup.find('div', class_='bandcamp-friday-vm')
    data_fundraisers = json.loads(bandcamp_friday_vm['data-fundraisers'])

    next_bandcamp_friday = datetime.strptime(data_fundraisers['data'], '%a, %d %b %Y %H:%M:%S %z')

    is_it = (next_bandcamp_friday < datetime.now() < next_bandcamp_friday + DAY)

    return jsonify(is_it)

