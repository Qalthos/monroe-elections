#!/usr/bin/env python
#
# This code is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this code.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Nathaniel Case

""" Watchdog is a part of Monroe Election Dashboard."""
from __future__ import print_function
from datetime import datetime

import bs4
import requests
import sh
import yaml

def check_existence(url):
    try:
        html = requests.get(url).content
        soup = bs4.BeautifulSoup(html)
        return soup.find('election')['dt']
    except:
        return False

def check_election(county, date):
    date_parsed = datetime.strptime(date, '%Y%m%d').replace(hour=12)
    if date_parsed > now:
        # Parse the output of `atq`:
        # The output consists of `jobid date queue user`, but date has
        # lots of whitespace, so we split, throw away the ends, and join
        # it again.
        jobs = [' '.join(bits.split()[1:-2]) for bits in sh.atq().split('\n') if bits]
        for job in jobs:
            if datetime.strptime(job, '%a %b %d %H:%M:%S %Y') == date_parsed:
                # Job already exists
                break
        else:
            print("There's a new election coming up in {} at {}!".format(county, date_parsed))
            sh.at('-t', '{}1200'.format(date), _in="python election.py -l")


with open('config.yaml') as config_file:
    conf = yaml.load(config_file)

now = datetime.now().replace(hour=12)
for county in conf:
    dates = []

    if conf[county].get('url'):
        url = conf[county]['url'] + 'ElectionEvent.xml'
        date = check_existence(url)
        if date:
            check_election(county, date)
    elif conf[county].get('base_url'):
        for etype in ['pe', 'ge']:
            url = conf[county]['base_url'].format(year=now.year%100, election=etype)
            date = check_existence(url)
            if date:
                check_election(county, date)
