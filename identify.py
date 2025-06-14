import pandas as pd
import argparse
import json
import re
import sys
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

# Map each requirement ID to its associated dataset
REQUIREMENT_TO_DATASET = {
    #'R1': 'DataSets/bpicR1.csv',
    'R1': 'DataSets/Real/BPI_12.csv',
    'S1': 'DataSets/Real/Sepsis_R2.csv',
    'S2': 'DataSets/Real/Sepsis_R3.csv',
    'B1': 'DataSets/Real/BPI_12.csv',

}

def parse_requirement(req):
    """Parse condition and consequence from the requirement"""
    condition_seconds = int(re.findall(r'\d+', req['condition'])[0])
    from_label, to_label = [x.strip() for x in req['consequence'].split('->')]
    livecycle_start = req["livecycle_start"]
    livecycle_end = req["livecycle_end"]
    return condition_seconds, from_label, to_label, livecycle_start, livecycle_end

def identify_conditional_followups(df, result_df):
    print("\n🔎 Identifying conditional follow-up steps for violations...")

    df_sorted = df.sort_values(by=['case:concept:name', 'time:timestamp'])

    # Get from_label used in this result set
    if result_df.empty:
        print("No result data provided.")
        return

    from_label = result_df.iloc[0]['from']

    # Split case IDs
    violation_cases = result_df[result_df['delta_seconds'] > 0]['case:concept:name'].unique()
    non_violation_cases = result_df[result_df['delta_seconds'] <= 0]['case:concept:name'].unique()

    # Track which activities appear after from_label in each case
    violation_followups = {}
    non_violation_followups = {}

    for case_id, group in df_sorted.groupby('case:concept:name'):
        group = group.reset_index(drop=True)
        followup_set = set()

        for i, row in group.iterrows():
            if row['concept:name'] == from_label:
                after = group.iloc[i+1:]
                followup_set.update(after['concept:name'].tolist())
                break  # only consider first from_label

        if case_id in violation_cases:
            violation_followups[case_id] = followup_set
        elif case_id in non_violation_cases:
            non_violation_followups[case_id] = followup_set

    # === Strict Check ===
    all_violation_acts = set.union(*violation_followups.values()) if violation_followups else set()
    all_non_violation_acts = set.union(*non_violation_followups.values()) if non_violation_followups else set()
    strict_exclusives = all_violation_acts - all_non_violation_acts

    print(f"\n🧠 Strict exclusives (only after violations, never after compliant cases):")
    if strict_exclusives:
        for act in sorted(strict_exclusives):
            print(f"- {act}")
    else:
        print("None found.")

    # === Relaxed Check ===
    # Activity must appear in ALL violation cases, and not in ALL non-violation cases
    common_in_violations = set.intersection(*violation_followups.values()) if violation_followups else set()
    relaxed_exclusives = set()

    for act in common_in_violations:
        appears_in_all_non_violations = all(act in s for s in non_violation_followups.values())
        if not appears_in_all_non_violations:
            relaxed_exclusives.add(act)

    print(f"\n🧠 Relaxed patterns (always after violations, but not always after compliant cases):")
    if relaxed_exclusives:
        for act in sorted(relaxed_exclusives - strict_exclusives):
            print(f"- {act}")
    else:
        print("None found.")


def r1_evaluation(log, activity_name, required_seconds ):
    results = []

    activity_name = activity_name.strip()

    for trace in log:
        case_id = trace.attributes.get('concept:name')
        schedule_time = None
        start_time = None

        for event in trace:
            event_activity = str(event.get('concept:name', '')).strip()
            transition = str(event.get('lifecycle:transition', '')).strip().upper()
            timestamp = event.get('time:timestamp')

            if event_activity == activity_name:
                if transition == 'SCHEDULE' and schedule_time is None:
                    schedule_time = timestamp
                elif transition == 'START' and start_time is None:
                    start_time = timestamp

            # If both found, no need to continue
            if schedule_time and start_time:
                break

        if schedule_time and start_time:
            actual_diff = (start_time - schedule_time).total_seconds()
            delta = actual_diff - required_seconds

            results.append({
                'case:concept:name': case_id,
                'activity': activity_name,
                'from': 'SCHEDULE',
                'to': 'START',
                'from_time': schedule_time,
                'to_time': start_time,
                'actual_seconds': actual_diff,
                'required_seconds': required_seconds,
                'delta_seconds': delta
            })

    return pd.DataFrame(results)

def evaluate_requirement(df, from_label, to_label, condition_seconds):
    """Compute time deltas for each occurrence of from_label leading to the next to_label"""
    results = []

    df_sorted = df.sort_values(by=['case:concept:name', 'time:timestamp'])

    for case_id, group in df_sorted.groupby('case:concept:name'):
        group = group.reset_index(drop=True)
        for i, row in group.iterrows():
            if row['concept:name'] == from_label:
                from_time = row['time:timestamp']

                # Look ahead for next to_label, but only before next from_label
                later = group.iloc[i+1:]
                next_from_index = later[later['concept:name'] == from_label].index.min()
                if pd.notna(next_from_index):
                    later = later.loc[:next_from_index - 1]

                match = later[later['concept:name'] == to_label]
                if not match.empty:
                    to_time = match.iloc[0]['time:timestamp']
                    actual_diff = (to_time - from_time).total_seconds()
                    delta = actual_diff - condition_seconds
                else:
                    to_time = pd.NaT
                    actual_diff = None
                    delta = None  # max violation / not computable

                results.append({
                    'case:concept:name': case_id,
                    'from': from_label,
                    'to': to_label,
                    'from_time': from_time,
                    'to_time': to_time,
                    'actual_seconds': actual_diff,
                    'required_seconds': condition_seconds,
                    'delta_seconds': delta
                })
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Evaluate a specific temporal requirement.")
    parser.add_argument('--requirement', type=str, default='B1',
                        choices=['B1', 'S1', 'S2'],
                        help='Requirement ID to evaluate (e.g., B1, S1, S2)')
    parser.add_argument('--requirements', type=str, default='requirements.json',
                        help='Path to the JSON file with requirements')

    args = parser.parse_args()

    requirement_id = args.requirement

    # Load requirements JSON
    with open(args.requirements, 'r') as f:
        requirements = json.load(f)
    

    # Get dataset for this requirement
    dataset_file = REQUIREMENT_TO_DATASET[requirement_id]
    

    # Load the corresponding dataset
    print(f"Loading dataset for {requirement_id}: {dataset_file}")
    df = pd.read_csv(dataset_file, sep=",")
    
    for col in df.columns:
        print(f"- {col}")

    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'], format='mixed')


    # Parse and evaluate requirement
    req = requirements[requirement_id]
    condition_seconds, from_label, to_label, livecycle_start, livecycle_end = parse_requirement(req)
    print(f"\n=== Evaluating {requirement_id}: {from_label} -> {to_label}, required ≤ {condition_seconds}s ===")
    if from_label in to_label:
        print(f"labels are identical, identifying by livecycle transitions instead")
        log = xes_importer.apply('DataSets/Real/BPI_Challenge_2012.xes')
        result_df = r1_evaluation(log, from_label, condition_seconds)
    else:
        result_df = evaluate_requirement(df, from_label, to_label, condition_seconds)

    if result_df.empty:
        print("No matching events found.")
    else:
        print(result_df[['case:concept:name', 'from', 'to', 'from_time', 'to_time', 'delta_seconds']])
        # Summary statistics
        mean_delta = result_df['delta_seconds'].mean()
        median_delta = result_df['delta_seconds'].median()

        print("\n📊 Summary Statistics:")
        print(f"- Mean delta (seconds):   {mean_delta:.2f}")
        print(f"- Median delta (seconds): {median_delta:.2f}")

        # Count positive, negative, zero deltas, and NaNs
        total = len(result_df)
        print(f'total: {total}')
        positive = (result_df['delta_seconds'] > 0).sum()
        print(f'positive: {positive}')
        negative = (result_df['delta_seconds'] < 0).sum()
        print(f'negative: {negative}')
        zero = (result_df['delta_seconds'] == 0).sum()
        print(f'zero: {zero}')
        missing = result_df['delta_seconds'].isna().sum()
        print(f'missing: {missing}')

        # Count NaNs as positive violations
        total_with_missing_as_violation = total
        positive_with_missing = positive + missing


        pct_pure_positive = (positive/total)*100
        pct_positive = (positive_with_missing / total_with_missing_as_violation) * 100
        pct_negative = (negative / total_with_missing_as_violation) * 100
        pct_zero = (zero / total_with_missing_as_violation) * 100
        pct_missing = (missing / total_with_missing_as_violation) * 100

        test= ((negative-total)/total)*100
        print(f"Violations with the same formula as in the paper {test}")

        print("\n📈 Delta Distribution (with missing transitions as violations):")
        print(f"- % Positive deltas (violations): {pct_pure_positive:.2f}%")
        print(f"- % Positive deltas wtih missing (violations): {pct_positive:.2f}%")
        print(f"- % Negative deltas (faster):     {pct_negative:.2f}%")
        print(f"- % Zero deltas (exact match):    {pct_zero:.2f}%")
        print(f"- (Included {missing} cases with missing 'to' label as violations which are {pct_missing:.2f}%)")

        #identify_conditional_followups(df, result_df)

if __name__ == "__main__":
    main()

