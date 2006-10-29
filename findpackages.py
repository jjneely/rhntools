#!/usr/bin/python

import os
import os.path
import sys
import config
import string
from types import IntType, FloatType, StringType
from rhnapi import RHNClient

TreeLocation = "/export/trees"
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

def bruteForceFind(p):
    epsilon = 0.0001
    for dir in PackageDirs:
        if dir.startswith('.'):
            continue

        namedir = os.path.join(PackageRoot, dir, p['package_name'])
        if not os.path.exists(namedir):
            continue

        for evr in [os.path.basename(i) for i in os.listdir(namedir)]:
            e, v, r = stringToVersion(evr)

            # Epoch
            if evr.find(':') == -1:
                # The evr directory doesn't contain the epoch field
                pass
            elif p['package_epoch'] == "" and e in [0, "0", ""]:
                pass
            elif p['package_epoch'] == int(e):
                pass
            else:
                continue

            # Version
            if isinstance(p['package_version'], StringType):
                if v == p['package_version']:
                    pass
                else:
                    continue
            elif isinstance(p['package_version'], IntType):
                try: i = int(v)
                except ValueError: continue
                if p['package_version'] == i:
                    pass
                else:
                    continue
            elif isinstance(p['package_version'], FloatType):
                try: f = float(v)
                except ValueError: continue
                if f - epsilon <= p['package_version'] <= f + epsilon:
                    pass
                else:
                    continue

            # Release
            if isinstance(p['package_release'], StringType):
                if r == p['package_release']:
                    pass
                else:
                    continue
            elif isinstance(p['package_release'], IntType):
                try: i = int(r)
                except ValueError: continue
                if p['package_release'] == i:
                    pass
                else:
                    continue
            elif isinstance(p['package_release'], FloatType):
                try: f = float(r)
                except ValueError: continue
                if f - epsilon <= p['package_release'] <= f + epsilon:
                    pass
                else:
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

