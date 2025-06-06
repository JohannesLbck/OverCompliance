import yaml
import os
import pandas as pd

def load_yaml(path):
    df = pd.DataFrame(columns=['concept:name', 'shift:timestamp', 'cpee:lifecycle:transition', 'data'])
    with open(path, 'r') as file:
        data = yaml.safe_load_all(file)
        for event in data:
            if 'event' in event:
                if 'cpee:lifecycle:transition' in event['event']:
                    if event['event']['cpee:lifecycle:transition'] in ("activity/calling", "activity/done", "dataelements/change"):
                        e = event['event']
                        row = pd.DataFrame([{
                            'concept:name': e.get('concept:name'),
                            'shift:timestamp': e.get('shift:timestamp'),
                            'cpee:lifecycle:transition': e['cpee:lifecycle:transition'],
                            'data' : e.get('data')
                        }])
                        df = pd.concat([df, row], ignore_index=True)
    return df 

def load_all(direc):
    return_data = []
    for filename in os.listdir(direc):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            path = os.path.join(direc, filename)
            return_data.append(load_yaml(path))
    return return_data


