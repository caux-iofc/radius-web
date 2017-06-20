#!/usr/bin/env python

import os
import ConfigParser
import radiusclient
import sys

if len(sys.argv) != 5:
    raise SyntaxError("Usage: radiuscmd name mac device cardid")
c = ConfigParser.SafeConfigParser()
c.read(os.path.expanduser("~/.config/radiusclient"))

r = radiusclient.radiusDatabaseClient({
            "host":c.get("MySQL", "host"),
            "user":c.get("MySQL", "user"),
            "passwd":c.get("MySQL", "password"),
            "db":c.get("MySQL", "database"),
#            "table":c.get("MySQL", "table")
})
r.addUser(*sys.argv[1:])
