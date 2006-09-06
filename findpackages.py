#!/usr/bin/python

import os
import os.path
import config
from rhnapi import RHNClient

TreeLocation = "/export/trees"
PackageRoot = "/var/satellite/redhat"
PackageDirs = os.listdir(PackageRoot)

def findRPM(path):
    for dir in PackageDirs:
        if dir.startswith('.'):
            continue

        location = os.path.join(PackageRoot, dir, path)
        if os.path.exists(location):
            return location

    return None

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
            rpm = "%(package_name)s/%(package_version)s-%(package_release)s/%(package_arch_name)s/%(package_name)s-%(package_version)s-%(package_release)s.%(package_arch_name)s.rpm" % p
            srpm = "%(package_name)s/%(package_version)s-%(package_release)s/SRPMS/%(package_name)s-%(package_version)s-%(package_release)s.src.rpm" % p
            
            location = findRPM(rpm)
            source = findRPM(srpm)
            if location is None:
                print "Error: Could not find binary package: %s" % rpm
            else:
                buildTreeUsing(chan['channel_label'], location, source)

