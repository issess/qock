#!/bin/bash


FOUND=`grep "usb0" /proc/net/dev`

if  [ -n "$FOUND" ] ; then

echo "usb modem found"

echo "wait for switch modem.."

sudo usb_modeswitch -v 0x12d1 -p 0x1f01 -V 0x12d1 -P 0x1001 -M "55534243000000000000000000000611060000000000000000000000000000"

sleep 5

echo "connect network..."

sudo pon e303

else

echo "usb modem not found"

fi




