#!/usr/bin/env python

import MySQLdb

class DatabaseError(Exception):
    pass

class radiusDatabaseClient():
    def __init__(self, databaseLoginInfo):
        self.databaseLoginInfo = databaseLoginInfo
        self.openDatabase(self.databaseLoginInfo)

    def openDatabase(self, databaseLoginInfo):
        self.db = MySQLdb.connect(**databaseLoginInfo)

    def isValidMacAddress(self, macAddress):
        """Expects a MAC address with no separators."""
        return len(set(macAddress).difference(set("0123456789ABCDEFabcdef"))) == 0 and len(macAddress) == 12

    def isPresentMacAddress(self, macAddress):
        """Checks if a MAC address is already in the database."""
        c = self.db.cursor()
        c.execute("SELECT * FROM radcheck WHERE UserName = %s", 
                  self.db.escape_string(macAddress)) 
        return c.rowcount > 0
    
    def sanitiseMacAddress(self, macAddress):
        return macAddress.replace("-", "").replace(":", "")

    def desanitiseMacAddress(self, macAddress):
        return "-".join(macAddress[i:i+2] for i in xrange(0, len(macAddress), 2))

    def getSuggestedCardID(self):
        c = self.db.cursor()
        c.execute("SELECT MAX(Number) FROM radcheck")
        returnData = c.fetchone()[0]
        if returnData == None:
            return 0
        return int(returnData) + 1

    def getQuoting(self, data):
        if type(data) == type("a"):
            return "'%s'" % data
        return data

    def addToTable(self, tableName, dataTuple):
        c = self.db.cursor()
        c.execute("INSERT INTO %s (%s) VALUES (%s)" % (
                  self.db.escape_string(tableName),
                  ",".join(self.db.escape_string(x[0]) for x in dataTuple),
                  ",".join(self.getQuoting(self.db.escape_string(x[1])) for x in dataTuple)))
        self.db.commit()

    def addUser(self, name, macAddress, cardID):
        macAddress = self.sanitiseMacAddress(macAddress)
        if not cardID.isdigit():
            raise ValueError("Invalid card ID.")
        if not self.isValidMacAddress(macAddress):
            raise DatabaseError("MAC address not valid.")
        if self.isPresentMacAddress(self.desanitiseMacAddress(macAddress)):
            raise DatabaseError("MAC address already present in database.")
        self.addToTable("radcheck", (
                ("UserName", "%s" % self.desanitiseMacAddress(macAddress)),
                ("Attribute", "User-Name"),
                ("Value", "%s" % self.desanitiseMacAddress(macAddress)),
                ("op", ":="),
                ("Who", name),
                ("Number", cardID)
            ))
        self.db.commit()
