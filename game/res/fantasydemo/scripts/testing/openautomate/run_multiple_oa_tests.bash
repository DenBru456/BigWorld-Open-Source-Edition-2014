#!/bin/bash
seed=1
if [ $# -gt 0 ]; then
   seed=$1
fi
while [ $seed -lt 1000 ];
do
	echo "running test with seed $seed"
	../../../../../src/lib/third_party/openautomate/Debug/oatest.exe -seed $seed ../../../../game/fantasydemo_hybrid.exe >> test_output
	if [ $? != 0 ]; then
		echo "test failed with seed $seed"
		exit 1
	fi
	seed=`expr $seed + 1`
done