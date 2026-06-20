---
title: "How to Run & Verify the Project"
subtitle: "WM9PH-15 — Machine Learning Project (CIC-IDS2017 Intrusion Detection)"
date: "Setup, execution and data-verification guide"
---

# 0. Why you got `ModuleNotFoundError: No module named 'numpy'`

This is **not a bug in the code**. It means VS Code ran the notebook against a
Python environment that does **not** have the scientific packages installed —
your `.venv` is empty, or the wrong interpreter/kernel is selected. Section 1
fixes it completely. Once the packages are installed and the right kernel is
selected, the import cell runs silently.

---

# 1. Set up the Python environment (do this once)

You already have a `.venv` folder in the project. We will install the required
packages into it and tell VS Code to use it.

> Open a terminal **in the SUBMISSION folder** (in VS Code: `Terminal → New
> Terminal`). The prompt should show the `SUBMISSION` directory.

## 1a. Activate the virtual environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```
If PowerShell blocks the script, run this once then retry:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

You should now see `(.venv)` at the start of your prompt.

> If you do **not** have a working `.venv`, create one first:
> `python -m venv .venv` (Windows: `py -m venv .venv`), then activate as above.

## 1b. Install the packages

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` is included in the project. It installs: `numpy`, `pandas`,
`scikit-learn`, `matplotlib`, `seaborn`, `joblib`, `jupyter`, `ipykernel`.

## 1c. Point VS Code at this environment

1. Open `01_intrusion_detection_BEST.ipynb`.
2. Click the **kernel picker** at the **top-right** of the notebook
   (it may say *"Select Kernel"* or show another Python version).
3. Choose **Python Environments → `.venv`** (the one in your project folder).

Now re-run the first cell. The `numpy` error is gone.

> **Quick sanity check** — run this in the activated terminal; it must print a
> version with no error:
> ```bash
> python -c "import numpy, pandas, sklearn, seaborn; print('OK', numpy.__version__)"
> ```

---

# 2. Verify your data is correct (recommended before the full run)

You downloaded the dataset into `DATASET/CSVs/`. There are **two** versions, and
choosing the right one matters:

| Folder | What it contains | Use it? |
|---|---|---|
| `GeneratedLabelledFlows/` `TrafficLabelling_` | Flow features **plus identifiers**: Flow ID, Source/Destination IP, Ports, Protocol, Timestamp | **No** |
| `MachineLearningCSV/` `MachineLearningCVE` | The 78 **behavioural** flow features + `Label` only | **Yes** |

**Why MachineLearningCVE is the right choice.** A good detector should learn
*how attack traffic behaves*, not *which IP address attacked*. The
GeneratedLabelledFlows version includes Source/Destination IP, Port and Timestamp.
If the model can see those, it can "cheat" by memorising that, say, `192.168.x.x`
was the attacker on that day — this is **identifier leakage** and the model will
not generalise to a real network. The MachineLearningCVE version has those
identifiers removed, leaving only behavioural statistics, which is exactly what
you want.

Run the included verifier (with your environment activated):

```bash
python verify_dataset.py "DATASET/CSVs/MachineLearningCSV/MachineLearningCVE"
```

It prints the file list, total rows (~2.8 million on the full set), column count
(should be ~79 = 78 features + label), the label distribution, the
Infinity/NaN/duplicate counts, and a **PASS / CHECK** verdict. A `PASS` means you
are pointing at the right folder and the notebook will handle the rest.

> If the verifier warns that **identifier columns** are present, you have pointed
> at `GeneratedLabelledFlows` by mistake — switch to `MachineLearningCVE`.

---

# 3. Run the project on the real data

Open the notebook and edit **only the configuration cell (cell 1)**:

```python
USE_REAL_DATA = True
DATA_DIR      = "DATASET/CSVs/MachineLearningCSV/MachineLearningCVE"
```

Then **Run All** (`▶▶` or `Run → Run All Cells`).

## 3a. If a CSV fails to read (encoding error)

One CIC-IDS2017 file (the Web-Attacks day) contains a non-UTF-8 byte in a label.
If you see a `UnicodeDecodeError`, replace the body of the `load_real` function in
the loading cell with this robust version:

```python
def load_real(folder):
    files = sorted(glob.glob(os.path.join(folder, '*.csv')))
    if not files:
        raise FileNotFoundError(f'No CSVs found in {folder!r}')
    frames = []
    for f in files:
        try:
            frames.append(pd.read_csv(f, low_memory=False))           # utf-8
        except UnicodeDecodeError:
            frames.append(pd.read_csv(f, low_memory=False, encoding='latin1'))
    return pd.concat(frames, ignore_index=True)
```

## 3b. The full dataset is large (~2.8M rows) — two sensible options

**Option A — verify quickly first (recommended).** Add this line at the **end of
the loading cell**, just after `df` is created, to work on a representative
stratified sample while you confirm everything runs end-to-end:

```python
# OPTIONAL: fast pass on a 300k stratified sample to validate the pipeline.
df = (df.groupby('Label', group_keys=False)
        .apply(lambda g: g.sample(min(len(g), 30000), random_state=42))
        .reset_index(drop=True))
```

Run the whole notebook on the sample (a couple of minutes). When you are happy it
works and the numbers look sensible, **comment that block out** and Run All again
on the full data for your final figures.

**Option B — run the full dataset directly.** Expect the Random-Forest training
and the hyperparameter search to take several minutes and a few GB of RAM. The
notebook already subsamples the *tuning* step for tractability; you can raise that
cap (the `train_size=10000` line) if you want to tune on more data.

---

# 4. What "correct output" looks like (how to verify the approach worked)

After **Run All**, check these — they confirm the pipeline behaved correctly:

1. **Cleaning report** prints a sensible feature count (≈ 67–78 after dropping
   constant columns) and removes some Inf/NaN cells and duplicate rows.
2. **Class distribution** shows the strong benign majority (~80% on the full set)
   and the long tail of attack classes — i.e. the imbalance is real.
3. **Model comparison table** shows three models with **F1 well above 0.9**, with
   Random Forest highest. *If any model shows recall = 0 or F1 = 0, something is
   wrong* (usually a label or split problem).
4. **Confusion matrix** is strongly diagonal but **not necessarily perfect** —
   a few false negatives are normal and healthy (a perfectly diagonal matrix on
   real data can signal leakage).
5. **Feature importances** are dominated by behavioural features (window sizes,
   inter-arrival timing, packet-length stats, flag counts) — *not* by anything
   that looks like an identifier. If you ever see an IP/port/timestamp at the top,
   you used the wrong CSV folder.
6. The model is saved to `models/ids_random_forest.joblib`, and the final cell
   reloads it and predicts on a few unseen flows.

---

# 5. Update the report with YOUR results (required before submitting)

Every figure and number in `AICS_Report.docx` / `.pdf` currently comes from the
offline reconstruction and is flagged with a **red "Replace before submission"
panel**. After your real run:

- Replace the figures in the report with the freshly generated ones (the notebook
  re-creates the same plots; export them or screenshot the notebook outputs).
- Update the metrics in **Table 1** (validation), **Table 3** (test) and the
  surrounding sentences (especially the false-positive / false-negative counts in
  the confusion-matrix paragraph).
- Rewrite **Appendix A (AI-use declaration)** truthfully: describe what you
  actually used, paste your **verbatim** prompts, and explain how you checked the
  output. The template version must not be submitted as-is.
- Add your **Student ID** on the cover.

---

# 6. Building the final submission zip

Your `SUBMISSION` folder already matches the brief's required deliverables:

```
SUBMISSION/
├── AICS_Report.pdf                      # report (or submit the .docx)
├── AICS_Report.docx
├── 01_intrusion_detection_BEST.ipynb# the executable solution
├── generate_synthetic.py                # only used when USE_REAL_DATA = False
├── verify_dataset.py                    # data sanity-checker
├── requirements.txt
├── README.md
├── figures/                             # report figures
├── models/ids_random_forest.joblib      # trained model + scaler
└── DATASET/                             # the data you downloaded
```

For submission, zip the folder **without** the multi-gigabyte `DATASET/PCAPs/`
(the brief asks for report + notebook(s) + trained model + data, but the PCAPs are
not needed by your CSV-based solution and will bloat the upload). Keep the
`MachineLearningCVE` CSVs if you want the marker to be able to re-run it; otherwise
the trained `.joblib` plus the notebook is sufficient to reproduce your tests.

---

# 7. Troubleshooting quick-reference

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: numpy` | Wrong kernel — select `.venv` (Section 1c) and `pip install -r requirements.txt`. |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate. |
| `FileNotFoundError: No CSVs found` | `DATA_DIR` path is wrong — copy the exact path of the `MachineLearningCVE` folder. |
| `UnicodeDecodeError` while reading | Use the `latin1` fallback `load_real` in Section 3a. |
| Notebook runs forever / runs out of RAM | Use the 300k stratified sample in Section 3b (Option A). |
| `ModuleNotFoundError: generate_synthetic` | Only happens with `USE_REAL_DATA = False`; keep `generate_synthetic.py` beside the notebook, or set `USE_REAL_DATA = True`. |
| Kernel keeps dying | Close other apps; sample the data; ensure 64-bit Python. |

You are taking the right approach: **binary benign-vs-attack** classification on
the **MachineLearningCVE** behavioural features, with a leakage-safe split, scaling
fitted on the training fold only, class weighting for imbalance, and
threshold-independent metrics (F1, ROC-AUC, PR-AUC) for evaluation.
