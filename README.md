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

## ⚙️ Setup

### 1. Clone Repository
```
git clone https://github.com/yourusername/ecommerce_data.git
cd ecommerce_data
```

### 2. Download Data From Kaggle (https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Place csv files in:** data/raw/

### 3. Create Virtual Environment
```
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On Mac/Linux
```

### 4. Install Dependencies
```
pip install -r requirements.txt
```

## ▶️ Run Project

### Option 1. Windows
Run
```
run_project.bat
```
This will:
1. Create/activate the virtual environment (if not already created)
2. Install required dependencies (if not already installed)
3. Run the ETL pipeline to generate the SQLite database
4. Launch the Streamlit dashboard

### Option 2. Manual
Run
```
# Run ETL pipeline
python orchestration/etl_flow.py
```

### Note
- The .gitignore excludes large data, outputs, and environment files.
- The database (brazil_ecommerce.db) is regenerated from raw Kaggle CSVs via the ETL pipeline.
- Outputs such as plots, logs, and SQL exports are saved in the outputs/ directory automatically.
streamlit run dashboard/app.py
```
