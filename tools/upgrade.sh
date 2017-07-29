#!/bin/bash

echo "updating qock............."

cd $QOCKDIR

if git pull --rebase --stat origin master
then
    echo "qock updated!"
else
    echo "there was an error updating!"
fi