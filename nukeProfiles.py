#!/usr/bin/python

# nukeProfiles.py - find matching profiles by regex and optionally delete
# Copyright (C) 2009 NC State University
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
import optparse
import time
from datetime import date
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

def cliOptions():
    usage = "%prog <URL> regex [regex [...]]"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("--delete", action="store_true", default=False,
                      dest="delete", 
                      help="Delete these registrations from RHN.")
    parser.add_option("--noconfirm", action="store_true", default=False,
                      dest="noconfirm", 
                      help="Don't ask for delete confirmation.")

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    opts, args = parser.parse_args(sys.argv)

    # first arg is name of the program
    opts.server = args[1]
    opts.regexs = args[2:]
    return opts

def search(rhn, regexs):
    s = rhn.server
    oldsystems = []
    REs = []
    systems = s.system.list_user_systems(rhn.session)

    for s in regexs:
        try:
            ex = re.compile(s)
        except re.error:
            print "Regular expression error: %s" % s
            sys.exit(1)
        REs.append(ex)

    for system in systems:
        for ex in REs:
            if ex.match(system['name']) is not None:
                oldsystems.append(system)
                continue

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

def main():

    print "Search and Destroy RHN Profiles"
    print

    o = cliOptions()

    rhn = RHNClient(o.server)
    rhn.connect()

    print "RHN API Version: %s" % rhn.server.api.system_version()
    print "Today's date = %s" % date.today().isoformat()
    print

    list = search(rhn, o.regexs)
    for s in list:
        print "Profile: %s \t\tID: %s" % (s["name"], s['id'])

    print "There are %s matching profiles" % len(list)

    if o.delete:
        print "Going to delete these registrations.  Hit ^C to abort now!"
        time.sleep(5)
        delete(rhn, list, o.noconfirm)

if __name__ == "__main__":
    main()

