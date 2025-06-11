# OverCompliance Identification

QuickStart:
1. Git Clone
2. `python3 synth_identify.py --r R2 --d M`
3. If any packages are missing, use your preferred virtual env and `pip install -r requirements.txt`

Quickstart will test Requirement R2 on dataset M which is also used for the cost calculation example.

There are two main scripts one for working with the BPIC and Sepsis datasets (A) and one for identification in the Synthetic datasets (B):

## (A) Identifcation for BPIC/Sepsis

1. Git Clone
2. `python3 identify.py --requirement XX --requirements requirements.json` where X refers to the requirements ID, i.e., options are --requirement B1, S1, S2
3. If any packages are missing, use your preferred virtual env and `pip install -r requirements.txt`

## (B) Identification for the Synthetic Dataset

There are 3 Synthetic Datasets O, U, M where O contains overcompliant traces, U contains undercompliant traces while finnaly M contains both over and undercompliant traces (meaning undercompliant processes). You can check any requirement of the running example on any of the processes using the script below. 

1. `python3 synth_identify.py --r RXX --d Y` where X in {R1, R2, R31, R32} and Y in {O, U, M}

There is also a little script which is used for estimating the costs at discrete levels:

1. `python3 discrete_levels.py`

