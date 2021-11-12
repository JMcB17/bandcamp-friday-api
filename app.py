import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_caching import Cache


DAY = timedelta(days=1)


app = Flask(__name__)
cache = Cache(app)


def is_it_bandcamp_friday():
    response = requests.get('https://isitbandcampfriday.com')
    soup = BeautifulSoup(response.content, 'html.parser')
    bandcamp_friday_vm = soup.find('div', id='bandcamp-friday-vm')
    data_fundraisers = json.loads(bandcamp_friday_vm['data-fundraisers'])[0]

    next_bandcamp_friday = datetime.strptime(data_fundraisers['date'], '%a, %d %b %Y %H:%M:%S %z')
    now = datetime.now(tz=next_bandcamp_friday.tzinfo)
    return next_bandcamp_friday < now < next_bandcamp_friday + DAY


@app.route('/isitbandcampfriday')
def api_view():
    return jsonify(is_it_bandcamp_friday())


if __name__ == "__main__":
    app.run()
