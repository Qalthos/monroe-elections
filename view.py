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

BAR_TYPES = {
    'DEM': 'democrat',
    'REP': 'republican',
    'GRN': 'green',
    'LBT': 'libertarian',
    'CON': 'conservative',
    'WF': 'workingfamilies',
    'WOR': 'workingfamilies',
    'IND': 'independence'
}

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


def write_json(election):
    json_filename = 'json/' + election['election']['nm']
    json_filename = json_filename.replace(' ', '-') + '.json'

    with open(json_filename, 'w') as f:
        f.write(json.dumps(election))

def write_html(county, county_data):
    """This method gets called to build the HTML for the scraper."""

    output_dir = os.path.join('html', county)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    text = update(county_data['election'], county_data['areatype'], county)
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


def tabs(key, name):
    with open('html/tabs.html', 'a') as tab_file:
        tab_file.write("<li class='tab'><a href='#' class='loadE' id='%s'>%s</a></li>\n" %
            (key, name))


def clear_tabs():
    with open('html/tabs.html', 'w') as tab_file:
        tab_file.write("")


def update(election, areatypes, county):
    """Writes out election information to a basic HTML file."""
    return """<img id='logo' src='data-submodule/{}/logo.jpg' />
              <h2>Reporting Precincts: {}/{} ({:0.1f}%)</h2>
              <h3>Last updated: {}</h3>""".format(
                county, election['clpol'], election['pol'],
                float(election['clpol'])/float(election['pol'])*100,
                election['ts'])


def area(areatypes, areas, contests):
    list_text = ["<ul>\n"]
    for areatype in sort_by_s(areatypes):
        list_text.append("<li>%s races<ul>\n" % areatype['nm'])

        for area in sort_by_s(areas):
            if area['atid'] == areatype['id']:
                if areatype['nm'] != area['nm']:
                    list_text.append("<li>%s<ul>\n" %
                             (area['nm']))
                for contest in sort_by_s(contests):
                    if contest['aid'] == area['id']:
                        list_text.append("<li><a href='#' class='loadC' id='%s'>%s</a></li>\n" %
                                 (contest['id'], contest['nm']))
                list_text.append('</ul></li>\n')
        list_text.append('</ul></li>\n')
    list_text.append("</ul>\n")
    return list_text


def contest(contests, choices, parties):
    text = list()
    text.append('<html><head><link rel="stylesheet" href="../../css/progress.css" type="text/css" /></head><body>')
    for contest in sort_by_s(contests):
        if contest['bal'] == 0:
            contest['bal'] = 1
        text.append("<a name='c%s' />\n" % contest['id'])
        text.append("<div id='c%s'>\n" % contest['id'])
        text.append("<table>\n")
        text.append("<tr><th colspan=5>%s</th></tr>\n" % contest['nm'])
        total_ballots = contest['bal']/100.0
        for choice in sort_by_s(choices):
            if choice['conid'] == contest['id']:
                if choice['e'] == "1":
                    winner = "*"
                else:
                    winner = ""

                party_class = 'OTHER'

                if len(choice['vot']) == 2:
                    # Get rid of 'tot' so we don't get confused
                    choice['vot'].pop('tot')
                    single_line = choice['vot'].popitem()
                    pid = single_line[0]
                    if parties[pid]['ab'].upper() in BAR_TYPES:
                        party_class = BAR_TYPES[parties[pid]['ab'].upper()]
                    total = single_line[1]
                    party = parties[pid]['nm']
                else:
                    total = choice['vot'].pop('tot')
                    party = "Total"
                text.append("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td><progress class='{3}' value={4} max=100 /> {4:.0f}%</td><td>{5}</td></tr>\n" \
                    .format(winner, choice['nm'], party, party_class,
                            total/total_ballots, total))
                party_list = sorted(choice['vot'], key=lambda pid: parties[pid]['s'])
                for party in party_list:
                    party_class = 'OTHER'
                    if parties[party]['ab'].upper() in BAR_TYPES:
                        party_class = BAR_TYPES[parties[party]['ab'].upper()]
                    text.append("<tr><td colspan=2/><td>{0}</td><td><progress class='{1}' value={2} max=100 /> {2:.0f}%</td><td>{3}</td></tr>\n" \
                        .format(parties[party]['nm'], party_class,
                            choice['vot'][party]/total_ballots,
                            choice['vot'][party]))
        text.append("<tr><td/><td colspan=3>Blank Ballots<a href='#key'>*</a></td><td>%s</td></tr>\n" % contest['bl'])
        text.append("<tr><td/><td colspan=3>Undervotes<a href='#key'>*</a></td><td>%s</td></tr>\n" % contest['uv'])
        text.append("<tr><td/><td colspan=3>Overvotes<a href='#key'>*</a></td><td>%s</td></tr>\n" % contest['ov'])
        text.append("</table><br/>\n")
        text.append("</div>\n")

    text.append('</body></html>')
    return text


def sort_by_s(dict_to_sort):
    """
    Takes a dictionary of dictionaries where each inner dictionary has a
    sort value called s.  The function emits a new list sorted on s of the
    inner dictionaries.

    """

    return sorted(dict_to_sort.values(), key=itemgetter('s'))
