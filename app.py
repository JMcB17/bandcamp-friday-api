import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify


__version__ = '1.0.0'


DAY = timedelta(days=1)
DATETIME_FORMAT = '%a, %d %b %Y %H:%M:%S %z'
URL = 'https://isitbandcampfriday.com'


def get_data_fundraisers() -> dict:
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    bandcamp_friday_vm = soup.find('div', id='bandcamp-friday-vm')
    data_fundraisers = json.loads(bandcamp_friday_vm['data-fundraisers'])[0]

    return data_fundraisers


def format_response(data_fundraisers: dict) -> dict:
    next_bandcamp_friday = datetime.strptime(data_fundraisers['date'], DATETIME_FORMAT)
    next_end = next_bandcamp_friday + DAY
    now = datetime.now(tz=next_bandcamp_friday.tzinfo)
    it_is = (next_bandcamp_friday < now < next_end)

    response = {
        'it_is': it_is,
        'next_start': next_bandcamp_friday.timestamp(),
        'next_end': next_end.timestamp(),
        'cached_from': int(now.timestamp()),
        'data_fundraisers': data_fundraisers,
    }
    return response


def is_it_bandcamp_friday() -> bool:
    data_fundraisers = get_data_fundraisers()
    info_dict = format_response(data_fundraisers)
    return info_dict['it_is']


class CachedFriday:
    def __init__(self):
        self.last_response = format_response(get_data_fundraisers())

    def cached_response(self) -> dict:
        now = datetime.now().timestamp()

        if now < self.last_response['next_start']:
            pass
        elif (
                now < self.last_response['next_end']
                and self.last_response['next_start'] < self.last_response['last_cached']
        ):
            pass
        else:
            self.last_response = format_response(get_data_fundraisers())

        return self.last_response


app = Flask(__name__)
cached_friday = CachedFriday()


@app.route('/v1')
def api_view_v1():
    return jsonify(cached_friday.cached_response()['it_is'])


@app.route('/v2')
def api_view_v2():
    return jsonify(cached_friday.cached_response())


if __name__ == "__main__":
    app.run()
