#!/bin/bash


cp $QOCKDIR/tools/qock.sh /etc/init.d/qock

mkdir -p /var/run/qock/
mkdir -p /var/log/qock/

update-rc.d -f qock defaults

