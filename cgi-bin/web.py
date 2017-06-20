#!/usr/bin/env python

import os
import cgi
import ConfigParser
import radiusclient
import sys

c = ConfigParser.SafeConfigParser()
c.read(os.path.expanduser("~/.config/radiusclient"))

r = radiusclient.radiusDatabaseClient({
            "host":c.get("MySQL", "host"),
            "user":c.get("MySQL", "user"),
            "passwd":c.get("MySQL", "password"),
            "db":c.get("MySQL", "database"),
#            "table":c.get("MySQL", "table"),
})

def tail():
    print "</body></html>\n"

def buildForm(formTuple):
    """Name, description, id, value"""
    for item in formTuple:
#        yield """<label>%s<span class="small">%s</span></label>
#                 <input type="text" name="%s" value="%s" />""" % item
        print >> sys.stderr, item[2]
        if item[2] == "role":
             yield """<label>%s<span class="small">%s</span></label>
                      <select name="%s"><option value="Normal" />Normal</option><option value="CSP student" />CSP student</option></select>%s""" % item
        else:
             yield """<label>%s<span class="small">%s</span></label>
                      <input type="text" name="%s" value="%s" />""" % item

    yield """<button type="submit" name="submit">Commit</button>"""

print """Content-Type: text/html

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
<link rel="stylesheet" type="text/css" href="/css/macaddr.css" />
<title>RADIUS database modification</title>
</head>
<body>
<div id="stylized" class="myform">"""

p = cgi.FieldStorage(keep_blank_values=True)
if p.has_key("last10"):
    print "<h2>last 10</h2>\n"
    print "<table border=1>"
    c = r.db.cursor()
    c.execute("select id, username as mac, who, number, device, role from radcheck order by number desc limit 10")
    for s in c:
        print "<tr>"
        for t in s:
            print "<td>" + str(t) + "</td>"
        print "<tr/>"
    print "</table>"
    tail()
    exit(0)
elif p.has_key("submit"):
    try:
        r.addUser(p.getvalue("name"), p.getvalue("macAddress"), p.getvalue("cardID"))
        print """<ul>
        <li>Name: %s</li>
        <li>MAC: %s</li>
        <li>Card ID: %s</li>
        </ul>
        <p>The above entry was accepted.</p>""" % (p.getvalue("name"), p.getvalue("macAddress"), p.getvalue("cardID"))
    except radiusclient.DatabaseError as e:
        print "<strong>ERROR:</strong><p>%s</p>" % e
        if p.getvalue("name") == "":
            raise SyntaxError("Name cannot be null.")
        if p.getvalue("device") == "":
            raise SyntaxError("Device cannot be null.")
        if not p.getvalue("cardID").isdigit():
            raise SyntaxError("Card ID must be numeric.")
        r.addUser(p.getvalue("name"), p.getvalue("macAddress"), p.getvalue("device"), p.getvalue("cardID"), p.getvalue("role"))
        print "<p>%s added successfully.</p>" % p.getvalue("name")
    except:
        print "<p>Error: %s</p>" % str(sys.exc_info()[1])

formComponents = (
    ("Name", "First name, then last", "name", ""),
    ("MAC", "The NIC identifier", "macAddress", ""),
    ("Card ID", "The card number", "cardID", r.getSuggestedCardID()),
    ("Device", "E.g. laptop or phone", "device", ""),
    ("Role", "User role","role", ""),
)

print """<form id="form" method="post"><h1>RADIUS database modification</h1><p>Authorisation for the "IOFC" network.</p>"""
print "\n".join(buildForm(formComponents))
print "<p><a href=\"web.py?last10=yes\">Last 10 addresses</a>.</p>\n"
 
print "</div></body></html>"
tail()
