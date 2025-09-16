# 🛒 E-Commerce Brazil Data Analysis

This project analyzes the [Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).  
It provides a full end-to-end pipeline:

- **ETL pipeline** → Load, clean, and transform raw Kaggle CSVs into an SQLite database  
- **SQL + Python analysis** → KPIs and data diagnostics  
- **Interactive dashboard** → Streamlit app to explore results  
- **One-click orchestration** → Automated project runner (`run_project.bat`)  

---

> **Note**: `data/raw/`, `data/processed/`, and `outputs/` are **not included** in the repo because they are too large. Add them locally after cloning.  

---

## 📽️ Visual
https://drive.google.com/file/d/10QEMdSWo8NAndPd4MFDxKlY7x6dFZP1Y/view?usp=sharing

### Note
- The .gitignore excludes large data, outputs, and environment files.
- The database (brazil_ecommerce.db) is regenerated from raw Kaggle CSVs via the ETL pipeline.
- Outputs such as plots, logs, and SQL exports are saved in the outputs/ directory automatically.
streamlit run dashboard/app.py
```
