
class RHNStore(object):
    
    def __init__(self, sdb):
        self.sdb = sdb
        self.conn = self.sdb.getConnection()
        self.c = self.sdb.getCursor()
    
    def addSystem(self, system):
        q1 = """select clientid from CLIENTS where rhnsid = %s"""
        q2 = """insert into CLIENTS (rhnsid, name, lastcheckin) values
                (%s, %s, %s)"""
        q3 = """update CLIENTS set lastcheckin = %s where clientid = %s"""

        self.c.execute(q1, (system["id"],))
        ret = self.c.fetchone()

        if ret == None:
            self.c.execute(q2, (system["id"], system["name"],
                                system["last_checkin"]))
        else:
            self.c.execute(q3, (system["last_checkin"], ret[0][0]))
            
        self.conn.commit()

