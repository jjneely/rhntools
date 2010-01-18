#!/bin/bash

# Sync up our RHN Satellite to upstream

# random wait
perl -le 'sleep rand 3600' 

exec sat-sync-now.sh

