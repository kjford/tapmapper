#!/bin/bash
cd ~/tapmapper/tapmapper/
echo 'Processing raw tweets'
python procrawtweets.py
echo 'Cleaning and binning raw tweets'
python cleanandbinproctweets.py
echo 'Recomputing TFIDF table'
python computetfidf.py
echo 'Creating output files'
python getstats.py
echo 'Done'