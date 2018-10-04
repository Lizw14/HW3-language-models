#! /usr/bin/env bash

path=$PWD
dir=""

mkdir out1
mkdir out2

for lam in $(seq 0.001 0.001 0.02)
do
	./fileprob.py TRAIN add$lam words-10.txt gen
	RESULT1=$(./fileprob.py TEST add$lam words-10.txt gen gsdev/gen/*)
	./fileprob.py TRAIN add$lam words-10.txt spam
	RESULT2=$(./fileprob.py TEST add$lam words-10.txt spam gsdev/spam/*)
	echo $RESULT1 > out1/result1.$lam
	echo $RESULT2 > out2/result2.$lam

done

./compute_lam.py	

#rm -r out1
#rm -r out2

