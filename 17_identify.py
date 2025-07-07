import pandas as pd

def verify(C,I):
    Compliant = False
    Per = False
    if C:
        if I:
            Compliant = True
            Per = True
    else:
        Compliant = True
    return Compliant, C, I, Per

def verify_B2(trace_df):
    labels = trace_df['concept:name'].tolist()
    C1 = (trace_df['CreditScore'] < 100).any()
    C2 = (trace_df['case:RequestedAmount'] > 40000).any()
    C = C1 and C2
    #I = "A_Denied" in trace_df['concept:name'].values
    I = 'W_Assess potential fraud' in labels
    ## I am looking for some label that happens often but not all the time
    #I = 'W_Assess potential fraud' in df['concept:name'].values 
    return verify(C, I)

def verify_B3(trace_df):
    labels = trace_df['concept:name'].tolist()
    C = 'A_Submitted' in labels 
    #I = "A_Denied" in trace_df['concept:name'].values
    I = 'W_Complete application' in labels
    ## I am looking for some label that happens often but not all the time
    #I = 'W_Assess potential fraud' in df['concept:name'].values 
    return verify(C, I)

def verify_B4(trace_df):
    labels = trace_df['concept:name'].tolist()
    I= 'W_Complete application' in labels
    #I = "A_Denied" in trace_df['concept:name'].values
    C = 'O_Sent (mail and online)' in labels
    ## I am looking for some label that happens often but not all the time
    #I = 'W_Assess potential fraud' in df['concept:name'].values 
    return verify(C, I)

def verify_B5(trace_df):
    labels = df['concept:name'].tolist()
    C = (trace_df['case:LoanGoal'] == 'Home improvement').any()
    I = (trace_df['case:RequestedAmount'] < 10000).any()
    #I = "A_Denied" in trace_df['concept:name'].values
    ## I am looking for some label that happens often but not all the time
    #I = 'W_Assess potential fraud' in df['concept:name'].values
    return verify(C, I)


## Loading
df = pd.read_csv('DataSets/Real/BPI_17.csv', sep='\t')

## For testing, only looks at 10 percent of traces
#df= df.iloc[:int(len(df) * 0.10)]


print(df.columns)

grouped = df.sort_values('time:timestamp').groupby('case:concept:name')

print(len(grouped))

Set_Compliant = []
Set_C = []
Set_I = []
Set_Per = []
for _, trace in grouped:
    compliant, c, i, per = verify_B2(trace)
    Set_Compliant.append(compliant)
    Set_C.append(c)
    Set_I.append(i)
    Set_Per.append(per)

print(f'The process has {len(grouped)} traces')

max_over_compliance = (1-(sum(Set_C)/len(grouped)))
print(f'The process has {sum(Set_Compliant)} compliant traces (|Compliant|)')
print(f'The process requires the execution of the consequence in {sum(Set_C)} traces (|C|)')
print(f'The process is executing the consequence in {sum(Set_I)} traces (|I|)')
print(f'The process is correctly executing the consequence in {sum(Set_Per)} traces (|Per|)')
over_compliance_level = ((sum(Set_I)-sum(Set_Per))/len(grouped))
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
c = sum(Set_I)/len(grouped)
u = round(1-(sum(Set_Compliant)/len(grouped)),2)
print(sum(Set_Compliant))
print(len(grouped))

Cost = u*C_viol + (c-p)*C_con - (c-p)*P_over
print(f'u*C_viol + (c-p)*C_con - (c-p)*P_over = Cost')
print(f'{u}*{C_viol} + ({c}-{p})*{C_con} - ({c}-{p})*{P_over} = {Cost}')
Cost_V2 = abs(under_compliance_level)*C_viol + over_compliance_level*C_con - abs(over_compliance_level)*P_over
print(Cost_V2)

