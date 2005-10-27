
class RHNStore(object):
    
    def __init__(self, sdb):
        self.sdb = sdb
        self.conn = self.sdb.getConnection()
        self.c = self.sdb.getCursor()
   
    def commit(self):
        self.conn.commit()
        
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
            self.c.execute(q3, (system["last_checkin"], ret[0]))
            return ret[0]

        self.c.execute(q1, (system["id"],))
        return self.c.fetchone()[0]
            
    def addGroup(self, grp):
        q1 = """select groupid from GROUPINFO where rhnsid = %s"""
        q2 = """insert into GROUPINFO (rhnsid, name) values (%s, %s)"""
        
        self.c.execute(q1, (grp["sgid"],))
        ret = self.c.fetchone()

        if ret == None:
            self.c.execute(q2, (grp["sgid"], grp["system_group_name"]))
        else:
            return ret[0]

        self.c.execute(q1, (grp["sgid"],))
        return self.c.fetchone()[0]

    def subscribeGroup(self, clientid, groupids):
        q1 = """delete from GROUPS where clientid = %s"""
        self.c.execute(q1, (clientid,))

        if len(groupids) == 0:
            return

        q2 = """insert into GROUPS (clientid, groupid) values """
        for id in groupids:
            q2 = "%s (%s, %s)," % (q2, clientid, id)

        self.c.execute(q2[:-1], ())

    def markActive(self, clients):
        q = ""
        for id in clients:
            if q == "":
                q = "clientid = %s"
            else:
                q = q + " or clientid = %s"

        q1 = """update CLIENTS set active = 0"""
        q2 = """update CLIENTS set active = 1 where """ + q

        self.c.execute(q1, ())
        self.c.execute(q2, clients)
