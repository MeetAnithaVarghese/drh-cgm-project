import pandas as pd
import numpy as np
import argparse
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
OUTPUT_DIR = "./diabetes_research_data"

def setup_folders():
    for m in ['abbott', 'dexcom', 'medtronic', 'demographics']:
        os.makedirs(os.path.join(OUTPUT_DIR, m), exist_ok=True)

def generate_events(days):
    """Generates a list of meal and exercise events."""
    events = []
    for d in range(days):
        # 3 Meals a day
        for h in [8, 13, 19]:
            ts = datetime(2026, 1, 1) + timedelta(days=d, hours=h)
            events.append({'time': ts, 'type': 'Meal', 'val': np.random.randint(30, 70)})
        # Random exercise
        if np.random.rand() > 0.4:
            ts = datetime(2026, 1, 1) + timedelta(days=d, hours=17, minutes=30)
            events.append({'time': ts, 'type': 'Exercise', 'val': 30})
    return events

# --- EXPORT LOGIC ---

def save_as_abbott(p_id, t_seq, g_values, events):
    rows = []
    # Abbott typically logs historic data every 15 mins
    for i in range(0, len(t_seq), 15):
        rows.append({
            'Device': 'FreeStyle Libre 3',
            'Device Timestamp': t_seq[i].strftime('%Y/%m/%d %H:%M'),
            'Record Type': 0,
            'Historic Glucose mg/dL': g_values[i],
            'Notes': ''
        })
    # Add Events
    for e in events:
        rows.append({
            'Device Timestamp': e['time'].strftime('%Y/%m/%d %H:%M'),
            'Record Type': 4 if e['type'] == 'Meal' else 5,
            'Notes': f"{e['type']}: {e['val']}"
        })
    pd.DataFrame(rows).to_csv(f"{OUTPUT_DIR}/abbott/{p_id}_libre.csv", index=False)

def save_as_dexcom(p_id, t_seq, g_values, events):
    rows = []
    # Dexcom logs every 5 mins
    for i in range(0, len(t_seq), 5):
        rows.append({
            'Timestamp': t_seq[i].isoformat(),
            'Event Type': 'EGV',
            'Glucose Value (mg/dL)': g_values[i]
        })
    for e in events:
        rows.append({'Timestamp': e['time'].isoformat(), 'Event Type': e['type'], 'Event Value': e['val']})
    pd.DataFrame(rows).to_csv(f"{OUTPUT_DIR}/dexcom/{p_id}_clarity.csv", index=False)

def save_as_medtronic(p_id, t_seq, g_values, events):
    rows = []
    # Medtronic wide format (simplified for research)
    for i in range(0, len(t_seq), 5):
        rows.append({
            'Date': t_seq[i].strftime('%d/%m/%y'),
            'Time': t_seq[i].strftime('%H:%M:%S'),
            'Sensor Glucose (mg/dL)': g_values[i],
            'Carb Input': next((e['val'] for e in events if e['time'] == t_seq[i] and e['type'] == 'Meal'), '')
        })
    pd.DataFrame(rows).to_csv(f"{OUTPUT_DIR}/medtronic/{p_id}_simplera.csv", index=False)


def generate_demographics(n_participants, mfg_name, days):
    """Generates a demographics file specific to a manufacturer cohort."""
    # Use a specific seed for each manufacturer to keep them distinct but reproducible
    seeds = {'abbott': 10, 'dexcom': 20, 'medtronic': 30, 'all': 40}
    np.random.seed(seeds.get(mfg_name, 50))
    
    data = []
    for i in range(1, n_participants + 1):
        p_id = f"SUBJ_{i:03d}"
        data.append({
            'USUBJID': p_id,
            'AGE': np.random.randint(18, 80),
            'SEX': np.random.choice(['M', 'F']),
            'ETHNICITY': np.random.choice(['Hispanic', 'Not Hispanic']),
            'DIABETES_TYPE': np.random.choice(['T1D', 'T2D'], p=[0.4, 0.6]),
            'BASE_HBA1C': round(np.random.uniform(6.0, 10.0), 1),
            'DEVICE_ASSIGNED': mfg_name.upper(),
            'STUDY_LENGTH_DAYS': days
        })
    
    df = pd.DataFrame(data)
    # Save the demographic file inside the specific manufacturer's folder
    path = f"{OUTPUT_DIR}/{mfg_name}/demographics_{mfg_name}.csv"
    if mfg_name == 'all':
        path = f"{OUTPUT_DIR}/demographics/participants_master.csv"
    
    df.to_csv(path, index=False)
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mfg", choices=['abbott', 'dexcom', 'medtronic', 'all'], default='all')
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    setup_folders()
    
    # Determine which manufacturers to process
    target_mfgs = ['abbott', 'dexcom', 'medtronic'] if args.mfg == 'all' else [args.mfg]

    print(f"🚀 Starting Research Generation: {args.n} participants | {args.days} days")

    for mfg in target_mfgs:
        print(f"--- Processing {mfg.upper()} Cohort ---")
        
        # 1. Generate and save demographics for this specific manufacturer
        demo_df = generate_demographics(args.n, mfg, args.days)
        
        # 2. Generate CGM data for each participant in this demographic
        for _, patient in demo_df.iterrows():
            p_id = patient['USUBJID']
            a1c = patient['BASE_HBA1C']
            
            # Use a more realistic physiological trace based on the patient's A1c
            t_seq = [datetime(2026, 1, 1) + timedelta(minutes=m) for m in range(args.days * 1440)]
            
            # Scale glucose baseline by their A1c (higher A1c = higher mean glucose)
            mean_glucose = (28.7 * a1c) - 46.7
            g_values = np.random.normal(mean_glucose, 15, len(t_seq)).clip(40, 400).astype(int)
            
            events = generate_events(args.days)

            if mfg == 'abbott': save_as_abbott(p_id, t_seq, g_values, events)
            if mfg == 'dexcom': save_as_dexcom(p_id, t_seq, g_values, events)
            if mfg == 'medtronic': save_as_medtronic(p_id, t_seq, g_values, events)

    print(f"\n✅ Success! All data saved in '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()