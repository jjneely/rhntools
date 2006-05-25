import pickle
import MySQLdb
import getpass

host="mysql01.unity.ncsu.edu"
user="cls_admin"
passwd = getpass.getpass("CLS Mysql Password:")
db="campuslinux"

conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
cursor = conn.cursor()
cursor.execute("select hostname from realmlinux")

l = []

for row in cursor.fetchall():
    print row[0]
    l.append(row[0])

s = pickle.dumps(l)
fd = open("hosts.pic", "w")
fd.write(s)
fd.close()

