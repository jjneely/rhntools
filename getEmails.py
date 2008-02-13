#!/usr/bin/python

# getEmails.py - Find email address for each RHN account holder
# Copyright (C) 2008 NC State University
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
import optparse
from datetime import date
from rhnapi import RHNClient

def cliOptions():
    usage = "%prog <URL> [options]"
    parser = optparse.OptionParser(usage=usage)

    #parser.add_option("--noconfirm", action="store_true", default=False,
    #                  dest="noconfirm", 
    #                  help="Don't ask for delete confirmation.")

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

def search(rhn):
    ret = []
    users = rhn.server.user.list_users(rhn.session)

    for user in users:
        id = user['login']
        detail = rhn.server.user.getDetails(rhn.session, id)
        email = "%s %s <%s>" % (detail['first_names'], detail['last_name'],
                                detail['email'])
        ret.append(email)

    return ret

def main():

    print "Email Addresses of RHN Account Holders."

    o = cliOptions()

    rhn = RHNClient(o.server)
    rhn.connect()

    print "RHN API Version: %s" % rhn.server.api.system_version()
    print "Today's date = %s" % date.today().isoformat()
    print

    list = search(rhn)
    for s in list:
        print s


if __name__ == "__main__":
    main()

