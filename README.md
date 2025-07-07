# OverCompliance Identification

QuickStart:
1. Git Clone
2. `python3 synth_identify.py --r R2 --d M`
3. If any packages are missing, use your preferred virtual env and `pip install -r requirements.txt`

Quickstart will test Requirement R2 on dataset M which is also used for the cost calculation example.

There are three main scripts one for working with the BPIC12 and Sepsis datasets (A), one for the evaluation using the BPIC17 datase (B), and one for identification in the Synthetic datasets (C):

## (A) Identifcation for BPIC2012/Sepsis

1. Git Clone
2. `python3 identify.py --requirement XX --requirements requirements.json` where X refers to the requirements ID, i.e., options are --requirement B1, S1, S2
3. If any packages are missing, use your preferred virtual env and `pip install -r requirements.txt`


## (B) Identifaction for BPIC2017

The BPIC2017 dataset is too large to just upload to GitHub directly, so replicating this takes slightly more steps. If you want to skip this step we also included the results of these verifications as .txt files in the 17\_results directory.

1. Git Clone
2. Move to the DataSets\Real directory `cd DataSets\Real` 
3. Download the BPIC2017 dataset into the Datasets\Real directory from [https://data.4tu.nl/articles/dataset/BPI_Challenge_2017/12696884](https://data.4tu.nl/articles/dataset/BPI_Challenge_2017/12696884) 
4. Unzip and then gunzip the folder
5. Transform the .xes file into a .csv or change the code of the 17\_identify to work with a .xes file instead. You can do this in python using pm4py by loading the file into python and then exporting it as .csv: `log = pm4py.read_xes('<path-to-xes-log-file.xes>')` and `log.to_csv('BPIC17.csv', sep='\t', encoding='utf-8', index=False, header=True)`
6. `python3 17_identify.py`

To verify the different requirements simply change the ID in the code from B2 to B3, B4, or B5 respectively.

## (C) Identification for the Synthetic Dataset

There are 3 Synthetic Datasets O, U, M where O contains overcompliant traces, U contains undercompliant traces while finnaly M contains both over and undercompliant traces (meaning undercompliant processes). You can check any requirement of the running example on any of the processes using the script below. 

1. `python3 synth_identify.py --r RXX --d Y` where X in {R1, R2, R31, R32} and Y in {O, U, M}

There is also a little script which is used for estimating the costs at discrete levels:

1. `python3 discrete_levels.py`

This last script has no logging so depending on your device give it a second to execute.
