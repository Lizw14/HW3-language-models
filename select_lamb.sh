#! /usr/bin/env bash


for lam in $(seq 0 0.01 1)
do
	./textcat.py TRAIN add$lam words-10.txt gen spam
	./textcat.py TRAIN add$lam words-10.txt gen spam

	
