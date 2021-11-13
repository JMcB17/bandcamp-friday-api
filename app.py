import json
from datetime import datetime, timedelta
from typing import Callable

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_caching import Cache


# add more info as json
# v1
# standalone func
# remove flask_caching


DAY = timedelta(days=1)


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})


def get_data_fundraisers() -> dict:
    response = requests.get('https://isitbandcampfriday.com')
    soup = BeautifulSoup(response.content, 'html.parser')
    bandcamp_friday_vm = soup.find('div', id='bandcamp-friday-vm')
    data_fundraisers = json.loads(bandcamp_friday_vm['data-fundraisers'])[0]

    return data_fundraisers


def format_response(data_fundraisers: dict) -> dict:
    next_bandcamp_friday = datetime.strptime(data_fundraisers['date'], '%a, %d %b %Y %H:%M:%S %z')
    next_end = next_bandcamp_friday + DAY
    now = datetime.now(tz=next_bandcamp_friday.tzinfo)
    it_is = (next_bandcamp_friday < now < next_end)

    response = {
        'it_is': it_is,
        'next_start': next_bandcamp_friday.timestamp(),
        'next_end': next_end.timestamp(),
        'now': now.timestamp(),
        'data_fundraisers': data_fundraisers,
    }
    return response


def is_it_bandcamp_friday() -> bool:
    data_fundraisers = get_data_fundraisers()
    info_dict = format_response(data_fundraisers)
    return info_dict['it_is']


class CachedFriday:
    def __init__(self):
        self.next: datetime = datetime.fromtimestamp(0)

    def cached_is_it_bandcamp_friday(self) -> bool:
        data_fundraisers = get_data_fundraisers()
        info_dict = format_response(data_fundraisers)

        it_is = info_dict['it_is']
        next_end = info_dict['next_end']
        next_bandcamp_friday = info_dict['next_start']

        if it_is:
            self.next = next_end
        else:
            self.next = next_bandcamp_friday

        return it_is

    # noinspection PyUnusedLocal
    def cache_check(self, f: Callable):
        if self.next is None:
            return True

        now = datetime.now(tz=self.next.tzinfo)
        if self.next < now:
            return True

        return False


cached_friday = CachedFriday()


@app.route('/isitbandcampfriday')
@cache.cached(unless=cached_friday.cache_check)
def api_view():
    return jsonify(cached_friday.cached_is_it_bandcamp_friday())


if __name__ == "__main__":
    app.run()
