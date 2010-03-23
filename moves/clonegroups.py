#!/usr/bin/python

# This lovely bit of code selects groups from one RHN server (or organization)
# and copies them to a new RHN server or organization.  It does not move
# profiles or registrations, just the groups.

import sys
import optparse
import getpass
import re

sys.path.insert(0, "../")

from rhnapi import RHNClient

def getGroups(rhn, exp=None):
    print "Regular Expression: %s" % exp
    groups = rhn.server.systemgroup.listAllGroups(rhn.session)
    ret = {}
    if exp is not None:
        regex = re.compile(exp)
    for i in groups:
        if exp is None or regex.search(i['name']) is not None:
            ret[i['name']] = i['description']

    return ret

def setGroups(rhn, groups):
    current = getGroups(rhn)

    keys = groups.keys()
    keys.sort()
    for i in keys:
        if i in current:
            print "Group %s already exists on the destination." % i
        else:
            print "Creating %s" % i
            rhn.server.systemgroup.create(rhn.session, i, groups[i])

def main():
    parser = optparse.OptionParser()
    parser.add_option("", "--furl", action="store", default=None,
            dest="furl", help="From RHN URL: https://foo.bar/rpc/api")
    parser.add_option("", "--turl", action="store", default=None,
            dest="turl", help="Destination RHN URL")
    parser.add_option("", "--fuser", action="store", default=None,
            dest="fuser", help="From RHN user")
    parser.add_option("", "--tuser", action="store", default=None,
            dest="tuser", help="Destination RHN user")
    parser.add_option("", "--fpass", action="store", default=None,
            dest="fpass", help="From RHN password")
    parser.add_option("", "--tpass", action="store", default=None,
            dest="tpass", help="Destination RHN password")
    parser.add_option("-i", "--include", action="store", default=None,
            dest="include", help="Regular Expression of groups to include")

    opts, args = parser.parse_args(sys.argv)

    for i in ["furl", "turl", "fuser", "tuser"]:
        if getattr(opts, i) is None:
            print "The from and destination URLs and usernames are required."
            print
            parser.print_help()
            sys.exit(1)

    if opts.fpass is None:
        opts.fpass = getpass.getpass("From RHN Password: ")

    if opts.tpass is None:
        opts.tpass = getpass.getpass("Destination RHN Password: ")

    fRHN = RHNClient(opts.furl)
    fRHN.connect(opts.fuser, opts.fpass)

    groups = getGroups(fRHN, opts.include)
    
    tRHN = RHNClient(opts.turl)
    tRHN.connect(opts.tuser, opts.tpass)

    setGroups(tRHN, groups)

    print "Done!"

if __name__ == "__main__":
    main()

