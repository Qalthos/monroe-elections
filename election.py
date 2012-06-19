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
#         Ralph Bean -- http://threebean.org
#         Beau Bouchard -- http://beaubouchard.com

import optparse
import os
import sys
from time import sleep
import urllib

from BeautifulSoup import BeautifulStoneSoup

from gitsupport import commitAll
from view import write_html, write_json

# A few known sources of valid XML files
#BASE_URL = "http://www.london.ca/elections/results/"
#BASE_URL = "http://city.waterloo.on.ca/election2010/"
#BASE_URL = "http://guelph.ca/vote/uploads/results/"

BASE_URLS = {
    'Monroe': "http://enr.monroecounty.gov/",
    'Suffolk': "http://apps.suffolkcountyny.gov/boe/eleres/12pr/",
    'Chautauqua': "http://www.co.chautauqua.ny.us/departments/boe/Documents/2012%20Presidential%20Primary/",
}

BASE_DIR = os.path.split(os.path.abspath(__file__))[0]


def pull_file(county, filename):
    """Pulls a file from a remote source and saves it to the disk."""
    url = "%s%s" % (BASE_URLS[county], filename)

    filepath = os.path.join(BASE_DIR, "data-submodule", county)

    # Create directory if necessary
    if not os.path.exists(filepath):
        os.mkdir(filepath)

    os.chdir(filepath)
    (filename, headers) = urllib.urlretrieve(url, filename)
    commitAll()
    os.chdir(BASE_DIR)

    return os.path.join(filepath, filename)


def initial_read(county):
    """
    Reads the contents of ElectionEvent.xml.
    This file should not change during the election, so should only need to be
    read once.

    In case results are not yet available, it also zeroes out data.

    """

    filename = pull_file(county, 'ElectionEvent.xml')
    with open(filename) as file_:
        html = file_.read()

    soup = BeautifulStoneSoup(html)
    data = dict()

    election = soup.find('election')
    data['election'] = {'nm': election['nm'], 'des': election['des'], \
      'jd': election['jd'], 'ts': election['ts'], 'pol': 0, 'clpol': 0}

    contests = soup.findAll('contest')
    data['contest'] = soup_to_dict(contests, 'id', ['nm', 'aid', 'el', 's', 'id'])
    seen_aids = set()
    for contest in data['contest'].values():
        seen_aids.add(contest['aid'])

    areas = soup.findAll('area')
    data['area'] = soup_to_dict(areas, 'id', ['nm', 'atid', 'el', 's', 'id'])
    seen_atids = set()
    dropped_aids = set()
    for aid, area in data['area'].items():
        if aid not in seen_aids:
            # No contest is attached to this area, so we can ignore it
            dropped_aids.add(aid)
        else:
            seen_atids.add(area['atid'])
    for aid in dropped_aids:
        del data['area'][aid]

    areatypes = soup.findAll('areatype')
    data['areatype'] = soup_to_dict(areatypes, 'id', ['nm', 's', 'id'])
    dropped_atids = set()
    for atid in data['areatype']:
        if atid not in seen_atids:
            # No areas attached to an areatype?  Drop those too.
            dropped_atids.add(atid)
    for atid in dropped_atids:
        del data['areatype'][atid]

    parties = soup.findAll('party')
    data['party'] = soup_to_dict(parties, 'id', ['nm', 'ab', 's', 'id'])

    choices = soup.findAll('choice')
    data['choice'] = soup_to_dict(choices, 'id', ['nm', 'conid', 's', 'id'])

    return data


def scrape_results(county, data):
    """
    Reads the contents of results.xml.
    This is the file that has all the changing information, so this is the
    method that should get run to update the values.

    """

    filename = pull_file(county, 'results.xml')
    with open(filename) as file_:
        html = file_.read()

    soup = BeautifulStoneSoup(html)

    election = soup.find('results')
    data['election'].update({'ts': election['ts'], 'clpol': election['clpol'],
                             'pol': election['pol'], 'fin': election['fin']})

    results = soup_to_dict(soup.findAll('area'), 'id', ['bal', 'vot', 'pol', 'clpol'])
    for id_ in results:
        try:
            data['area'][id_].update(results[id_])
        except KeyError:
            # We probably dropped it, so ignore.
            pass

    results = soup_to_dict(soup.findAll('contest'), 'id', ['bal', 'bl', 'uv', 'ov'])
    for id_ in results:
        data['contest'][id_].update(results[id_])

    results = soup_to_dict(soup.findAll('choice'), 'id', ['vot', 'e'])
    for id_ in results:
        data['choice'][id_].update(results[id_])

    return data


def soup_to_dict(soup, key, values):
    """
    Reads a bunch of attributes form an XML tag and puts them into a dict.

    """

    data = dict()
    for item in soup:
        if not data.get(item[key]):
            data[item[key]] = {}
        for value in values:
            if item.name == "choice" and value == "vot":
                if not data[item[key]].get(value):
                    data[item[key]][value] = {}
                if item.get('tot') == "1":
                    data[item[key]][value]['tot'] = int(item.get(value, 0))
                else:
                    data[item[key]][value][item['pid']] = int(item.get(value, 0))
            elif value == "e":
                if item.get(value):
                    data[item[key]][value] = item[value]
            elif value in ["bal", "s"]:
                data[item[key]][value] = int(item.get(value, 1))
            else:
                data[item[key]][value] = item.get(value, '0').encode('ASCII', 'xmlcharrefreplace')

    return data


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-l", "--loop", dest="loop",
                      action="store_true", default=False,
                      help="run in a loop (infinitely)")
    parser.add_option("-i", "--interval", dest="interval",
                      default=120, type='float',
                      help="number of seconds to sleep between runs")
    options, args = parser.parse_args()

    print "Reading data"
    DATA = dict()
    for county in BASE_URLS:
        DATA[county] = initial_read(county)
    while True:
        for county in BASE_URLS:
            print("Scraping results for %s county" % county)
            DATA[county] = scrape_results(county, DATA[county])

        #print "Writing json."
        #write_json(DATA)

        print "Writing file(s)."
        write_html(DATA)

        if not options.loop:
            break

        print "Sleeping for", options.interval, "seconds"
        sleep(options.interval)
