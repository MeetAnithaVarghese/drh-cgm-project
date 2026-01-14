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

# --- RAW DATA EXPORTERS (Your provided logic) ---

def save_raw_abbott(p_id, t_seq, g_values):
    """Simulates a LibreView CSV export (15-min sampling)."""
    rows = []
    for i in range(0, len(t_seq), 15):
        rows.append({
            "Device": "FreeStyle Libre 3",
            "Serial Number": "SN-987654321",
            "Device Timestamp": t_seq[i].strftime("%Y/%m/%d %H:%M"),
            "Record Type": 0,
            "Historic Glucose mg/dL": g_values[i],
            "Scan Glucose mg/dL": "",
            "Non-numeric Rapid-Acting Insulin": "",
            "Rapid-Acting Insulin (units)": ""
        })
    df = pd.DataFrame(rows)
    file_path = os.path.join(OUTPUT_DIR, "abbott", f"{p_id}_abbott.csv")
    with open(file_path, 'w') as f:
        f.write(f'"Patient Name","{p_id}"\n"Export Date","2026/01/15 10:00"\n\n')
        df.to_csv(f, index=False)

def save_raw_dexcom(p_id, t_seq, g_values):
    """Simulates a Dexcom Clarity CSV export (5-min sampling)."""
    rows = []
    for i in range(0, len(t_seq), 5):
        rows.append({
            "Index": i // 5,
            "Timestamp": t_seq[i].strftime("%Y-%m-%dT%H:%M:%S"),
            "Event Type": "EGV",
            "Event Subtype": "",
            "Glucose Value (mg/dL)": g_values[i],
            "Glucose Internal": "",
            "Transmitter ID": "TX-12345"
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, "dexcom", f"{p_id}_dexcom.csv"), index=False)

def save_raw_medtronic(p_id, t_seq, g_values):
    """Simulates a Medtronic CareLink CSV export (5-min sampling)."""
    rows = []
    for i in range(0, len(t_seq), 5):
        rows.append({
            "Index": i // 5,
            "Date": t_seq[i].strftime("%d/%m/%y"),
            "Time": t_seq[i].strftime("%H:%M:%S"),
            "New Device Time": "",
            "Sensor Glucose (mg/dL)": g_values[i],
            "ISIG Value": round(np.random.uniform(15, 45), 2),
            "Event Marker": ""
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUTPUT_DIR, "medtronic", f"{p_id}_medtronic.csv"), index=False)

# --- DEMOGRAPHICS ---

def generate_demographics(n_participants):
    """Generates immutable demographics based on a fixed seed."""
    np.random.seed(42) # Fixed seed so demographics never change
    data = []
    for i in range(1, n_participants + 1):
        p_id = f"SUBJ_{i:03d}"
        data.append({
            "USUBJID": p_id,
            "AGE": np.random.randint(18, 75),
            "SEX": np.random.choice(["M", "F"]),
            "BASE_HBA1C": round(np.random.uniform(5.5, 9.5), 1),
            "DIABETES_TYPE": "Type 1" if np.random.rand() > 0.3 else "Type 2"
        })
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(OUTPUT_DIR, "demographics", "demographics.csv"), index=False)
    return df

# --- MAIN EXECUTION ---

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mfg", choices=['abbott', 'dexcom', 'medtronic', 'all'], default='all')
    parser.add_argument("--n", type=int, default=20, help="Number of participants")
    parser.add_argument("--days", type=int, default=7, help="Duration (7, 14, 28)")
    args = parser.parse_args()

    setup_folders()
    demo_df = generate_demographics(args.n)
    
    target_mfgs = ['abbott', 'dexcom', 'medtronic'] if args.mfg == 'all' else [args.mfg]

    for mfg in target_mfgs:
        print(f"Generating {args.days} days of raw {mfg.upper()} data...")
        
        for idx, patient in demo_df.iterrows():
            p_id = patient['USUBJID']
            a1c = patient['BASE_HBA1C']
            
            # Deterministic Seed per participant
            # This ensures Day 1-7 is the same when you generate 28 days later
            np.random.seed(2000 + idx)
            
            t_seq = [datetime(2026, 1, 1) + timedelta(minutes=m) for m in range(args.days * 1440)]
            mean_g = (28.7 * a1c) - 46.7
            g_values = np.random.normal(mean_g, 20, len(t_seq)).clip(40, 400).astype(int)

            if mfg == 'abbott': save_raw_abbott(p_id, t_seq, g_values)
            elif mfg == 'dexcom': save_raw_dexcom(p_id, t_seq, g_values)
            elif mfg == 'medtronic': save_raw_medtronic(p_id, t_seq, g_values)

    print(f"Done! Check the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()