#! /usr/bin/env bash

path=$PWD
dir=""

rm -r out1
rm -r out2

mkdir out1
mkdir out2

for c in $(seq 0.01 0.01 0.1)
do
	./textcat.py TRAIN loglinear$c chars-10.txt en.1K sp.1K
	RESULT1=$(./textcat.py TEST loglinear$c chars-10.txt en.1K sp.1K 0.7 esdev/english/*/*)
	RESULT2=$(./textcat.py TEST loglinear$c chars-10.txt en.1K sp.1K 0.7 esdev/spanish/*/*)

	echo $RESULT1 > out1/$c
	echo $RESULT2 > out2/$c

done

./compute_c.py
