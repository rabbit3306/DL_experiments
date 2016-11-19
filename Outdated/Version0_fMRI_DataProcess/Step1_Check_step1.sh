#!/bin/bash


# list the samples we want to process
IIDarray=( 346237 258600 287986 322000 360323 \
301395 306073 360317 382187 258955 280778 300334 \
343912 345555 228872 357475 376933 368413 291229 \
295969 300043 306375 342326 341793 342278 342915 \
347402 348491 358777 381307 367567 342514 223896 \
233437 234917 238542 238623 240811 243902 254581 \
255986 257271 259654 259806 260580 262078 264214 \
266208 266634 267713 268914 268925 269279 273503 \
279084 279472 280365 281887 282646 283913 289559 \
289656 290815 296769 296863 300088 308182 308403 \
308418 315850 350735 365086 387091)

declare -i fileShould=140

for iid in ${IIDarray[@]};
do
    cd /home/medialab/data/ADNI/fMRI_${iid}
    fileNo=$(ls -1 | wc -l)
    if [ $fileNo -ne $fileShould ]
    then
        echo $iid
        echo $fileNo
    fi
done
