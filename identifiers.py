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

def verify_r1(df):
    labels = df['concept:name'].tolist()
    C = 'Receive Loan Request' in labels
    I = 'Create Loan File' in labels
    return verify(C,I) 

def verify_r2(df):
    labels = df['concept:name'].tolist()
    helper = 'Decline due to bad credit worthiness' in labels
    for row in df['data']:
        if row is not None:
            if row[0]['name'] == "loan_amount":
                C = row[0]['value'] > 10000 and not helper
    I = 'Evaluate Loan Risk' in labels
    return verify(C,I) 

def r2_discrete_levels(df):
    labels = df['concept:name'].tolist()
    helper = 'Decline due to bad credit worthiness' in labels
    for row in df['data']:
        if row is not None:
            if row[0]['name'] == "loan_amount":
                C = row[0]['value'] > 10000 and not helper
                case_5000 = row[0]['value'] > 5000 and not helper
                case_50000 = row[0]['value'] > 50000 and not helper
    I = 'Evaluate Loan Risk' in labels
    Compliant, C, I, Per = verify(C,I)
    return Compliant, C, I, Per, case_5000, case_50000


def verify_r31(df):
    labels = df['concept:name'].tolist()
    C = 'Sign Loan Contract' in labels
    I = 'Check Credit Worthiness' in labels
    return verify(C,I)


def verify_r32(df):
    labels = df['concept:name'].tolist()
    for row in df['data']:
        if row is not None:
            if row[0]['name'] == "credit_worthy":
                C = row[0]['value'] == False
    I = 'Decline due to bad credit worthiness' in labels
    return verify(C,I)

