#!/usr/bin/python

# findpackages.py - Generate Yum'able trees from the sat package store
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

import os
import os.path
import sys
import config
import string
from types import IntType, FloatType, StringType
from rhnapi import RHNClient

TreeLocation = "/var/satellite/yum"
PackageRoot = "/var/satellite/redhat"
PackageDirs = os.listdir(PackageRoot)

# Stolen from Yum
def stringToVersion(verstring):
    if verstring is None:
        return ('0', None, None)
    i = string.find(verstring, ':')
    if i != -1:
        try:
            epoch = string.atol(verstring[:i])
        except ValueError:
            # look, garbage in the epoch field, how fun, kill it
            epoch = '0' # this is our fallback, deal
    else:
        epoch = '0'
    j = string.find(verstring, '-')
    if j != -1:
        if verstring[i + 1:j] == '':
            version = None
        else:
            version = verstring[i + 1:j]
        release = verstring[j + 1:]
    else:
        if verstring[i + 1:] == '':
            version = None
        else:
            version = verstring[i + 1:]
        release = None
    return (epoch, version, release)

def match(string, unknown, epsilon = 0.0001):
    # Does the string evaluate to the unknown typed value close enough
    # to be equal?

    if isinstance(unknown, StringType):
        return string == unknown

    if isinstance(unknown, IntType):
        try: 
            i = int(string)
        except ValueError: 
            return False
        return unknown == i

    if isinstance(unknown, FloatType):
        try: 
            f = float(string)
        except ValueError: 
            return False
        return (f - epsilon) <= unknown <= (f + epsilon)

    print "Unknown package EVR value %s of type %s could not be matched to %s" \
            % (unknown, type(unknown), string)
    return False

def bruteForceFind(p):
    for dir in PackageDirs:
        if dir.startswith('.'):
            continue

        namedir = os.path.join(PackageRoot, dir, p['package_name'])
        if not os.path.exists(namedir):
            continue

        for evr in [os.path.basename(i) for i in os.listdir(namedir)]:
            e, v, r = stringToVersion(evr)
            print "EVR: (%s, %s, %s)" % (e, v, r)

            # Epoch
            if evr.find(':') == -1:
                # The evr directory doesn't contain the epoch field
                pass
            elif p['package_epoch'] == "" and e == "0":
                pass
            elif match(e, p['package_epoch']):
                pass
            else:
                continue

            # Version
            if not (match(v, p['package_version']) and
               match(r, p['package_release'])):
                continue

            # If we are here then we have a directory name that matched
            bindir = os.path.join(namedir, evr, p['package_arch_name'])
            srcdir = os.path.join(namedir, evr, 'SRPMS/')
            binpath = None
            srcpath = None

            # Okay, there should be ONE rpm file here
            if not os.access(bindir, os.R_OK):
                print "Directory not found: %s" % bindir
                print "Found packages but arch directory missing?"
                continue
            for file in os.listdir(bindir):
                if file.endswith("%(package_arch_name)s.rpm" % p):
                    binpath = os.path.join(bindir, file)
                    break

            # and one src rpm file
            if os.access(srcdir, os.R_OK):
                for file in os.listdir(srcdir):
                    if file.endswith("src.rpm"):
                        srcpath = os.path.join(srcdir, file)
                        break

            return binpath, srcpath
    
    print "Error:  Could not find packages: %s" % str(p)
    return None, None

#def findRPM(path):
#    for dir in PackageDirs:
#        if dir.startswith('.'):
#            continue
#
#        location = os.path.join(PackageRoot, dir, path)
#        if os.path.exists(location):
#            return location
#
#    return None

def buildTreeUsing(label, rpm, srpm):
    if rpm == None:
        return

    location = os.path.join(TreeLocation, label, 'RPMS', os.path.basename(rpm))
    dir, file = os.path.split(location)
    if not os.path.exists(dir):
        os.makedirs(dir, 0755)
    if not os.path.exists(location):
        os.symlink(rpm, location)

    if srpm == None:
        return
    location = os.path.join(TreeLocation, label, 'SRPMS', 
                            os.path.basename(srpm))
    dir, file = os.path.split(location)
    if not os.path.exists(dir):
        os.makedirs(dir, 0755)
    if not os.path.exists(location):
        os.symlink(srpm, location)
    
def main():
    rhncfg = config.RHNConfig()
    rhn = RHNClient(rhncfg.getURL())
    rhn.connect(rhncfg.getUserName(), rhncfg.getPassword())

    channels = rhn.server.channel.list_software_channels(rhn.session)

    for chan in channels:
        packages = rhn.server.channel.software.list_all_packages(rhn.session,
                                                  chan['channel_label'])

        for p in packages:
            #rpm, srpm = buildPath(p, False)
            #location = findRPM(rpm)
            #source = findRPM(srpm)
            #if location == None:
            #    rpm, srpm = buildPath(p, True)
            #    location = findRPM(rpm)
            #    source = findRPM(srpm)

            location, source = bruteForceFind(p)

            if location == None:
                print "Error: Could not find binary package:"
                print p
            else:
                buildTreeUsing(chan['channel_label'], location, source)

if __name__ == "__main__":
    main()

