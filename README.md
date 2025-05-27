# OverCompliance Identification

QuickStart:
1. Git Clone
2. `python3 identify.py `
3. If any packages are missing, use your preferred virtual env and `pip install -r requirements.txt`

This repository contains the code for the evaluation of the ... Paper.

There are two main scripts one for working with the BPIC and Sepsis datasets (A) and one for identification in the Synthetic datasets (B):

## (A) Identifcation for BPIC/Sepsis

1. Git Clone
2. `python3 identify.py --requirement RX -- requirements requirements.json` where X refers to the requirements ID
3. If any packages are missing, use your preferred virtual env and `pip install -r requirements.txt`

## (B) Identification for the Synthetic Dataset

There are 3 Synthetic Datasets O, U, M where O contains overcompliant traces, U contains undercompliant traces while finnaly M contains both over and undercompliant traces (meaning undercompliant processes). You can check any requirement of the running example on any of the processes, but in practice it makes the most sense to check them as described in the Paper. For this use the Quickstart Check below

1. Git Clone
2. `python3 synth_identify_all.py`

However you can also check specific requirements on specific datasets by passing the arguments:

1. `python3 synth_identify.py --r RX.X --d Y` where X in {R1, R2, R3.1, R3.2} and Y in {O, U, M}
