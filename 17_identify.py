import pandas as pd
import argparse

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

def verify_B2(trace_df):
    labels = trace_df['concept:name'].tolist()
    C1 = (trace_df['CreditScore'] < 100).any()
    C2 = (trace_df['case:RequestedAmount'] > 40000).any()
    C = C1 and C2
    D = 'W_Assess potential fraud' in labels
    return verify(C, D)

def verify_B3(trace_df):
    labels = trace_df['concept:name'].tolist()
    C = 'A_Submitted' in labels 
    D = 'W_Complete application' in labels
    return verify(C, D)

def verify_B4(trace_df):
    labels = trace_df['concept:name'].tolist()
    D= 'W_Complete application' in labels
    C = 'O_Sent (mail and online)' in labels
    return verify(C, D)

def verify_B5(trace_df):
    labels = df['concept:name'].tolist()
    C = (trace_df['case:LoanGoal'] == 'Home improvement').any()
    D = (trace_df['case:RequestedAmount'] < 10000).any()
    return verify(C, D)


verifiers = {
    'B6' : verify_B2,
    'B7' : verify_B3,
    'B8' : verify_B4,
    'B9' : verify_B5
        }


## ArgsParsing
parser = argparse.ArgumentParser(description="Evaluate a specific requirement of the BPIC17 dataset")
parser.add_argument('--r', type=str, default='B6', choices=['B6', 'B7', 'B8', 'B9'], help= 'Which requirement to evaluate')

args = parser.parse_args()

## Loading
df = pd.read_csv('DataSets/Real/BPI_17.csv', sep='\t')

## For testing, only looks at 10 percent of traces
#df= df.iloc[:int(len(df) * 0.10)]


print(df.columns)

grouped = df.sort_values('time:timestamp').groupby('case:concept:name')

print(len(grouped))

Set_Compliant = []
Set_C = []
Set_D = []
Set_Per = []
for _, trace in grouped:
    compliant, c, i, per = verifiers[args.r](trace)
    Set_Compliant.append(compliant)
    Set_C.append(c)
    Set_D.append(i)
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

