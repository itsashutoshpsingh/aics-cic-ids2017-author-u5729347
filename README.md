WM9PH-15 — Machine Learning Intrusion Detection (CIC-IDS2017)

CONTENTS OF THIS SUBMISSION (per the assignment brief — single zip):
  1. REPORT
       AICS_Report.docx           <- primary report (open in Microsoft Word; figures render in Word)
       AICS_Report_LaTeX_alt.pdf  <- same project, LaTeX/PDF format (figure-perfect)
  2. JUPYTER NOTEBOOK(S)
       01_intrusion_detection_BEST.ipynb          <- main pipeline (binary + multiclass + robustness)
       02_intrusion_detection_FULL_DATASET.ipynb  <- full-dataset variant
  3. TRAINED MODEL + LOAD/TEST CODE
       models/ids_random_forest.joblib            <- REPLACE with the model your own run saves
       (the notebook's final cell loads the model and re-runs the test exactly as in the report)

BEFORE SUBMITTING:
  - Put your NAME and STUDENT ID on the report cover.
  - Rewrite Appendix A (AI declaration) truthfully, with your verbatim prompts.
  - Re-run the notebook on your local CIC-IDS2017 copy so the notebook outputs and the
    saved model are YOUR executed results (numbers may differ trivially by seed/library).
  - Keep references for any extra libraries (all are free: scikit-learn, numpy, pandas, matplotlib).
