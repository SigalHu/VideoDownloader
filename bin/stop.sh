#!/usr/bin/env bash

cd `dirname $0`
cd ..
kill `cat pid.txt`
