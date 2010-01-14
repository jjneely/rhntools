#!/bin/bash

# Sync up our RHN Satellite to upstream

# random wait
#perl -le 'sleep rand 3600' 

satellite-sync #--email >/dev/null 2>/dev/null
SATRET=$?

/root/bin/make-yumable.sh
YUMRET=$?

# Now Tell nagios that we were successful
if [ $SATRET == "0" -a $YUMRET == "0" ] ; then
    STAT="linux05rhn\tsat-sync\t0\tSatellite Sync was successful\n" 
else
    STAT="linux05rhn\tsat-sync\t2\tSatellite Sync was NOT successful\n"
fi

echo -e "$STAT" | /root/bin/send_nsca.pl -H nagios.unity.ncsu.edu

