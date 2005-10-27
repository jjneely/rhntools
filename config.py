import ConfigParser

class Configuration(object):

    type = ""

    def __init__(self):
        self.cfg = ConfigParser.ConfigParser()
        files = self.cfg.read(['rhn.conf'])

        if files == None:
            raise Exception("Configuration file not found.")

    def get(self, key):
        return self.cfg.get(self.type, key)


class RHNConfig(Configuration):

    type = "rhn"

    def getURL(self):
        return self.get("url")

    def getUserName(self):
        return self.get("user")

    def getPassword(self):
        return self.get("password")
    

class DBConfig(Configuration):

    type = "db"
   
    def getDBType(self):
        return self.get("db_type")

    def DBFile(self):
        return self.get("db")

    #def ConfigDir(self):
    #    return self.get("configs")

