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
    

class DBConfig(Configuration):

    type = "db"
   
    def getDBType(self):
        return self.get("db_type")

    def DBFile(self):
        return self.get("db")

    #def ConfigDir(self):
    #    return self.get("configs")

