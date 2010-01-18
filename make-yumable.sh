#!/bin/bash

# Where is the yum tree start
YUMROOT=/var/satellite/yum/rhel

cd /usr/share/rhntools

if [ "$1" = "-f" ] ; then
    CHANNELS=""
    for c in `find $YUMROOT -type l`; do
        DIR=`basename $c`
        CHANNELS="$CHANNELS $DIR"
    done
    echo "Updating all channels: $CHANNELS"
    VERBOSE=true
else
    # This builds the package trees and outputs channels that changed
    CHANNELS=`python findpackages53.py`
    VERBOSE=false
fi

DONE=""

echo "Starting Creatrepo runs:"
date

if [ "$1" = "-f" ] ; then
    OPTS="--database"
else
    OPTS="--skip-stat --update --checkts --database"
fi

for CHANNEL in $CHANNELS ; do
    for REPO in `find $YUMROOT -type l -name $CHANNEL` ; do
        DIR=`dirname $REPO`
        if echo "$DONE" | grep "$DIR" > /dev/null ; then
            continue
        fi

        DONE="$DONE $DIR"
        [ -d $DIR/cache ] || mkdir $DIR/cache
        if $VERBOSE ; then
            echo "Updating repo in $DIR..."
            createrepo $OPTS -c $DIR/cache $DIR
        else
            echo "Updating repo in $DIR from new packages in $CHANNEL ..."
            createrepo $OPTS -q -c $DIR/cache $DIR
        fi            
    done
done

echo "Createrepo runs done."
date

