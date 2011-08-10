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
# 	  Beau Bouchard -- http://beaubouchard.com

from BeautifulSoup import BeautifulStoneSoup
from time import sleep
from urllib2 import urlopen, URLError
import optparse

from view import write_html

# A few known sources of valid XML files
#BASE_URL = "http://www.london.ca/elections/results/"
#BASE_URL = "http://city.waterloo.on.ca/election2010/"
#BASE_URL = "http://guelph.ca/vote/uploads/results/"
BASE_URL = "http://enr.monroecounty.gov/"

OFFLINE = False


def initial_read():
    """
    Reads the contents of ElectionEvent.xml.
    This file should not change during the election, so should only need to be
    read once.

    In case results are not yet available, it also zeroes out data.

    """

    if OFFLINE:
        html = file("ElectionEvent.xml").read()
    else:
        try:
            html = urlopen("%sElectionEvent.xml" % BASE_URL)
        except URLError:
            return None
    soup = BeautifulStoneSoup(html)

    election = soup.find('election')
    elect = {'nm': election['nm'], 'des': election['des'], \
      'jd': election['jd'], 'ts': election['ts'], 'pol': 0, 'clpol': 0}
    areatypes = soup.findAll('areatype')
    atyp = soup_to_dict(areatypes, 'id', ['nm', 's', 'id'])
    areas = soup.findAll('area')
    area = soup_to_dict(areas, 'id', ['nm', 'atid', 'el', 's', 'id'])
    contests = soup.findAll('contest')
    contest = soup_to_dict(contests, 'id', ['nm', 'aid', 'el', 's', 'id'])
    parties = soup.findAll('party')
    party = soup_to_dict(parties, 'id', ['nm', 'ab', 's', 'id'])
    choices = soup.findAll('choice')
    choice = soup_to_dict(choices, 'id', ['nm', 'conid', 's', 'id'])

    return {'election': elect, 'areatype': atyp, 'area': area,
            'contest': contest, 'choice': choice, 'party': party}


def scrape_results(data):
    """
    Reads the contents of results.xml.
    This is the file that has all the changing information, so this is the
    method that should get run to update the values.

    """

    if OFFLINE:
        html = file("results.xml").read()
    else:
        try:
            html = urlopen("%sresults.xml" % BASE_URL)
        except URLError:
            return data
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


def sort_by_s(dict_to_sort):
    """
    Takes a dictionary of dictionaries where each inner dictionary has a
    sort value called s.  The function emits a new list sorted on s of the
    inner dictionaries.

    """

    return sorted(dict_to_sort.values(), key=itemgetter('s'))

# Output Methods
def print_tables(data_dict):
    """
    Writes out the election information to a readable text table.
    Exceedingly basic output.

    """

    for contest in sort_by_s(data_dict['contest']):
        print("\n%s %s/%s" % (contest['nm'], contest['bal'], contest['el']))
        for candidate in sort_by_s(data_dict['choice']):
            if candidate['conid'] == contest['id']:
                print("%s: %s" % (candidate['nm'], candidate['vot']))



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

        print "Writing file(s)."
        HTML = write_html(DATA)

        if not options.loop:
            break

        print "Sleeping for", options.interval, "seconds"
        sleep(float(options.interval))
