#!/usr/bin/python

import xmlrpclib
import sys
import getpass

class RHNClient(object):

    def __init__(self, serverURL):
        self.url = serverURL


    def connect(self):
        self.server = xmlrpclib.ServerProxy(self.url)
        user, pw = self.auth()
        self.session = self.server.auth.login(user, pw, 3600)


    def auth(self):
        sys.stdout.write("RHN User Name: ")
        id = sys.stdin.readline()
        id = id.strip()

        pw = getpass.getpass("RHN Password: ")

        return id, pw
        
