#!/usr/bin/python

import sys
import xmlrpclib

s = xmlrpclib.ServerProxy("https://rhn.redhat.com/rpc/api")
print "RHN API Version: %s" % s.api.system_version()

session = s.auth.login('ncsurhel', 'Cfvls20', 1000)
print "Session ID = %s" % session

group_tally = {}
ungrouped = []
systems = s.system.list_user_systems(session)
c = 0

for system in systems:
    c = c + 1
    grps = s.system.list_groups(session, system["id"])
    flag = 0
    
    sys.stderr.write("Working on: %s\n" % system["name"])

    for grp in grps:
        name = grp["system_group_name"]
        if grp["subscribed"] > 0:
            flag = 1
            if group_tally.has_key(name):
                group_tally[name] = group_tally[name] + 1
            else:
                group_tally[name] = 1

    if not flag:
        ungrouped.append(system)

# Print out the group_tally nicely
for key in group_tally.keys():
    print "%s: %s" % (key, group_tally[key])

print "Ungrouped Systems:"
for system in ungrouped:
    print "   %s" % system["name"]

print "Total Systems: " + str(c)

