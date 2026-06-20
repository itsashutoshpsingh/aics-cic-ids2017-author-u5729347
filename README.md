# CIC-IDS2017 Intrusion Detection

Machine-learning intrusion detection on the CIC-IDS2017 flow dataset for WM9PH-15.
The project covers binary detection (benign vs malicious), multi-class attack
attribution, and robustness checks (time-ordered split, unseen-attack and noise tests).

## Files

| File | Purpose |
|------|---------|
| `intrusion_detection.ipynb` | Full pipeline: load, clean, compare models, tune, evaluate, robustness, save model |
| `ids_utils.py` | Shared data loading, cleaning and splitting |
| `load_and_test.py` | Loads the saved model and re-runs the binary test |
| `models/ids_random_forest.joblib` | Trained Random Forest |
| `requirements.txt` | Dependencies |

## Dataset

CIC-IDS2017, `MachineLearningCVE` CSV folder only, from the Canadian Institute for
Cybersecurity: https://www.unb.ca/cic/datasets/ids-2017.html
The raw CSVs are large and public, so they are not stored here; download them and set
`DATA_DIR` at the top of the notebook and of `load_and_test.py`.

## Run

```
pip install -r requirements.txt
jupyter notebook intrusion_detection.ipynb     # run top to bottom
python load_and_test.py                        # reload the model and score the test set
```

All dependencies are free and standard (numpy, pandas, scikit-learn, matplotlib, joblib).
