import pandas as pd
import argparse
import json
import sys
import os
from preprocessing import *
from identifiers import *

dict_paths = {
    'M' : 'DataSets/Mixed',
    'O' : 'DataSets/Over',
    'U' : 'DataSets/Under'
        }
verifiers = {
    'R1' : verify_r1,
    'R2' : verify_r2,
    'R31' : verify_r31,
    'R32' : verify_r32
        }

parser = argparse.ArgumentParser(description="Evaluate a specific requirement")
parser.add_argument('--r', type=str, default='R2', choices=['R1', 'R2', 'R31', 'R32'], help= 'Which requirement to evaluate')
parser.add_argument('--d', type=str, default='M', choices=['M', 'O', 'U'], help = "Which dataset to use for the evaluation")

args = parser.parse_args()

data = load_all(dict_paths[args.d])

print(data)

Set_Compliant = []
Set_C = []
Set_I = []
Set_Per = []
for trace in data:
    compliant, c, i, per = verifiers[args.r](trace)
    Set_Compliant.append(compliant)
    Set_C.append(c)
    Set_I.append(i)
    Set_Per.append(per)

print(f'The process has {len(data)} traces')

max_over_compliance = (1-(sum(Set_C)/len(data)))
print(f'The process has {sum(Set_Compliant)} compliant traces (|Compliant|)')
print(f'The process requires the execution of the consequence in {sum(Set_C)} traces (|C|)')
print(f'The process is executing the consequence in {sum(Set_I)} traces (|I|)')
print(f'The process is correctly executing the consequence in {sum(Set_Per)} traces (|Per|)')
over_compliance_level = ((sum(Set_I)-sum(Set_C))/len(data))
print(f'The over-compliance level of the process is {over_compliance_level*100}%')
print(f'The maximal over-compliance level of the process is {max_over_compliance*100}%')
under_compliance_level = ((sum(Set_Per)-sum(Set_C))/len(data))
print(f'The under-compliance level of the process is {under_compliance_level*100}%')
print(f'The maximal under-compliance level of the process is -100%')

if sum(Set_Compliant) == len(data):
    print("Process is Compliant")
    if int(over_compliance_level) == 0:
        print(f'The process is perfectly compliant')
    else:
        print(f'The process is overcompliant')
else:
    print("Process is NonCompliant / undercompliant")

print(f'Cost Calculation:')
C_viol = 1500
C_con = 120
P_over = 0
print(f'Assuming: C_viol = {C_viol}, C_con = {C_con}, P_over = {P_over}')
p = sum(Set_C)/len(data)
c = sum(Set_I)/len(data)
u = round(1-(sum(Set_Compliant)/len(data)),2)
print(sum(Set_Compliant))
print(len(data))

Cost = u*C_viol + (c-p)*C_con - (c-p)*P_over
print(f'u*C_viol + (c-p)*C_con - (c-p)*P_over = Cost')
print(f'{u}*{C_viol} + ({c}-{p})*{C_con} - ({c}-{p})*{P_over} = {Cost}')
Cost_V2 = abs(under_compliance_level)*C_viol + over_compliance_level*C_con - abs(over_compliance_level)*P_over
print(f' {abs(under_compliance_level)}*{C_viol} + {abs(over_compliance_level)}*{C_con} - {over_compliance_level}*{P_over}')

print(Cost_V2)
