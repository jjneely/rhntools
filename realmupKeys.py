# This never worked because I use the RHN Satellite Default as the base
# channel for my keys.  The API kept tossing exceptions about the base
# channel of the child channel I was adding has not been added
#
# Error: <Fault -211: 'redstone.xmlrpc.XmlRpcFault: Key has not been assigned base channel for RHEL Client Supplementary (v. 6 for 64-bit x86_64)'>


from rhnapi import RHNClient
from datetime import date

import xmlrpclib
import optparse
import sys

flagchan = 'realmlinux-server5-i386'
channels = [
        'realmlinux-workstation6-i386',
        'realmlinux-workstation6-x86_64',
        'realmlinux-server6-i386',
        'realmlinux-server6-x86_64',

        'rhel-i386-client-optional-6',
        'rhel-i386-client-supplementary-6',
        'rhel-i386-server-optional-6',
        'rhel-i386-server-supplementary-6',
        'rhel-i386-workstation-optional-6',
        'rhel-i386-workstation-supplementary-6',

        'rhel-x86_64-client-optional-6',
        'rhel-x86_64-client-supplementary-6',
        'rhel-x86_64-server-optional-6',
        'rhel-x86_64-server-supplementary-6',
        'rhel-x86_64-workstation-optional-6',
        'rhel-x86_64-workstation-supplementary-6',
        ]

baseChannels = [
        'rhel-i386-client-6',
        'rhel-x86_64-client-6',
        'rhel-i386-server-6',
        'rhel-x86_64-server-6',
        'rhel-i386-workstation-6',
        'rhel-x86_64-workstation-6',
        ]

def cliOptions():
    usage = "%prog <URL> [options]"
    parser = optparse.OptionParser(usage=usage)

#    parser.add_option("-d", "--days", action="store", default=30,
#                      type="int", dest="days", help="Your RHN server.")
#    parser.add_option("-i", "--include", action="store", default=None,
#                      type="string", dest="include",
#                      help="Regex of groups to include. Conflicts with -e")
#    parser.add_option("-e", "--exclude", action="store", default=None,
#                      type="string", dest="exclude",
#                      help="Regex of groups to exclude. Conflicts with -i")
#    parser.add_option("--delete", action="store_true", default=False,
#                      dest="delete", 
#                      help="Delete these registrations from RHN.")
#    parser.add_option("--noconfirm", action="store_true", default=False,
#                      dest="noconfirm", 
#                      help="Don't ask for delete confirmation.")

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    opts, args = parser.parse_args(sys.argv)

    # first arg is name of the program
    opts.server = args[1]
    return opts


def main():
    o = cliOptions()

    rhn = RHNClient(o.server)
    rhn.connect()

    print "RHN API Version: %s" % rhn.server.api.system_version()
    print "Today's date = %s" % date.today().isoformat()
    print

    for i in rhn.server.activationkey.listActivationKeys(rhn.session):
        print "Key: %s (%s)" % (i['description'], i['key'])
        if flagchan in i['child_channel_labels']:
            print "   A RealmLinux Key"
            for c in channels:
                if c not in i['child_channel_labels']:
                    print "   Adding sub-channel: %s" % c
                    try:
                        rhn.server.activationkey.addChildChannels(rhn.session,
                            i['key'], [c])
                    except xmlrpclib.Fault, e:
                        print "   Error: %s" % str(e)
            sys.exit()



if __name__ == '__main__':
    main()

