"""
This file is the new, updated HTML renderer for the election scraper.

It does cool javascripty things.  It aslo looks much better than my version.

author: Dave Silverman
author: Nathaniel Case

"""

from operator import itemgetter

HEADER = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
  <head>
	<script type="text/javascript" src="js/jquery.js"></script>
	<script type="text/javascript" src="js/jquery.progressbar.min.js"></script>
	<script type="text/javascript" src="js/election.js"></script>
  </head>
  <body>
      <a href="http://github.com/ralphbean/monroe-elections"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://d3nwyuy0nl342s.cloudfront.net/img/7afbc8b248c68eb468279e8c17986ad46549fb71/687474703a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f6461726b626c75655f3132313632312e706e67" alt="Fork me on GitHub"></a>
    <table>"""

FOOTER = """
      <tr><td width="30%">
        <div id="area"></div>
      </td><td colspan=2>
        <div id="contest"></div>
      </td></tr>
      <tr><td colspan=2>
        <a name='key'/>
        A blank ballot is a ballot which has been handed in with
        no votes recorded on it.<br/>

        An undervote occurs when the number of choices selected by a voter
        in a contest is less than the maximum number allowed for that
        contest or when no selection is made for a single choice
        contest. (Wikipedia)<br/>

        An overvote occurs when one votes for more than the maximum
        number of selections allowed in a contest. (Wikipedia)<br/>
      </td></tr>
    </table>
  </body>
</html>"""
BAR_TYPES = ['DEM', 'REP', 'GRN', 'LBT', 'CON', 'WOR', 'IND']

def write_html(data_dict):
    """This method gets called to build the HTML for the scraper."""

    text = [HEADER]
    text.extend(headers(data_dict['election'], data_dict['areatype']))
    text.append(FOOTER)
    container_file = open('index.html', 'w')
    container_file.writelines(text)
    container_file.close()

    text = areas(data_dict['areatype'], data_dict['area'], data_dict['contest'])
    area_file = open("area.html", 'w')
    area_file.writelines(text)
    area_file.close()

    text = write_contests(data_dict['contest'], data_dict['choice'], data_dict['party'])
    contest_file = open("contest.html", 'w')
    contest_file.writelines(text)
    contest_file.close()


def headers(election, areatypes):
    """Writes out election information to a basic HTML file."""

    text = ["<tr><td colspan=3><h1>Unofficial data for %s %s</h1></td></tr>\n" %\
             (election['jd'], election['des'])]
    text.append("<tr><td colspan=2 width='50%%'>")
    text.append("<ul style='list-style-type: none'>\n")
    for areatype in sort_by_s(areatypes):
        text.append("<li><a href='#' class='loadA' id='%s'>List of %s races</a><li/>" %
                 (areatype['id'], areatype['nm']))
    text.append("</ul>")
    text.append("<!--<a href='#contest' class='load'>List of all races in %s</a><br/>-->\n" %
             election['jd'])
    text.append("</td><td>")
    text.append("<h2>Reporting Precincts: %s/%s</h2>\n" %
             (election['clpol'], election['pol']))
    text.append("<h3>Last updated: %s</h3>\n" % election['ts'])
    text.append("Brought to you by <br><a href=\"http://foss.rit.edu\" target=\"_blank\"><img src=\"http://foss.rit.edu/files/logo.png\" alt=\"FOSS@RIT\" border=none></a>")
    text.append("</td></tr>")
    return text


def areas(areatypes, areas, contests):
    text = ["<a name='areas'/>\n"]
    for areatype in sort_by_s(areatypes):
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
        text.append("</table><br/>\n")
        text.append("</div>\n")
    return text


def write_contests(contests, choices, parties):
    text = ["<a name='contests'/>\n"]
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
