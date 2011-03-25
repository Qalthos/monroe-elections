#!/usr/bin/env python2

from BeautifulSoup import BeautifulStoneSoup
from urllib2 import urlopen

base = "http://www.london.ca/elections/results/"
# base = "http://66.192.47.50"

text = urlopen("results.xml")
name_text = urlopen("ElectionEvent.xml")

soup = BeautifulStoneSoup(text)
names = BeautifulStoneSoup(name_text)

contests = soup.findAll('contest')
contest_names = names.findAll('contest')
choices = soup.findAll('choice')
choice_names = names.findAll('choice')

for contest in contest_names:
    print "\n%s" % contest['nm']
    for choice in choices:
        for choice2 in choice_names:
            if choice2['conid'] == contest['id'] and choice2['id'] == choice['id']:
                print choice2['nm'], choice['vot']
