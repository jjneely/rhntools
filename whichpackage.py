#!/usr/bin/python

# whichpackage.py -- Find the latest EVR of a RHN package
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
import os
import xmlrpclib
import optparse
import config
from rhnapi import RHNClient

def cliOptions():
    usage = "%prog <URL> [options]"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-c", "--channel", action="store", default=None,
                      dest="channel", 
                      help="RHN Channel to Search")
    parser.add_option("-p", "--package", action="store", default=None,
                      dest="package", 
                      help="A Package Name")
    parser.add_option("-C", "--config", action="store", default=None,
                      dest="config", 
                      help="Config file location")
    parser.add_option("-d", "--download", action="store_true", default=False,
                      dest="download", 
                      help="Download This Package")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    opts, args = parser.parse_args(sys.argv)

    if len(args) != 2 and opts.config == None:
        print "You must provide the URL to your RHN server."
        parser.print_help()
        sys.exit(1)

    if opts.channel == None:
        print "You must provide a channel to search."
        parser.print_help()
        sys.exit(1)
    if opts.package == None:
        print "You must provide a package name."
        parser.print_help()
        sys.exit(1)

    if opts.config == None:
        # first arg is name of the program
        opts.server = args[1]
    return opts

def whichPackage(rhn, chan, pkg):
    packages = rhn.server.channel.software.listLatestPackages(rhn.session,
                                                              chan)

    ret = []
    for p in packages:
        if p['package_name'] == pkg:
            if p['package_epoch'] == ' ':
                p['package_epoch'] = '0'
            ret.append((p['package_epoch'], p['package_version'],
                        p['package_release'], p['package_arch_label']))

    return ret

def main():

    cfg = None
    rhn = None
    o = cliOptions()

    if o.config != None:
        if not os.access(o.config, os.R_OK):
            print "Cannot read config: %s" % o.config
            sys.exit(2)

        cfg = config.RHNConfig(o.config)
        rhn = RHNClient(cfg.getURL())
        rhn.connect(cfg.getUserName(), cfg.getPassword())
    else:
        rhn = RHNClient(o.server)
        rhn.connect()

    for tuple in whichPackage(rhn, o.channel, o.package):
        print "%s %s %s %s" % tuple


if __name__ == "__main__":
    main()

