#!/usr/bin/python

import xmlrpclib
import sys
import getpass

class RHNClient(object):

    def __init__(self, serverURL):
        self.url = serverURL


    def connect(self, user=None, password=None):
        self.server = xmlrpclib.ServerProxy(self.url)
        if user == None or password == None:
            user, password = self.auth()
            
        self.session = self.server.auth.login(user, password, 3600)


    def auth(self):
        sys.stdout.write("RHN User Name: ")
        id = sys.stdin.readline()
        id = id.strip()

        pw = getpass.getpass("RHN Password: ")

        return id, pw
        
