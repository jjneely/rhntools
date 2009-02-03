#!/usr/bin/python

# oldSystems.py - Find and possibly remove inactive systems from RHN
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

import re
import sys
import xmlrpclib
import time
import types
import optparse
from sets import Set
from datetime import date
from datetime import timedelta
from rhnapi import RHNClient

# Stolen from Yum
# Copyright 2005 Duke University
def userconfirm():
    """gets a yes or no from the user, defaults to No"""

    while True:            
        choice = raw_input('Is this ok [y/N]: ')
        choice = choice.lower()
        if len(choice) == 0 or choice[0] in ['y', 'n']:
            break

    if len(choice) == 0 or choice[0] != 'y':
        return False
    else:            
        return True
# end stealage

def parseDate(s):
    if isinstance(s, types.StringType):
        tuple = time.strptime(s, "%Y-%m-%d")
    else:
        # RHN's version of ISO8601: 20080924T14:28:37
        tuple = time.strptime(s.__str__(), '%Y%m%dT%H:%M:%S')

    return date.fromtimestamp(time.mktime(tuple))

def cliOptions():
    usage = "%prog <URL> [options]"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-d", "--days", action="store", default=30,
                      type="int", dest="days", help="Your RHN server.")
    parser.add_option("-e", "--exclude", action="store", default=None,
                      type="string", dest="exclude",
                      help="Regex of groups to ingore.")
    parser.add_option("--delete", action="store_true", default=False,
                      dest="delete", 
                      help="Delete these registrations from RHN.")
    parser.add_option("--noconfirm", action="store_true", default=False,
                      dest="noconfirm", 
                      help="Don't ask for delete confirmation.")

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

def getGroups(rhn, serverid):
    groups = rhn.server.system.listGroups(rhn.session, serverid)
    list = []

    for group in groups:
        if int(group['subscribed']) != 0:
            list.append(group['system_group_name'])

    return list

def search(rhn, days, excludes):
    s = rhn.server
    delta = timedelta(days=days)
    today = date.today()
    oldsystems = []
    systems = s.system.list_user_systems(rhn.session)

    for system in systems:
        if len(excludes) > 0:
            subed = getGroups(rhn, int(system['id']))
            intersection = Set(subed).intersection(excludes)
            if len(intersection) > 0:
                print "Excluding system: %s" % system['name']
                continue

        d = parseDate(system["last_checkin"])
        if today - delta > d:
            # This machine hasn't checked in
            oldsystems.append(system)

    return oldsystems

def delete(rhn, list, noconfirm=False):
    for server in list:
        print "Removing %s..." % server["name"]
        if noconfirm or userconfirm():
            ret = rhn.server.system.deleteSystems(rhn.session,
                                                  int(server["id"]))
            if ret != 1:
                print "Removing %s failed with error code: %s" % \
                        (server["name"], ret)
        else:
            print "Skipping %s" % server["name"]

def findGroups(rhn, regex):
    # Return groups that match regex
    # We do this by grabbing a registered system and listing its groups.
    # this gives us a list of all groups and if the system is subscribed
    # from which we build a new list of names that match the regex.

    systems = rhn.server.system.list_user_systems(rhn.session)
    if len(systems) == 0:
        raise StandardError("No systems subscribed to RHN.")

    groups = rhn.server.system.listGroups(rhn.session, int(systems[0]['id']))
    list = []
    for group in groups:
        match = regex.match(group['system_group_name'])
        if match != None:
            list.append(group['system_group_name'])

    return list

def main():

    print "Search and Destroy old RHN registrations."
    print

    o = cliOptions()

    rhn = RHNClient(o.server)
    rhn.connect()

    print "RHN API Version: %s" % rhn.server.api.system_version()
    print "Today's date = %s" % date.today().isoformat()
    print

    if o.exclude:
        try:
            regex = re.compile(o.exclude)
            excludes = findGroups(rhn, regex)
        except re.error:
            print "Regular expression error: %s" % o.exclude
            sys.exit(1)
        print "Excluding Groups: %s" % excludes
    else:
        excludes = []


    list = search(rhn, o.days, excludes)
    for s in list:
        print s["name"]

    print "There are %s inactive systems." % len(list)

    if o.delete:
        print "Going to delete these registrations.  Hit ^C to abort now!"
        time.sleep(5)
        delete(rhn, list, o.noconfirm)

if __name__ == "__main__":
    main()

