#!/bin/bash

if [ ! -d /afs/unity/web/l/linux/secure/rhntools/rhnstats ] ; then
    exit 0
fi

cd /afs/unity/web/l/linux/secure/rhntools/rhnstats
python rhnstats.py

