#!/usr/bin/python

import sys
from rhnapi import RHNClient
import rhndb
import pysqlite
import config
import time
from simpletal import simpleTAL, simpleTALES

def main():

    dbcfg = config.DBConfig()
    rhncfg = config.RHNConfig()

    rhn = RHNClient(rhncfg.getURL())
    rhn.connect(rhncfg.getUserName(), rhncfg.getPassword())

    sdb = pysqlite.PySqliteDB(dbcfg)
    db = rhndb.RHNStore(sdb)

    populate(db, rhn)
    doHTML(db)

def populate(db, rhn):
    clients = []
    systems = rhn.server.system.list_user_systems(rhn.session)

    for system in systems:
        #sys.stderr.write("Working on: %s\n" % system["name"])
        clientid = db.addSystem(system)
        subscribedTo = []
        clients.append(clientid)

        grps = rhn.server.system.list_groups(rhn.session, system["id"])
        flag = 0
    
        for grp in grps:
            groupid = db.addGroup(grp)
            name = grp["system_group_name"]
            if grp["subscribed"] > 0:
                flag = 1
                subscribedTo.append(groupid)

        db.subscribeGroup(clientid, subscribedTo)

    db.markActive(clients)
    db.commit()

def doHTML(db):
    file = "rhn.phtml"
    templatefile = "template.html"
    table = []

    total = db.getTotalCount()

    for group in db.getGroups():
        d = {}
        d["name"] = db.getGroupName(group)
        d["count"] = db.getGroupCount(group)
        p = int(10000 * float(d["count"]) / float(total))
        d["percent"] = p / 100.0
        
        table.append(d)

    context = simpleTALES.Context()
    context.addGlobal("total", total)
    context.addGlobal("table", table)
    context.addGlobal("date", time.strftime("%A %B %d %H:%M:S %Z %Y"))

    template = simpleTAL.compileHTMLTemplate(open(templatefile))
    output = open(file, 'w')
    
    template.expand(context, output)
    output.close()
    

if __name__ == "__main__":
    main()

