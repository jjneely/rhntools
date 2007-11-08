#!/usr/bin/python

import sys
import xmlrpclib
import time
import optparse
from datetime import date
from datetime import timedelta
from rhnapi import RHNClient

def parseDate(s):
    tuple = time.strptime(s, "%Y-%m-%d")
    return date.fromtimestamp(time.mktime(tuple))

def cliOptions():
    usage = "%prog <URL> [options]"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-d", "--days", action="store", default=30,
                      type="int", dest="days", help="Your RHN server.")
    parser.add_option("--delete", action="store_true", default=False,
                      dest="delete", help="Delete these registrations from RHN")

    if len(sys.argv) == 1:
        parser.print_help()

    opts, args = parser.parse_args(sys.argv)

    if len(args) != 2:
        print "You must provide the URL to your RHN server."
        parser.print_help()
        sys.exit(1)

    # first arg is name of the program
    opts.server = args[1]
    return opts

def search(rhn, days):
    s = rhn.server
    delta = timedelta(days=days)
    today = date.today()
    oldsystems = []
    systems = s.system.list_user_systems(rhn.session)

    for system in systems:
        #sys.stderr.write("Working on: %s  ID: %s\n" % \
        #                 (system["name"], system["id"]))

        d = parseDate(system["last_checkin"])
        if today - delta > d:
            # This machine hasn't checked in
            oldsystems.append(system)

    return oldsystems

def delete(rhn, list):
    for server in list:
        print "Removing %s..." % server["name"]
        rhn.system.deleteSystems(int(server["id"]))

def main():

    print "Search and Destroy old RHN registrations."
    print

    o = cliOptions()

    rhn = RHNClient(o.server)
    rhn.connect()

    print "RHN API Version: %s" % rhn.server.api.system_version()
    print "Today's date = %s" % date.today().isoformat()
    print

    list = search(rhn, o.days)
    for s in list:
        print s["name"]

    print "There are %s inactive systems." % len(list)

    if o.delete:
        print "Going to delete these registrations.  Hit ^C to abort now!"
        time.sleep(5)
        delete(rhn, list)

if __name__ == "__main__":
    main()

