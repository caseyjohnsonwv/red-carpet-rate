import csv
from datetime import datetime, timedelta
from os import getenv
import re
from typing import List
from bs4 import BeautifulSoup
from gcloud import storage
import requests
from requests.adapters import Retry, HTTPAdapter


BASE_URL = 'https://reservations.universalorlando.com/ibe/default.aspx?hgID=641'

req = requests.Session()
retries = Retry(total=3, backoff_factor=1)
req.mount('http://', HTTPAdapter(max_retries=retries))


forecast_range_days = getenv('forecast_range_days')
forecast_range_days = int(forecast_range_days) if forecast_range_days else 1


class Promo:
    FAMILY_AND_FRIENDS = 'ZEMPUS'
    RED_CARPET_RATE = 'ZEMPUR'
    NONE = ''

    def get_all():
        return [Promo.FAMILY_AND_FRIENDS, Promo.RED_CARPET_RATE, Promo.NONE]


class HotelRate:
    def __init__(self, name, rate, check_in, check_out, nights, search_url, promo):
        self.name = name
        self.rate = rate
        self.check_in = check_in
        self.check_out = check_out
        self.nights = nights
        self.search_url = search_url
        self.promo = promo
        self.total = rate*nights

    def __repr__(self):
        return f"${self.total} ({self.check_in} - {self.check_out} @ ${self.rate}/night with {self.promo}): {self.name}"

    def as_csv_row(self):
        return [self.total, self.rate, self.check_in, self.check_out, self.nights, self.name, self.promo, self.search_url]

    def csv_header_row():
        return ['Total', 'Rate', 'Check In', 'Check Out', 'Nights', 'Property', 'Promo', 'URL']


class UO:
    def get_deals(check_in:str, nights:int, promo:str) -> List[HotelRate]:
        deals = []
        check_out = datetime.strftime(datetime.strptime(check_in, '%m/%d/%Y') + timedelta(days=nights), '%m/%d/%Y')
        check_in_fmt = datetime.strftime(datetime.strptime(check_in, '%m/%d/%Y'), '%Y-%m-%d')
        check_out_fmt = datetime.strftime(datetime.strptime(check_out, '%m/%d/%Y'), '%Y-%m-%d')

        full_url = f"{BASE_URL}&checkin={check_in}&nights={nights}&promo={promo}"
        resp = req.get(full_url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        names = [r.text for r in soup.find_all('a', {'class': 'wsName'})]
        rates = [r.text for r in soup.find_all('span', {'class': 'ws-number'})]
        for i,rate in enumerate(rates):
            try:
                rate = int(re.findall('\d+', rate)[0])
                promo = None if promo == '' else promo
                deal = HotelRate(names[i], rate, check_in_fmt, check_out_fmt, nights, full_url, promo)
                deals.append(deal)
            except ValueError | IndexError as ex:
                print(ex)

        return deals


def main():
    earliest_date = datetime.now() + timedelta(hours=2)
    latest_date = earliest_date + timedelta(days=forecast_range_days - 1)
    max_nights = 7

    deals = []
    check_in = earliest_date
    while check_in <= latest_date:
        check_in_fmt = datetime.strftime(check_in, '%m/%d/%Y')
        for night_count in range(1, max_nights+1):
            for promo in Promo.get_all():
                print(f"Querying {night_count}-night stays from {check_in_fmt} with promo '{promo}'")
                try:
                    results = UO.get_deals(check_in_fmt, night_count, promo)
                    deals.extend(results)
                    del results
                except requests.exceptions.Timeout:
                    print(f"Request timed out!")
        check_in += timedelta(days=1)
    deals.sort(key=lambda d:(d.check_in, d.total, d.name))
    
    csvpath = 'UO_Hotels.csv'
    with open(csvpath, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(HotelRate.csv_header_row())
        writer.writerows([d.as_csv_row() for d in deals])
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('uo-hotels-store')
    blob = bucket.blob(csvpath)
    blob.upload_from_filename(csvpath)
    print(f"Uploaded CSV to {blob.public_url}")
    


if __name__ == '__main__':
    main()