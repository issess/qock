#!/bin/bash

FOUND=`grep "usb0" /proc/net/dev`

if  [ -n "$FOUND" ] ; then

echo "usb modem found"

echo "disconnect network...."
sudo poff e303

else

echo "usb modem not found"

fi







