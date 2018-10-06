#! /usr/bin/env bash

path=$PWD
dir=""

rm -r out1
rm -r out2

mkdir out1
mkdir out2

for c in $(seq 5 1 15)
do
	./textcat_ensp_c.py TRAIN loglinear$c chars-10.txt en.1K sp.1K
	RESULT1=$(./textcat_ensp_c.py TEST loglinear$c chars-10.txt en.1K sp.1K 0.7 /home/data/cs465/hw-lm/english_spanish/dev/english/*/*)
	RESULT2=$(./textcat_ensp_c.py TEST loglinear$c chars-10.txt en.1K sp.1K 0.7 /home/data/cs465/hw-lm/english_spanish/dev/spanish/*/*)

	echo $RESULT1 > out1/$c
	echo $RESULT2 > out2/$c

done

./compute_c.py
