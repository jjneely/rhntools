import pickle
import xmlrpclib
import string
import sys
import getpass

# Generated via the getRealmHosts.py script
hosts = pickle.loads(open("hosts.pic").read())

server = xmlrpclib.ServerProxy("https://rhn.linux.ncsu.edu/rpc/api")
print "RHN API Version: %s" % server.api.system_version()

sys.stdout.write("RHN Username: ")
userid = sys.stdin.readline().strip()
pw = getpass.getpass("RHN Password: ")

session = server.auth.login(userid, pw, 3600)
print "Session ID = %s" % session

list = server.system.list_user_systems(session)
print "We have %s systems in RHN" % len(list)
print "We have %s systems to Realm-ize" % len(hosts)

systems = {}
for i in list:
    systems[i['name']] = i['id']

#print server.system.list_child_channels(session, systems['anduril.pams.ncsu.edu'])

for host in hosts:
    print "\nProcessing %s..." % host

    if systems.has_key(host):
        sid = systems[host]
        chans = server.system.list_child_channels(session, sid)
    elif systems.has_key(string.split(host, '.')[0]):
        sid = systems[string.split(host, '.')[0]]
        print "Trying alternate name: %s" % string.split(host, '.')[0]
        chans = server.system.list_child_channels(session, sid)
    else:
        print "WARNING: %s not found in RHN" % host
        continue

    print "Found Host: %s" % host

    chan = ""
    cid = ""
    for c in chans:
        if c['LABEL'] in ['realmlinux-ws3',
                          'realmlinux-as3',
                          'realmlinux-as4',
                          'realmlinux-ws4',
                          'realmlinux-as3-amd64',
                          'realmlinux-ws3-amd64',
                          'realmlinux-ws4-amd64',
                          'realmlinux-as4-amd64']:
            chan = c['LABEL']
            cid = c['ID']
    
    if chan == "":
        print "Realm Linux channel already set for: %s" % host
        continue
    
    print "Setting sub-channels of %s to %s, %s" % (host, chan, cid)
    ret = server.system.set_child_channels(session, sid, cid)
    print "RHN Returned %s" % ret
    
