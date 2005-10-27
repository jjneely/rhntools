#!/usr/bin/python

import sys
from rhnapi import RHNClient
import rhndb
import pysqlite
import config

def main():

    dbcfg = config.DBConfig()

    rhn = RHNClient("https://rhn.linux.ncsu.edu/rpc/api")
    rhn.connect()

    sdb = pysqlite.PySqliteDB(dbcfg)
    db = rhndb.RHNStore(sdb)

    populate(db, rhn)

def populate(db, rhn):
    group_tally = {}
    ungrouped = []
    clients = []
    systems = rhn.server.system.list_user_systems(rhn.session)
    c = 0

    for system in systems:
        sys.stderr.write("Working on: %s\n" % system["name"])
        clientid = db.addSystem(system)
        subscribedTo = []
        clients.append(clientid)

        c = c + 1
        grps = rhn.server.system.list_groups(rhn.session, system["id"])
        flag = 0
    
        for grp in grps:
            groupid = db.addGroup(grp)
            name = grp["system_group_name"]
            if grp["subscribed"] > 0:
                flag = 1
                subscribedTo.append(groupid)
                if group_tally.has_key(name):
                    group_tally[name] = group_tally[name] + 1
                else:
                    group_tally[name] = 1

        if not flag:
            ungrouped.append(system)

        db.subscribeGroup(clientid, subscribedTo)

    db.markActive(clients)
    db.commit()

    # Print out the group_tally nicely
    for key in group_tally.keys():
        print "%s: %s" % (key, group_tally[key])

    print "Ungrouped Systems:"
    for system in ungrouped:
        print "   %s" % system["name"]

    print "Total Systems: " + str(c)


if __name__ == "__main__":
    main()

