# Web scraper for retrieving housing data from https://quotablevalue.co.nz/property-search/
# Written by Shaun Lowis, for Bodeker Scientific

import time
import os
import requests
import csv
import itertools
import random

import pandas as pd

from urllib.parse import urlparse
from urllib.request import Request, urlopen

from multiprocessing import Pool
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def GET_UA():
    uastrings = [
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
    ]
 
    return random.choice(uastrings)

def save_errs(failed_urls, err_path):
    """Save error indices to .csv file

    Args:
        failed_urls (dictionary): Keys = int iterable, values = web addresses.
    """
    
    err_file = os.path.join(err_path, 'failed_urls.csv')

    if os.path.exists(err_file):
        with open(err_file, "a") as f:
            writer = csv.writer(f)
            for key, value in failed_urls.items():
                writer.writerow([key, value])
                
    # If the file already exists, append to it;
    # Else write the file.
    else:
        with open(err_file, "w") as f:
            writer = csv.writer(f)
            for key, value in failed_urls.items():
                writer.writerow([key, value])

    print('Added errors...')

def scrape(count):
    """ Navigates to quotablevalue.co.nz and retrieves all of the property info on each house in their database.
        returns a dictionary containing houses' info."""
    failed_urls = {}
    ua = UserAgent()
    proxies = []

    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', ua.random)
    proxies_doc = urlopen(proxies_req).read().decode('utf8')

    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = soup.find(id='proxylisttable')

    # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append({'ip': row.find_all('td')[0].string, 'port': row.find_all('td')[1].string})

    out_dict = {}
    it = 0
    while True:

        proxy_index = random.randint(0, len(proxies) - 1)
        proxy = proxies[proxy_index]

        house_details = {}
        page = requests.get(f"https://quotablevalue.co.nz/property-search/property-details/{count}/", headers={'User-Agent': GET_UA()}, proxies=proxy)

        # To combat scraper being too fast for website, add sleep
        # time.sleep(1.5)
        
        soup = BeautifulSoup(page.content, 'html.parser')
        address = soup.find(id="property-details-address")

        dl_data = soup.find_all("dd")

        # Below finds the respective information about each home.
        # The try and except block is a catch for failed websites or indices.
        # The failed get operation is reported and stored to a file.
        house_vars = ['category_code', 'category_description', 'capital_value', 'land_value',
                    'last_valued', 'improvement_value', 'valuation_reference', 'legal_description',
                    'council', 'land_use', 'units_of_use', 'property_contour', 'view_from_property', 
                    'roof_construction', 'roof_condition', 'wall_construction', 'wall_condition', 
                    'number_of_free_standing_garages', 'number_of_main_roof_garages', 'number_of_carparks'
                    'deck', 'other_significant_improvements']
        try:
            for i, var in enumerate(house_vars):
                data = dl_data[i]
                house_details[var] = data
            out_dict[address.text] = house_details

        except IndexError:
            failed_urls[count] = f"https://quotablevalue.co.nz/property-search/property-details/{count}/"
            print(f'Get operation failed on iteration {it}, count {count}, reporting.')

        # This function ends after 1000 iterations in order to produce multiple files.
        # Also allows the function to be easily rerun at some interval if a crash happens.
        if it == 1000:
            print(f'{count} houses done.')
            break

        else:
            count += 1
            it += 1
    save_errs(failed_urls, r'/mnt/temp/sync_to_data/NZ_buildings/housing_data/iteration_2')

    return out_dict

def save_data(in_dict, path, iterations):
    """ Checks the target directory, expects input dictionary of house information, saves
        a new file, with filename changing as per first line of code below."""

    file = os.path.join(path, f'qv_housing_{iterations}.csv')
    fields = ['category_code', 'category_description', 'address', 'capital_value', 'land_value', 'last_valued', 
            'improvement_value', 'valuation_reference', 'legal_description', 'council', 'land_use', 'units_of_use',
            'property_contour', 'view_from_property', 'roof_construction', 'roof_condition', 'wall_construction',
            'wall_condition', 'number_of_free_standing_garages', 'number_of_main_roof_garages', 'number_of_carparks',
            'deck', 'other_significant_improvements']
    
    # If the file already exists, append to it;
    if os.path.exists(file):
        with open(file, "a") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            for k,d in (in_dict.items()):
                w.writerow(mergedict({'address': k}, d))

    # Else write the file.
    else:
        with open(file, "w") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for k,d in (in_dict.items()):
                w.writerow(mergedict({'address': k}, d))
            
    print(f'Wrote file to {file}')
        

def mergedict(a,b):
    """ Helper function to convert nested dictionary to .csv easier."""
    a.update(b)
    return a


def main():
    """ Runs scraper per iteration count until all data from website is scraped, saves to 
        house_data_dir a file for when scraper count reaches 1000, i.e. every 1000 houses,
        makes a new .csv file."""
    house_data_dir = r'/mnt/temp/sync_to_data/NZ_buildings/housing_data/iteration_2'
    
    print('Starting web scraping...')

    x = 0

    while True:
        with Pool(processes=4) as p:
            df_list = p.map(scrape, [x*1000, ((x+1)*1000), ((x+2)*1000), ((x+3)*1000)])

        with Pool(processes=4) as p1:
            args = [(df_list[0], house_data_dir, (x*1000)), (df_list[1], house_data_dir, ((x+1)*1000)), 
                    (df_list[2], house_data_dir, ((x+2)*1000)), (df_list[3], house_data_dir, ((x+3)*1000))]
            p1.starmap(save_data, args)

        x += 4

        print(f'Currently on iteration x = {x * 1000}...')

main()
