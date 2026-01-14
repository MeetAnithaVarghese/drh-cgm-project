
# Diabetes CGM Research Data Pipeline

This project simulates a clinical research environment for Continuous Glucose Monitoring (CGM). It includes a synthetic data generator that mimics raw exports from major manufacturers and a set of **Singer.io Taps** to standardize this data into an immutable, appendable research database.

## 1. Project Structure

```text
.
├── diabetes_research_data/       # Generated raw sensor data
│   ├── abbott/                   # Simulated LibreView CSVs
│   ├── dexcom/                   # Simulated Clarity CSVs
│   ├── medtronic/                # Simulated CareLink CSVs
│   └── demographics/             # Participant metadata (Age, HbA1c, etc.)
├── src/
│   ├── main.py                   # The Synthetic Data Generator
│   ├── tap_abbott.py             # Singer Tap for Abbott Libre
│   ├── tap_dexcom.py             # Singer Tap for Dexcom G6
│   └── tap_medtronic.py          # Singer Tap for Medtronic Guardian
├── requirements.txt              # Project dependencies
└── drh_diabetes.db               # Final standardized SQLite Research Hub

```

## 2. Setup and Installation

1. **Activate your Virtual Environment:**

```fish
python -m venv venv
source venv/bin/activate.fish

```

1. **Install Dependencies:**

```fish
pip install -r requirements.txt

```

## 3. Step 1: Generate Synthetic Research Data

The generator creates realistic physiological data based on participant HbA1c. It is **deterministic**, meaning if you generate 7 days of data today and 28 days tomorrow, the first 7 days will remain identical.

| Argument | Description |
| --- | --- |
| `--mfg` | Manufacturer selection (`abbott`, `dexcom`, `medtronic`, or `all`) |
| `--n` | Number of participants to generate |
| `--days` | Study duration in days (e.g., 7, 14, 28) |

**Example Command:**

```fish
python src/generate-manufacturer-data.py --mfg all --n 20 --days 14
python src/generate-research-data.py --mfg all --n 20 --days 14

```

## 4. Step 2: Standardizing Data (Singer Taps)

To move data from raw manufacturer formats into the **Combined CGM Tracing** format, run the specific taps. Each tap outputs standardized JSON lines.

### Standardized Format (DRH)

* `id`: A deterministic hash of `ParticipantID + Timestamp` (Ensures Immutability).
* `participant_id`: The unique subject identifier.
* `date_time`: Formatted as `YYYY-MM-DD HH:MM:SS`.
* `cgm_value`: The glucose reading in mg/dL.

**Run a Tap to view JSON output:**

```fish
python src/tap_abbott.py

```

## 5. Step 3: Persistence (SQLite / DRH Hub)

To maintain an **immutable and append-only** database, pipe the Tap output into a target. The system uses the `id` hash as a primary key. If a record already exists in the database, it will not be overwritten (protecting the original data).

**Ingest all data into the Research Hub:**

```fish
# Ingest Abbott
python src/tap_abbott.py | target-sqlite --config config.json

# Ingest Dexcom
python src/tap_dexcom.py | target-sqlite --config config.json

```

## 6. Research Use Case

This pipeline handles three critical research scenarios:

1. **Longitudinal Growth:** When new data is added to a file, the system only appends the new timestamps and ignores the old ones.
2. **Data Integrity:** If a raw file is deleted from the folder, the data remains safely stored in the `drh_diabetes.db`.
3. **Consistency:** Even with different sampling rates (Abbott 15-min vs Dexcom 5-min), the final database treats all participants as a single, unified cohort.

---


