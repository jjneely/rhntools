#!/usr/bin/python
#
# rhnstats.py - Generate db/web/csv statistics for RHN usage.
# Copyright (C) 2007 NC State University
# Written by Jack Neely <jjneely@ncsu.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys

# The rhnapi module is a directory above
sys.path.append("../")

from genshi.template import TemplateLoader
from rhnapi import RHNClient
import cPickle as pickle
import os.path
import config
import time
import optparse
import re

clients = {}
groups  = {}

def parseOpts():
    opts = optparse.OptionParser()
    opts.add_option("", "--csv", action="store_true", default=False,
                    dest="csv", help="Output in CSV Format")
    opts.add_option("", "--localdb", action="store_true", default=False, 
                    dest="localdb", help="Don't Query RHN")
    opts, args = opts.parse_args(sys.argv)
    return opts
        
def main():
    global clients, groups

    opts = parseOpts()
    dbcfg = config.DBConfig()
    rhncfg = config.RHNConfig()

    if opts.localdb and os.path.exists("rhnstats.db"):
        fd = open("rhnstats.db")
        clients, groups = pickle.load(fd)
        fd.close()
    else:
        rhn = RHNClient(rhncfg.getURL())
        rhn.connect(rhncfg.getUserName(), rhncfg.getPassword())

        populate(rhn)
        fd = open("rhnstats.db", "w")
        pickle.dump((clients, groups), fd, -1)
        fd.close()

    if opts.csv:
        print "Writing CSV file..."
        doCSV()
    else:
        doHTML()

def populate(rhn):
    global clients, groups
    systems = rhn.server.system.list_user_systems(rhn.session)

    for system in systems:
        #sys.stderr.write("Working on: %s\n" % system["name"])
        client = {}
        client["id"] = int(system["id"])
        client["name"] = system["name"]
        client["last_checkin"] = system["last_checkin"]
        subscribedTo = []

        # Sub Channels available for subscription, does not include
        # already subscribed sub channels.
        channels =  rhn.server.system.list_child_channels(rhn.session, 
                                                          system["id"])
        chanLabels = [ i['label'] for i in channels ]
        client["channels"] = chanLabels

        if len([ i for i in chanLabels if re.search("^realmlinux", i) ]) > 0:
            client["RL"] = True
        else:
            client["RL"] = False

        grps = rhn.server.system.list_groups(rhn.session, system["id"])
   
        client["subscribed"] = []
        for grp in grps:
            gid = int(grp["sgid"])
            if int(grp["subscribed"]) > 0:
                if gid not in groups:
                    groups[gid] = {"name" : grp["system_group_name"],
                                   "count": 0, 
                                   "rl"   : 0, }
                groups[gid]["count"] = groups[gid]["count"] + 1
                if client["RL"]:
                    groups[gid]["rl"] = groups[gid]["rl"] + 1

                client["subscribed"].append(gid)

        clients[client["id"]] = client

def doCSV():
    file = "rhn.csv"
    title = ["Name", "Number of Licenses", "Number of Realm Linux Clients",
             "Percentage of Total Licnese"]
    table = []

    total = len(clients)

    for gid in groups.keys():
        row = []
        row.append(groups[gid]["name"])
        row.append(groups[gid]["count"])
        row.append(groups[gid]["rl"])
        p = float(groups[gid]["count"]) / float(total)
        row.append(p * 100)

        table.append(row)

    table.sort(lambda x,y: cmp(x[0], y[0]))
    table.insert(0, title)

    fd = open(file, 'w')
    for row in table:
        for field in row:
            if field == row[0]:
                fd.write("%s" % field)
            else:
                fd.write(",%s" % field)
        fd.write("\n")

    fd.write("\nTotal Licenes,%s" % total)
    fd.close()
    
def doHTML():
    file = "rhn.phtml"
    templatefile = "template.genshi"
    loader = TemplateLoader([os.path.dirname(__file__)])
    template = loader.load(templatefile)

    table = []
    total = len(clients)
    totalRL = 0

    for gid in groups.keys():
        d = {}
        d["name"] = groups[gid]["name"]
        d["count"] = groups[gid]["count"]
        d["rlcount"] = groups[gid]["rl"]
        p = float(groups[gid]["count"]) / float(total)
        d["percent"] = p * 100
        
        table.append(d)
        totalRL = totalRL + groups[gid]["rl"]

    table.sort(lambda x,y: cmp(x["name"], y["name"]))

    stream = template.generate(
        total=total,
        totalrl = totalRL,
        table = table,
        date = time.strftime("%A %B %d %H:%M:%S %Z %Y"),
        )

    fd = open(file, 'w')
    fd.write(stream.render("xhtml"))
    fd.close()
    

if __name__ == "__main__":
    main()

