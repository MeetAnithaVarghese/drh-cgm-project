import singer
import pandas as pd
import hashlib
from datetime import datetime

STREAM_NAME = 'combined_cgm_tracing'

def get_pk(p_id, dt):
    return hashlib.md5(f"{p_id}{dt}".encode()).hexdigest()

def transform_abbott(p_id, row):
    # Abbott format: YYYY/MM/DD HH:MM
    dt_obj = datetime.strptime(row['Device Timestamp'], '%Y/%m/%d %H:%M')
    dt_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
    return {
        'id': get_pk(p_id, dt_str),
        'participant_id': p_id,
        'date_time': dt_str,
        'cgm_value': float(row['Historic Glucose mg/dL'])
    }

def main():
    schema = {
        'properties': {
            'id': {'type': 'string'},
            'participant_id': {'type': 'string'},
            'date_time': {'type': 'string', 'format': 'date-time'},
            'cgm_value': {'type': 'number'}
        }
    }
    singer.write_schema(STREAM_NAME, schema, ['id'])
    
    # Path logic based on your structure
    base_path = "./diabetes_research_data_7days/abbott/"
    for filename in os.listdir(base_path):
        if filename.endswith("_abbott.csv"):
            p_id = filename.split('_')[0] + "_" + filename.split('_')[1]
            df = pd.read_csv(os.path.join(base_path, filename))
            # Only type 0 (Historic Glucose)
            df = df[df['Record Type'] == 0].dropna(subset=['Historic Glucose mg/dL'])
            
            for _, row in df.iterrows():
                singer.write_record(STREAM_NAME, transform_abbott(p_id, row))

if __name__ == "__main__":
    import os
    main()