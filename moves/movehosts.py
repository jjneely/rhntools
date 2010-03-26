#!/usr/bin/python

# Move hosts from one RHN Organization to another.

# The from user must be an OrgAdmin or Satellite Admin capable of
# initiating the move (the org.migrateSystems API call).
#
# The destination user must be a RHN user that has access to where
# the hosts are moving to.  Perhaps the OrgAdmin of the new Organization.
# This is used to set channels, groups, and entitlements on the
# moved host.
#
# This script assumes the same group names, channels, and entitlements
# exist in the new organization.  See the clonegroups.py script for
# moving over sets of groups.

import sys
import optparse
import getpass
import re

sys.path.insert(0, "../")

from rhnapi import RHNClient

def getSysIDs(rhn, exp=None):
    hosts = []
    if exp is not None:
        regex = re.compile(exp)

    r = rhn.server.system.listSystems(rhn.session)
    for i in r:
        if exp is not None and regex.search(i['name']) is None:
            continue
        hosts.append(int(i['id']))

    return hosts

def getHostDetail(rhn, sysid):
    ret = {}
    ret['name'] = rhn.server.system.getName(rhn.session, sysid)['name']
    ret['id'] = sysid
    ret['entitlements'] = rhn.server.system.getEntitlements(rhn.session, sysid)
    ret['base'] = rhn.server.system.getSubscribedBaseChannel\
                  (rhn.session, sysid)['label']
    ret['child'] = []
    ret['groups'] = []

    for i in rhn.server.system.listSubscribedChildChannels(rhn.session, sysid):
        ret['child'].append(i['label'])

    for i in rhn.server.system.listGroups(rhn.session, sysid):
        if int(i['subscribed']) == 1:
            ret['groups'].append(i)

    return ret

def setHostDetail(rhn, d):
    print "Setting details for %s..." % d['name']
    id = d['id']
    sys.stdout.write("Entitlements...")
    rhn.server.system.upgradeEntitlement(rhn.session, id, d['entitlements'][0])
    sys.stdout.write("BaseChannel...")
    rhn.server.system.setBaseChannel(rhn.session, id, d['base'])
    sys.stdout.write("ChildChannels...")
    rhn.server.system.setChildChannels(rhn.session, id, d['child'])
    sys.stdout.write("Groups...")

    # We have to look up the groups in the new Org and map their IDs to
    # the old group names.  Keying off the same group name.
    groups = {}
    for i in rhn.server.systemgroup.listAllGroups(rhn.session):
        groups[i['name']] = i['id']
    for i in d['groups']:
        if i['system_group_name'] in groups:
            gid = groups[i['system_group_name']]
            rhn.server.system.setGroupMembership(rhn.session, id, gid, 1)
        else:
            print "Error (NOT HALTING): Can't find group %s" \
                  % i['system_group_name']
    sys.stdout.write("\n")


def main():
    parser = optparse.OptionParser()
    parser.add_option("", "--url", action="store", default=None,
            dest="url", help="RHN URL: https://foo.bar/rpc/api")
    parser.add_option("", "--fuser", action="store", default=None,
            dest="fuser", help="From RHN user")
    parser.add_option("", "--tuser", action="store", default=None,
            dest="tuser", help="Destination RHN user")
    parser.add_option("", "--fpass", action="store", default=None,
            dest="fpass", help="From RHN password")
    parser.add_option("", "--tpass", action="store", default=None,
            dest="tpass", help="Destination RHN password")
    parser.add_option("", "--orgid", action="store", default=None,
            dest="orgid", type="int", help="New RHN Org ID")
    parser.add_option("-i", "--include", action="store", default=None,
            dest="include", help="Regular Expression of groups to include")

    opts, args = parser.parse_args(sys.argv)

    for i in ["url", "fuser", "tuser", "orgid"]:
        if getattr(opts, i) is None:
            print "The URL, OrgID, and usernames are required."
            print
            parser.print_help()
            sys.exit(1)

    if opts.fpass is None:
        opts.fpass = getpass.getpass("From RHN Password: ")

    if opts.tpass is None:
        opts.tpass = getpass.getpass("Destination RHN Password: ")

    print "Connecting with the 'from' RHN account..."
    fRHN = RHNClient(opts.url)
    fRHN.connect(opts.fuser, opts.fpass)
    print "Connecting with the 'to' RHN account..."
    tRHN = RHNClient(opts.url)
    tRHN.connect(opts.tuser, opts.tpass)

    hosts = getSysIDs(fRHN, opts.include)
    for i in hosts:
        detail = getHostDetail(fRHN, i)
        try: 
            fRHN.server.org.migrateSystems(fRHN.session, opts.orgid, [i])
        except:
            print "Migration of %s failed, shutting down..." % detail['name']
            raise
        print "%s migrated..." % detail['name']
        try:
            setHostDetail(tRHN, detail)
        except:
            print "Error setting host details for %s, halting..." \
                   % detail['name']
            raise
    

    print "Done!"

if __name__ == "__main__":
    main()

