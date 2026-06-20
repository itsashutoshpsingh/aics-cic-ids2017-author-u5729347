"""
verify_dataset.py
-----------------
Sanity-checks your CIC-IDS2017 data BEFORE you run the full notebook, so you can
confirm you are pointing at the right folder and that the files look as expected.

Usage (from the SUBMISSION root):
    python verify_dataset.py
or point it explicitly at a folder:
    python verify_dataset.py "DATASET/CSVs/MachineLearningCSV/MachineLearningCVE"

It prints a short report and a PASS/CHECK verdict. It does NOT modify anything.
"""
import sys, os, glob
import pandas as pd
import numpy as np

# The 78 behavioural flow features we expect (after stripping whitespace).
EXPECTED_HINT = {"Flow Duration", "Total Fwd Packets", "Flow Bytes/s",
                 "Flow Packets/s", "SYN Flag Count", "Destination Port"}
# Identifier columns that should NOT be present for a generalisable detector.
LEAKAGE_COLS = {"Flow ID", "Source IP", "Src IP", "Source Port", "Src Port",
                "Destination IP", "Dst IP", "Timestamp", "Protocol"}

DEFAULT_DIRS = [
    "DATASET/CSVs/MachineLearningCSV/MachineLearningCVE",
    "DATASET/CSVs/MachineLearningCSV",
    "MachineLearningCSV/MachineLearningCVE",
    "data",
]


def find_dir(arg):
    if arg:
        return arg
    for d in DEFAULT_DIRS:
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.csv")):
            return d
    return None


def read_csv_safe(path):
    """Read a CIC-IDS2017 CSV, tolerating the non-UTF-8 byte in some labels."""
    for enc in ("utf-8", "latin1"):
        try:
            return pd.read_csv(path, low_memory=False, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, low_memory=False, encoding="latin1",
                       encoding_errors="replace")


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    folder = find_dir(arg)
    print("=" * 70)
    print("CIC-IDS2017 DATASET VERIFICATION")
    print("=" * 70)
    if not folder:
        print("\u274c Could not find a CSV folder. Pass the path explicitly, e.g.:")
        print('   python verify_dataset.py "DATASET/CSVs/MachineLearningCSV/MachineLearningCVE"')
        return
    files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    print(f"Folder      : {folder}")
    print(f"CSV files   : {len(files)}")
    for f in files:
        print(f"   - {os.path.basename(f)}")
    if not files:
        print("\u274c No CSV files in that folder.")
        return

    # load
    frames, total = [], 0
    for f in files:
        d = read_csv_safe(f)
        frames.append(d); total += len(d)
    df = pd.concat(frames, ignore_index=True)
    df.columns = df.columns.str.strip()

    label_col = "Label" if "Label" in df.columns else df.columns[-1]
    feats = [c for c in df.columns if c != label_col]

    print("\n" + "-" * 70)
    print(f"Total rows         : {len(df):,}")
    print(f"Total columns      : {df.shape[1]}  ({len(feats)} features + label)")
    print(f"Label column       : '{label_col}'")

    # leakage / wrong-folder check
    present_leak = sorted(set(df.columns) & LEAKAGE_COLS)
    hint_present = len(EXPECTED_HINT & set(df.columns))

    print("\nLABEL DISTRIBUTION")
    vc = df[label_col].astype(str).value_counts()
    for k, v in vc.items():
        print(f"   {k:35s} {v:>10,}  ({v/len(df):6.2%})")
    benign = vc.get("BENIGN", 0)
    attack = len(df) - benign
    print(f"\n   Benign vs Attack   : {benign:,}  vs  {attack:,}  "
          f"(attack prevalence {attack/len(df):.1%})")

    # data-quality probe
    num = df[feats].apply(pd.to_numeric, errors="coerce")
    n_inf = int(np.isinf(num.to_numpy(dtype='float64', na_value=np.nan)).sum())
    n_nan = int(num.isna().sum().sum())
    n_dup = int(df.duplicated().sum())
    print("\nDATA-QUALITY PROBE")
    print(f"   Infinite values    : {n_inf:,}")
    print(f"   Missing/NaN values : {n_nan:,}")
    print(f"   Duplicate rows     : {n_dup:,}")

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    ok = True
    if present_leak:
        ok = False
        print("\u26a0\ufe0f  This looks like the GeneratedLabelledFlows version: it contains")
        print(f"    identifier columns {present_leak}.")
        print("    Use the MachineLearningCVE folder instead (behavioural features only),")
        print("    OR drop those columns, or the model may 'cheat' by memorising hosts.")
    if hint_present >= 4 and not present_leak:
        print("\u2705  Column set looks like the MachineLearningCVE flow features - correct input.")
    if benign == 0:
        ok = False
        print("\u26a0\ufe0f  No 'BENIGN' label found - check the label column / encoding.")
    if 60 <= len(feats) <= 85 and not present_leak:
        print(f"\u2705  Feature count ({len(feats)}) is in the expected CICFlowMeter range.")
    if n_inf or n_nan or n_dup:
        print("\u2705  Expected quirks present (Inf/NaN/duplicates) - the notebook's")
        print("    cleaning step will handle these.")
    if ok and not present_leak:
        print("\n\u2192 PASS. Set USE_REAL_DATA = True and DATA_DIR to this folder, then Run All.")
    else:
        print("\n\u2192 CHECK the warnings above before running the notebook.")
    print("=" * 70)


if __name__ == "__main__":
    main()
