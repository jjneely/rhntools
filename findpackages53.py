#!/usr/bin/python

# findpackages53.py - Generate flat directories of RPMs on a RHNSAT 5.3
# Copyright (C) 2010 NC State University
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

# Run this script on the RHN Satellite.  It will use the RHN API to
# learn about all the channels and packages and will create
# directories of <channel name>/RPMS that contain symlinks to the
# rpms in the /var/satellite/redhat store.  You can then run
# yum-arch/createrepo on the generated directories.

import os
import sys
import time
import os.path
import datetime
import config

from rhnapi import RHNClient

# Where do we build the symlink farm?
TreeLocation = "/var/satellite/yum/channels"
RPMFile = "%(name)s-%(version)s-%(release)s.%(arch_label)s.rpm"

def main():
    try:
        rhncfg = config.RHNConfig()
        rhn = RHNClient(rhncfg.getURL())
        rhn.connect(rhncfg.getUserName(), rhncfg.getPassword())
    except Exception:
        sys.stderr.write("%s: Error loading configuration\n"
                         % sys.argv[0])
        sys.exit(3)
    
    #print "RHN API Version: %s" % rhn.server.api.system_version()
    #print "Today's date = %s" % datetime.date.today().isoformat()
    #print

    if not os.path.isdir(TreeLocation):
        sys.stderr.write("%s: %s does not exist or is not a directory\n"
                         % (sys.argv[0], TreeLocation))
        sys.exit(1)

    # returns a list of dicts where 'label' and 'id' are interesting
    channels = rhn.server.channel.listAllChannels(rhn.session)

    for c in channels:
        report = True
        cLocation = os.path.join(TreeLocation, c['label'], 'RPMS')
        if not os.path.exists(cLocation):
            os.makedirs(cLocation, 0755)

        # Gives list of dicts with NVERA and id
        packages = rhn.server.channel.software.listLatestPackages(
                       rhn.session, c['label'])

        for p in packages:
            pfile = RPMFile % p
            sys.stderr.write("%s: %s\n" % (c['label'], pfile))
            target = os.path.join(cLocation, pfile)
            if os.path.isfile(target):
                # Looks like the RPM is already here
                # avoid calling getDetails()
                # XXX: Verify?
                continue

            # dict of many details, like 'path'
            # getDetails takes 0.5 seconds to return
            details = rhn.server.packages.getDetails(rhn.session, p['id'])
            abs = os.path.join('/var/satellite', details['path'])

            if not os.path.isfile(abs):
                sys.stderr.write("%s: %s does not exist\n" 
                                 % (sys.argv[0], abs))
                sys.stderr.write("%s: Are you running this on the Satellite?\n"
                                 % sys.argv[0])
                sys.exit(2)

            if details['file'] != pfile:
                sys.stderr.write("Warning: RPM names are weird: %s != %s\n"
                                 % (details['file'], pfile))

            target = os.path.join(cLocation, details['file'])
            if os.path.exists(target):
                # File already here skpi
                # XXX: Verify it?
                pass
            else:
                if report:
                    # Report what channels have changed
                    print c['label']
                    report = False
                try:
                    os.link(abs, target)
                except OSError:
                    os.symlink(abs, target)


if __name__ == "__main__":
    main()

