"""
This is the old, less fancy HTML renderer for the election scraper.

It has lots of information, but doesn't look very good.

author: Nathaniel Case

"""

from operator import itemgetter

HEADER = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
	<head>
		<script type="text/javascript" src="js/jquery.js"></script>
        <script type='text/javascript'>
        $(document).ready(function() {
          //ACCORDION BUTTON ACTION	
          $('tr.button').click(function() {
            $('tr.content').slideUp('slow');	
            //$(this).nextUntil('tr').slideDown('slow');
            $(this).next().slideDown('slow');
          });

          //HIDE THE DIVS ON PAGE LOAD	
          $("tr.content").hide();
        });
        </script>
	</head>
    <body>"""
FOOTER = """<a name='key'/>
A blank ballot is a ballot which has been handed in with no votes recorded on it.<br/>\n")
An undervote occurs when the number of choices selected by a voter in a contest is less than the maximum number allowed for that contest or when no selection is made for a single choice contest. (Wikipedia)<br/>\n")
An overvote occurs when one votes for more than the maximum number of selections allowed in a contest. (Wikipedia)<br/>\n")
</body>
</html>"""


def write_html(data_dict):
    """This method gets called to build the HTML for the scraper."""

    text = [HEADER]
    text.extend(headers(data_dict['election'], data_dict['areatype']))
    text.extend(areas(data_dict['areatype'], data_dict['area'], data_dict['contest']))
    text.extend(contests(data_dict['contest'], data_dict['choice'], data_dict['party']))
    text.append(FOOTER)
    
    container_file = open('post_index.html', 'w')
    container_file.writelines(text)
    container_file.close()
    
    
def headers(election, areatypes):
    """Writes out election information to a basic HTML file."""

    text = ["<h1>Unofficial data for %s %s</h1>\n" %\
             (election['jd'], election['des'])]
    text.append("Brought to you by <br><a href=\"http://foss.rit.edu\" target=\"_blank\"><img src=\"http://foss.rit.edu/files/logo.png\" alt=\"FOSS@RIT\" border=none></a>")
    text.append("<h2>Reporting Precincts: %s/%s</h2>\n" %
             (election['clpol'], election['pol']))
    text.append("<h3>Last updated: %s</h3>\n" % election['ts'])
    for areatype in sort_by_s(areatypes):
        text.append("<a href='#area%s'>List of %s races</a><br/>\n" %
                 (areatype['id'], areatype['nm']))
    text.append("<a href='#contests'>List of all races in %s</a><br/>\n" %
             election['jd'])
    return text


def areas(areatypes, areas, contests):
    text = ["<a name='areas'/>\n"]
    for areatype in sort_by_s(areatypes):
        text.append("<a name='area%s'/>\n" % areatype['id'])
        text.append("<h3>%s Races</h3>\n" % areatype['nm'])
        text.append("<table>\n")
        for area in sort_by_s(areas):
            if area['atid'] == areatype['id']:
                if areatype['nm'] != area['nm']:
                    text.append("<tr><th align='left'>%s</th></tr>\n" %
                             (area['nm']))
                for contest in sort_by_s(contests):
                    if contest['aid'] == area['id']:
                        text.append("<tr><td><a href='#%s'>%s</a></td></tr>\n" %
                                 (contest['id'], contest['nm']))
        text.append("</table><br/>\n")
    return text


def contests(contests, choices, parties):
    text = ["<a name='contests'/>\n"]
    for contest in sort_by_s(contests):
        text.append("<a name='%s'/>\n" % contest['id'])
        text.append("<table width='100%'>\n")
        text.append("<tr><th colspan=4>%s</th></tr>\n" % contest['nm'])
        for choice in sort_by_s(choices):
            if choice['conid'] == contest['id']:
                if choice['e'] == "1":
                    winner = "*"
                else:
                    winner = ""
                if len(choice['vot']) == 2:
                    choice['vot'].pop('tot')
                    single_line = choice['vot'].popitem()
                    text.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" %
                            (winner, choice['nm'], parties[single_line[0]]['nm'], single_line[1]))
                else:
                    row_class = ""
                    if len(choice['vot']) > 2:
                        row_class = " class='button'"
                    total = choice['vot'].pop('tot')
                    text.append("<tr%s><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" %
                            (row_class, winner, choice['nm'], "Total", total))
                party_list = sorted(choice['vot'], key=lambda pid: int(parties[pid]['s']))
                for party in party_list:
                    text.append("<tr class='content'><td colspan=2/><td>%s</td><td>%s</td></tr>\n" %
                             (parties[party]['nm'], choice['vot'][party]))
        text.append("<tr><td/><td colspan=2>Blank Ballots<a href='#key'>*</a></td><td>%s</td></tr>" % contest['bl'])
        text.append("<tr><td/><td colspan=2>Undervotes<a href='#key'>*</a></td><td>%s</td></tr>" % contest['uv'])
        text.append("<tr><td/><td colspan=2>Overvotes<a href='#key'>*</a></td><td>%s</td></tr>" % contest['ov'])
        text.append("</table><br/>\n")
    return text


def sort_by_s(dict_to_sort):
    """
    Takes a dictionary of dictionaries where each inner dictionary has a
    sort value called s.  The function emits a new list sorted on s of the
    inner dictionaries.

    """

    return sorted(dict_to_sort.values(), key=itemgetter('s'))
