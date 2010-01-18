#!/bin/bash

# Sync up our RHN Satellite to upstream

satellite-sync --email >/dev/null 2>/dev/null
SATRET=$?

# Generate Yum repos from newly synced Satellite packages
make-yumable.sh
YUMRET=$?

# Now Tell nagios that we were successful
HOST=`hostname --short`
if [ $SATRET == "0" -a $YUMRET == "0" ] ; then
    STAT="$HOST\tsat-sync\t0\tSatellite Sync was successful\n" 
else
    STAT="$HOST\tsat-sync\t2\tSatellite Sync was NOT successful\n"
fi

echo -e "$STAT" | /root/bin/send_nsca.pl -H uni04sm.unity.ncsu.edu
echo -e "$STAT" | /root/bin/send_nsca.pl -H uni05sm.unity.ncsu.edu

