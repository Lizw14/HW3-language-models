#! /usr/bin/env bash

path=$PWD
dir=""

rm -r out1_
rm -r out2_

mkdir out1_
mkdir out2_

for c in $(seq 0.006 0.001 0.006)
do
	./textcat_ensp_c.py TRAIN improved chars-10.txt en.1K sp.1K
	RESULT1=$(./textcat_ensp_c.py TEST improved chars-10.txt en.1K sp.1K 0.7 /home/data/cs465/hw-lm/english_spanish/dev/english/*/*)
	RESULT2=$(./textcat_ensp_c.py TEST improved chars-10.txt en.1K sp.1K 0.7 /home/data/cs465/hw-lm/english_spanish/dev/spanish/*/*)

	echo $RESULT1 > out1_/$c
	echo $RESULT2 > out2_/$c

done

./compute_acc.py
