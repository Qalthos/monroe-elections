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
from time import sleep
import urllib

from BeautifulSoup import BeautifulStoneSoup

from gitsupport import commitAll
from view import write_html, write_json

# A few known sources of valid XML files
#BASE_URL = "http://www.london.ca/elections/results/"
#BASE_URL = "http://city.waterloo.on.ca/election2010/"
#BASE_URL = "http://guelph.ca/vote/uploads/results/"
BASE_URL = "http://enr.monroecounty.gov/"

# These have election-specific directories.  In these examples, the 2012
# Republican Presidential Primary
#BASE_URL = "http://www.co.chautauqua.ny.us/departments/boe/Documents/2012%20Presidential%20Primary/"
#BASE_URL = "http://apps.suffolkcountyny.gov/boe/eleres/12pr/"

BASE_DIR = os.path.split(os.path.abspath(__file__))[0]


def initial_read():
    """
    Reads the contents of ElectionEvent.xml.
    This file should not change during the election, so should only need to be
    read once.

    In case results are not yet available, it also zeroes out data.

    """

    filename = pull_file('ElectionEvent.xml')
    with open(filename) as file_:
        html = file_.read()

    soup = BeautifulStoneSoup(html)
    data = dict()

    election = soup.find('election')
    data['election'] = {'nm': election['nm'], 'des': election['des'], \
      'jd': election['jd'], 'ts': election['ts'], 'pol': 0, 'clpol': 0}

    areatypes = soup.findAll('areatype')
    data['areatype'] = soup_to_dict(areatypes, 'id', ['nm', 's', 'id'])

    areas = soup.findAll('area')
    data['area'] = soup_to_dict(areas, 'id', ['nm', 'atid', 'el', 's', 'id'])

    contests = soup.findAll('contest')
    data['contest'] = soup_to_dict(contests, 'id', ['nm', 'aid', 'el', 's', 'id'])

    parties = soup.findAll('party')
    data['party'] = soup_to_dict(parties, 'id', ['nm', 'ab', 's', 'id'])

    choices = soup.findAll('choice')
    data['choice'] = soup_to_dict(choices, 'id', ['nm', 'conid', 's', 'id'])

    return data


def pull_file(filename):
    """Pulls a file from a remote source and saves it to the disk."""
    url = "%s%s" % (BASE_URL, filename)

    filepath = os.path.join(BASE_DIR, "data-submodule")
    os.chdir(filepath)
    (filename, headers) = urllib.urlretrieve(url, filename)
    commitAll()
    os.chdir(BASE_DIR)

    return os.path.join(filepath, filename)


def scrape_results(data):
    """
    Reads the contents of results.xml.
    This is the file that has all the changing information, so this is the
    method that should get run to update the values.

    """

    filename = pull_file('results.xml')
    with open(filename) as file_:
        html = file_.read()

    soup = BeautifulStoneSoup(html)

    election = soup.find('results')
    data['election'].update({'pol': election['pol'],
                             'clpol': election['clpol'], 'ts': election['ts'],
                             'fin': election['fin']})
    areas = soup.findAll('area')
    area = soup_to_dict(areas, 'id', ['bal', 'vot', 'pol', 'clpol'],
                        data['area'])
    contests = soup.findAll('contest')
    cont = soup_to_dict(contests, 'id', ['bal', 'bl', 'uv', 'ov'],
                        data['contest'])
    choices = soup.findAll('choice')
    cand = soup_to_dict(choices, 'id', ['vot', 'e'], data['choice'])

    return {'election': data['election'], 'areatype': data['areatype'],
            'area': area, 'contest': cont, 'choice': cand, 'party': data['party']}


def soup_to_dict(soup, key, values, data=None):
    """
    Reads a bunch of attributes form an XML tag and puts them into a dict.

    """

    if not data:
        data = {}
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
                      default=120,
                      help="number of seconds to sleep between runs")
    options, args = parser.parse_args()

    try:
        float(options.interval)
    except TypeError as e:
        print "Interval *must* be a number, not '", options.interval, "'"
        sys.exit(1)


    print "Reading data"
    DATA = initial_read()
    while True:
        print "Scraping results"
        DATA = scrape_results(DATA)

        print "Writing json."
        write_json(DATA)

        print "Writing file(s)."
        write_html(DATA)

        if not options.loop:
            break

        print "Sleeping for", options.interval, "seconds"
        sleep(float(options.interval))
