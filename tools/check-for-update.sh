#!/bin/bash

#QOCK_UPDATED=`cat .qock-updated`
#whence git >/dev/null || return 0

while ! ping -c 1 -W 1 8.8.8.8 &> /dev/null ; do
    echo "Waiting for 8.8.8.8 - network interface might be down..."
    sleep 5
done

. $QOCKDIR/tools/upgrade.sh

