#!/usr/bin/env python3
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

import argparse
import asyncio
import os
import string

from bs4 import BeautifulSoup
import requests

from gitsupport import commit_all
from view import write_html, write_json, tabs, clear_tabs

BASE_URLS = {
    'monroe': 'http://enr.monroecounty.gov/',
    'suffolk': 'http://apps.suffolkcountyny.gov/boe/eleres/16pr/',
    'chautauqua': 'http://72.45.245.14/BOE/Results/',
    'orange': 'http://boe.co.orange.ny.us/',
}

BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
LOOP = asyncio.get_event_loop()


class Election(object):
    def __init__(self, county):
        self.county = county
        self.logo = None
        self.results = dict()
        self.filepath = os.path.join(BASE_DIR, "data-submodule", self.county)

        # Create storage directory if necessary
        if not os.path.exists(self.filepath):
            os.mkdir(self.filepath)

    async def initial_read(self):
        """
        Reads the contents of ElectionEvent.xml.
        This file should not change during the election, so should only need to be
        read once.

        In case results are not yet available, it also zeroes out data.

        """

        filename = await self.pull_file('ElectionEvent.xml')
        self.logo = await self.pull_file('logo.jpg')
        with open(filename) as file_:
            xml = file_.read()

        soup = BeautifulSoup(xml, 'lxml')

        election = soup.find('election')
        if not election:
            #Something went wrong... bailing.
            return

        self.results['election'] = {'nm': election['nm'], 'des': election['des'], \
            'jd': election['jd'], 'ts': election['ts'], 'pol': 0, 'clpol': 0}

        contests = soup.findAll('contest')
        self.results['contest'] = soup_to_dict(contests, 'id', ['nm', 'aid', 'el', 's', 'id'])
        seen_aids = set(map(lambda x: x['aid'], self.results['contest'].values()))

        areas = soup.findAll('area')
        self.results['area'] = soup_to_dict(areas, 'id', ['nm', 'atid', 'el', 's', 'id'])
        self.results['area'] = {k: v for k, v in self.results['area'].items() if k in seen_aids}
        seen_atids = set(map(lambda x: x['atid'], self.results['area'].values()))

        areatypes = soup.findAll('areatype')
        self.results['areatype'] = soup_to_dict(areatypes, 'id', ['nm', 's', 'id'])
        self.results['areatype'] = {k: v for k, v in self.results['areatype'].items() if k in seen_atids}

        parties = soup.findAll('party')
        self.results['party'] = soup_to_dict(parties, 'id', ['nm', 'ab', 's', 'id'])

        choices = soup.findAll('choice')
        self.results['choice'] = soup_to_dict(choices, 'id', ['nm', 'conid', 's', 'id'])

        tabs(self.county, ' '.join((self.results['election']['jd'],
                                    self.results['election']['des'])))

        return self

    async def scrape_results(self):
        """
        Reads the contents of results.xml.
        This is the file that has all the changing information, so this is the
        method that should get run to update the values.

        """

        filename = await self.pull_file('results.xml')
        with open(filename) as file_:
            xml = file_.read()

        soup = BeautifulSoup(xml, 'lxml')

        election = soup.find('results')
        self.results['election'].update({
            'ts': election['ts'],
            'clpol': election['clpol'],
            'pol': election['pol'],
            'fin': election['fin']
        })

        results = soup_to_dict(soup.findAll('area'), 'id', ['bal', 'vot', 'pol', 'clpol'])
        for id_ in results:
            try:
                self.results['area'][id_].update(results[id_])
            except KeyError:
                # We probably dropped it, so ignore.
                pass

        results = soup_to_dict(soup.findAll('contest'), 'id', ['bal', 'bl', 'uv', 'ov'])
        for id_ in results:
            self.results['contest'][id_].update(results[id_])

        results = soup_to_dict(soup.findAll('choice'), 'id', ['vot', 'e'])
        for id_ in results:
            self.results['choice'][id_].update(results[id_])

    async def pull_file(self, filename):
        """Pulls a file from a remote source and saves it to the disk."""
        url = "%s%s" % (BASE_URLS[self.county], filename)
        filepath = os.path.join(self.filepath, filename)

        try:
            future = LOOP.run_in_executor(None, requests.get, url)
            resp = await future
            if resp.status_code == 200 and resp.content:
                with open(filepath, 'wb') as out_file:
                    out_file.write(resp.content)
                commit_all(self.filepath)
        except requests.exceptions.ConnectionError:
            # Connection timed out, use the last one we have
            pass

        return filepath


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
                data[item[key]][value] = string.capwords(item.get(value, '0'))

    return data


async def scrape(election):
    print("Scraping results for %s county" % election.county)
    await election.scrape_results()

    print("Writing json.")
    write_json(election.results)

    print("Writing html.")
    write_html(election.county, election.results)


async def loop_or_not(county, options):
    election = Election(county)

    print("Reading data for %s" % county)
    await election.initial_read()

    if not election:
        return
    elif options.loop is False:
        await scrape(election)
    else:
        while True:
            await scrape(election)
            await asyncio.sleep(options.interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--loop", dest="loop",
                        action="store_true", default=False,
                        help="run in a loop (infinitely)")
    parser.add_argument("-i", "--interval", dest="interval",
                        default=120, type=int,
                        help="number of seconds to sleep between runs")
    options = parser.parse_args()
    clear_tabs()


    tasks = [
        asyncio.ensure_future(loop_or_not(county, options))
        for county in BASE_URLS
    ]
    LOOP.run_until_complete(asyncio.gather(*tasks))

    LOOP.close()


if __name__ == "__main__":
    main()
