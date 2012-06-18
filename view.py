"""
This file is the new, updated HTML renderer for the election scraper.

It does cool javascripty things.  It aslo looks much better than my version.

author: Dave Silverman
author: Nathaniel Case

"""

try:
    import simplejson as json
except ImportError:
    import json

import os
from operator import itemgetter

BAR_TYPES = ['DEM', 'REP', 'GRN', 'LBT', 'CON', 'WOR', 'IND']

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


def write_json(data_dict):
    json_filename = 'json/' + data_dict['election']['nm']
    json_filename = json_filename.replace(' ', '-') + '.json'

    with open(json_filename, 'w') as f:
        f.write(json.dumps(data_dict))

def write_html(data_dict):
    """This method gets called to build the HTML for the scraper."""
    with open('html/tabs.html', 'w') as tab_file:
        tab_file.writelines(tabs(data_dict.keys()))

    for county, county_data in data_dict.items():
        output_dir = os.path.join('html', county)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        text = update(county_data['election'], county_data['areatype'])
        with open(os.path.join(output_dir, 'update.html'), 'w') as update_file:
            update_file.writelines(text)

        text = area(county_data['areatype'], county_data['area'],
                    county_data['contest'])
        with open(os.path.join(output_dir, "area.html"), 'w') as area_file:
            area_file.writelines(text)

        text = contest(county_data['contest'], county_data['choice'],
                       county_data['party'])
        with open(os.path.join(output_dir, "contest.html"), 'w') as contest_file:
            contest_file.writelines(text)


def tabs(keys):
    retval = []
    for key in keys:
        retval.append("<td align='center'><a href='#' class='loadE' id='%s'>%s</a></td>\n" %
            (key, key))

    return retval


def update(election, areatypes):
    """Writes out election information to a basic HTML file."""
    return "<h2>Reporting Precincts: %s/%s</h2>\n<h3>Last updated: %s</h3>" % \
                (election['clpol'], election['pol'], election['ts'])


def area(areatypes, areas, contests):
    list_text = ["<ul id='list' style='list-style-type: none'>\n"]
    text = list()
    for areatype in sort_by_s(areatypes):
        list_text.append("<li><a href='#' class='loadA' id='%s'>List of %s races</a></li>\n" %
            (areatype['id'], areatype['nm']))
        text.append("<div id='a%s'>\n" % areatype['id'])
        text.append("<h3>%s Races</h3>\n" % areatype['nm'])
        text.append("<table>\n")
        for area in sort_by_s(areas):
            if area['atid'] == areatype['id']:
                if areatype['nm'] != area['nm']:
                    text.append("<tr><th align='left'>%s</th></tr>\n" %
                             (area['nm']))
                for contest in sort_by_s(contests):
                    if contest['aid'] == area['id']:
                        text.append("<tr><td><a href='#contest' class='loadC' id='%s'>%s</a></td></tr>\n" %
                                 (contest['id'], contest['nm']))
        text.append("</table>\n")
        text.append("</div>\n")
    list_text.append("</ul>\n")
    list_text.extend(text)
    return list_text


def contest(contests, choices, parties):
    text = list()
    for contest in sort_by_s(contests):
        if contest['bal'] == 0:
            contest['bal'] = 1
        text.append("<div id='c%s'>\n" % contest['id'])
        text.append("<table width='100%'>\n")
        text.append("<tr><th colspan=4>%s</th></tr>\n" % contest['nm'])
        total_ballots = contest['bal']/100.0
        for choice in sort_by_s(choices):
            if choice['conid'] == contest['id']:
                if choice['e'] == "1":
                    winner = "*"
                else:
                    winner = ""
                if len(choice['vot']) == 2:
                    choice['vot'].pop('tot')
                    single_line = choice['vot'].popitem()
                    pid = single_line[0]
                    party_class = 'OTHER'
                    if parties[pid]['ab'] in BAR_TYPES:
                        party_class = parties[pid]['ab']
                    text.append("<tr><td>%s</td><td>%s</td><td>%s</td><td class='%s'><span class='progressBar'>%s%%</span></td></tr>\n" %
                            (winner, choice['nm'], parties[pid]['nm'],
                             party_class, single_line[1]/total_ballots))
                else:
                    total = choice['vot'].pop('tot')
                    text.append("<tr><td>%s</td><td>%s</td><td>%s</td><td class='OTHER'><span class='progressBar'>%s%%</span></td></tr>\n" %
                            (winner, choice['nm'], "Total", total/total_ballots))
                party_list = sorted(choice['vot'], key=lambda pid: parties[pid]['s'])
                for party in party_list:
                    party_class = 'OTHER'
                    if parties[party]['ab'] in BAR_TYPES:
                        party_class = parties[party]['ab']
                    text.append("<tr><td colspan=2/><td>%s</td><td class='%s'><span class='progressBar'>%s%%</span></td></tr>\n" %
                             (parties[party]['nm'], party_class, choice['vot'][party]/total_ballots))
        text.append("<tr><td/><td colspan=2>Blank Ballots<a href='#key'>*</a></td><td>%s</td></tr>\n" % contest['bl'])
        text.append("<tr><td/><td colspan=2>Undervotes<a href='#key'>*</a></td><td>%s</td></tr>\n" % contest['uv'])
        text.append("<tr><td/><td colspan=2>Overvotes<a href='#key'>*</a></td><td>%s</td></tr>\n" % contest['ov'])
        text.append("</table><br/>\n")
        text.append("</div>\n")
    return text


def sort_by_s(dict_to_sort):
    """
    Takes a dictionary of dictionaries where each inner dictionary has a
    sort value called s.  The function emits a new list sorted on s of the
    inner dictionaries.

    """

    return sorted(dict_to_sort.values(), key=itemgetter('s'))
