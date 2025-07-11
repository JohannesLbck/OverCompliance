import pandas as pd
import argparse
from collections import Counter

def verify(C,D):
    Compliant = False
    Per = False
    if C:
        if D:
            Compliant = True
            Per = True
    else:
        Compliant = True
    return Compliant, C, D, Per

def verify_R3(trace_df):
    labels = trace_df['concept:name'].str.strip()
    A = 'aanname laboratoriumonderzoek'.strip()
    B = 'ordertarief'.strip()
    C = A in labels.values 
    if C:
        try:
            pos_A = labels[labels == A].index[0]
            pos_B = labels[labels == B].index[0]
            D = pos_A < pos_B
        except IndexError:
            D = True  
    else:
        D = False 
    return verify(C, D)

def verify_R1_2(trace_df):
    labels = trace_df['concept:name'].str.strip().tolist()
    C1 = 'vervolgconsult poliklinisch'.strip() in labels
    C2 = 'administratief tarief       - eerste pol'.strip() in labels
    C = C1 and C2
    a_indices = [i for i, label in enumerate(labels) if label == 'administratief tarief       - eerste pol']
    b_indices = [i for i, label in enumerate(labels) if label == 'vervolgconsult poliklinisch']

    # For each A, find the first B that comes after it
    D = False 
    for i, a_idx in enumerate(a_indices):
        # Find the first B after this A
        b_after = next((b for b in b_indices if b > a_idx), None)
        if b_after:
            D = any(a2 > a_idx and a2 < b_after for a2 in a_indices)
    return verify(C, D)

def verify_R10(trace_df):
    labels = trace_df['concept:name'].str.strip()
    C1 = (trace_df[[f'case:Diagnosis Treatment Combination ID:{i}' for i in range(1, 12)]] == 495326).any().any()
    A = 'hemoglobine foto-elektrisch'.strip()
    C2 = A in labels.values
    C = C1 and C2
    labels = trace_df['concept:name'].str.strip()
    B = 'ureum'.strip()
    if C2:
        try:
            pos_A = labels[labels == A].index[0]
            pos_B = labels[labels == B].index[0]
            D = pos_A < pos_B
        except IndexError:
            D = True
    else:
        D = False
    return verify(C, D)

def verify_R2(trace_df):
    labels = trace_df['concept:name'].str.strip().tolist()
    A = 'administratief tarief       - eerste pol'
    B = 'vervolgconsult poliklinisch'
    A_b = A in labels
    B_b = B in labels
    C = A_b or B_b
    #D = A_b and B_b
    D = (A_b and B_b) or (not A_b and not B_b)
    return verify(C, D)


def verify_R11(trace_df):
    labels = trace_df['concept:name'].str.strip()
    cols = ['case:Age', 'case:Age:1', 'case:Age:2', 'case:Age:3', 'case:Age:4']
    matching_cols = (df[cols] > 70)
    A = 'natrium vlamfotometrisch'.strip()
    B = 'calcium'.strip()
    C0 = A in labels.values
    C1 = matching_cols.any().any()
    C2 = (trace_df['case:Treatment code'] > 802).any()
    C3 = (trace_df[[f'case:Diagnosis Treatment Combination ID:{i}' for i in range(1, 12)]] < 394726).any().any()
    C4 = (trace_df['case:Treatment code'] == 803).any()
    C5 = (trace_df['case:Treatment code'] == 703).any()
    #C = (C1 and C2 and C3) or C4 or C5
    C = C0 and ((C1 and C2 and C3) or C4 or C5) 
    if C0:
        try:
            pos_A = labels[labels == A].index[0]
            pos_B = labels[labels == B].index[0]
            D = pos_A > pos_B
        except IndexError:
            D = True 
    else:
        D = True
    return verify(C, D)

def verify_R13(trace_df):
    labels = trace_df['concept:name'].str.strip().tolist()
    C1 = 'telefonisch consult' in labels
    C2 = (trace_df['case:Treatment code'] == 101).any()
    C3 = (trace_df['Producer code'] == 'SGAL').any()
    C4 = (trace_df['Producer code'] == 'SGNA').any()
    C = C1 and (C2 and (C3 or C4))
    D = not 'alkalische fosfatase -kinetisch-' in labels
    return verify(C, D)


def verify_R14(trace_df):
    section_col = trace_df['Section'].astype(str).str.strip()
    org_group_col = trace_df['org:group'].astype(str).str.strip()
    specialism_cols = ['Specialism code', 'case:Specialism code'] + [f'case:Specialism code:{i}' for i in range(1, 16)]
    existing_specialism_cols = [col for col in specialism_cols if col in trace_df.columns]

    specialism_match = (trace_df[existing_specialism_cols] == 86).any(axis=1)
    section_match = section_col == 'Section 4'

    matching_rows = trace_df[specialism_match & section_match]

    C = not matching_rows.empty
    D = (matching_rows['org:group'].astype(str).str.strip() == 'General Lab Clinical Chemistry').all() 
    return verify(C, D)

verifiers = {
    'B2' : verify_R2,
    'B3' : verify_R10,
    'B4' : verify_R11,
    'B5' : verify_R13
        }
parser = argparse.ArgumentParser(description="Evaluate a specific requirement")
parser.add_argument('--r', type=str, default='B2', choices=['B2', 'B3', 'B4', 'B5'], help= 'Which requirement to evaluate')

args = parser.parse_args()

## Loading
df = pd.read_csv('DataSets/Real/BPIC11.csv', sep='\t')

## For testing, only looks at x percent of traces
#df= df.iloc[:int(len(df) * 0.50)]


print(df.columns.tolist())

grouped = df.sort_values('time:timestamp').groupby('case:concept:name')

print(len(grouped))

Set_Compliant = []
Set_C = []
Set_D = []
Set_Per = []
for _, trace in grouped:
    compliant, c, d, per = verify_R13(trace)
    Set_Compliant.append(compliant)
    Set_C.append(c)
    Set_D.append(d)
    Set_Per.append(per)

print(f'The process has {len(grouped)} traces')

max_over_compliance = (1-(sum(Set_C)/len(grouped)))
print(f'The process has {sum(Set_Compliant)} compliant traces (|Compliant|)')
print(f'The process requires the execution of the consequence in {sum(Set_C)} traces (|C|)')
print(f'The process is executing the consequence in {sum(Set_D)} traces (|D|)')
print(f'The process is correctly executing the consequence in {sum(Set_Per)} traces (|Per|)')
over_compliance_level = ((sum(Set_D)-sum(Set_Per))/len(grouped))
print(f'The over-compliance level of the process is {over_compliance_level*100}%')
print(f'The maximal over-compliance level of the process is {max_over_compliance*100}%')
under_compliance_level = ((sum(Set_Per)-sum(Set_C))/len(grouped))
print(f'The under-compliance level of the process is {under_compliance_level*100}%')
print(f'The maximal under-compliance level of the process is -100%')

if sum(Set_Compliant) == len(grouped):
    print("Process is Compliant")
    if over_compliance_level == 0:
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
p = sum(Set_C)/len(grouped)
c = sum(Set_D)/len(grouped)
u = round(1-(sum(Set_Compliant)/len(grouped)),2)
print(sum(Set_Compliant))
print(len(grouped))

Cost = u*C_viol + (c-p)*C_con - (c-p)*P_over
print(f'u*C_viol + (c-p)*C_con - (c-p)*P_over = Cost')
print(f'{u}*{C_viol} + ({c}-{p})*{C_con} - ({c}-{p})*{P_over} = {Cost}')
Cost_V2 = abs(under_compliance_level)*C_viol + over_compliance_level*C_con - abs(over_compliance_level)*P_over
print(Cost_V2)

