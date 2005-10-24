INITDB = """

create table CLIENTS (
    clientid    INTEGER PRIMARY KEY,
    rhnsid      INTEGER,
    name        TEXT,
    lastcheckin TEXT
);

create table GROUPINFO (
    groupid     INTEGER PRIMARY KEY,
    rhnsid      INTEGER,
    name        TEXT,
    notes       TEXT
);

create table GROUPS (
    clientid    INTEGER,
    groupid     INTEGER
);

"""
