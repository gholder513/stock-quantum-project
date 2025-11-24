# 📘 Stock Movement Classification Using Classical & Quantum Models (2015–2020)

##  Developer Notes
Ran into early developmental issue where we had an unoriginal distribution of holds dominating our random forest output. This was due to our metrics being to agressive. For major S&P companies a 5% return change over a 10 day hold period is unlikely. I've been messing with changing our threshold to 3 and even 2% to encourage more volatility. We can also have our model give balanced weights but that will lower accuracy which I'm trying to stray away from doing if possible(changing class weights to balanced in our training function, class_weight="balanced").

For reference this was our original label distribution with 5% return and a 10 day hold period:
Label distribution:
label
HOLD    2173
BUY      536
SELL     273

After adjusting params:


frontend to be done:
Search Capability for Ticker Selection
Date Restriction(2015-2020)
Search Capability for model selection


Steps to retrain model:
cd backend
rm -rf data/processed/*
rm -f models/random_forest.pkl
python3 retrain.py

Already done: Create a Accuracy model(Random Forest):
To serve as our baseline and metric to determine our accuracy against different models
If a given model has the same determination as this one it is said to be accurate
Automate it so it can run on a range of dates with different models. Not specific dates only month and year to a future month and yearx (ex from March 2018 to Jan 2020)

TBD:
Add Logistic Regression Model
[text](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)

Add Variational Quantum Classifier model with Qiskit
[text](https://qiskit-community.github.io/qiskit-machine-learning/stubs/qiskit_machine_learning.algorithms.VQC.html)

Add CircuitQNN imports
[text](https://docs.pennylane.ai/en/stable/code/api/pennylane.qnn.TorchLayer.html)

Run via docker:
docker compose up --build

##  Project Overview

This project builds an end-to-end system that predicts **Buy**, **Hold**, or **Sell** signals for 200 publicly traded companies using historical stock market data from **2015–2020**. The classification system combines:

- **Classical machine learning models**
- **Quantum machine learning models** (simulated via quantum libraries)

The goal is to compare predictive accuracy between classical and quantum approaches using the **same feature set** and **same labeled dataset**.

The project includes:

- A **data pipeline** (download → feature engineering → labeling → dataset creation)
- Training **four models** (two classical, two quantum)
- A **FastAPI backend** that serves predictions
- A **React frontend** that visualizes predictions and comparisons

---

# 🧾 What Is a Ticker?

A **ticker** is the stock symbol used to identify a publicly traded company.

Examples:

| Company   | Ticker |
|-----------|--------|
| Apple     | AAPL   |
| Microsoft | MSFT   |
| Google    | GOOG   |

This project uses ~200 such tickers.

---

#  Data Source

All historical market data is retrieved from **Yahoo Finance** using the `yfinance` Python library.  
For each ticker, we download:

- Date  
- Open  
- High  
- Low  
- Close  
- Adjusted Close  
- Volume  

Raw data is saved as:
data/raw/<TICKER>_2015_2020.csv

---

# Feature Engineering (Only These Features Are Used)

The models are trained **only on engineered features**, not on raw OHLCV data.

## **1. Daily Return**

Measures change from the previous day:

\[
\text{return}_t = \frac{Close_t - Close_{t-1}}{Close_{t-1}}
\]

---

## **2. Moving Averages (MA5, MA10)**

Trend indicators:

- **MA5** = average closing price over the last 5 days  
- **MA10** = average closing price over the last 10 days  

---

## **3. Momentum Indicator (Choose One)**

### **Option A — 14-Day RSI (Relative Strength Index)**  
Normalized momentum indicator ranging from 0–100.

**OR**

### **Option B — Simple Momentum**
\[
\text{momentum}_{14} = Close_t - Close_{t-14}
\]

---

## **4. Volume Z-Score (20-Day)**

Standardizes trading volume:

\[
z = \frac{Volume_t - \mu_{20}}{\sigma_{20}}
\]

Where \( \mu_{20} \) and \( \sigma_{20} \) are the 20-day mean and standard deviation.

---

# 🔧 Normalization Strategy

After computing features, we normalize using one of two methods:

### **Option A — Per-Stock Z-Scaling (Recommended)**  
Each stock is normalized using only its own mean and standard deviation.

### **Option B — Global Scaling**  
Normalize across all stocks combined.

---

# Label Creation (Buy, Hold, Sell)

Labels are created using **only the price data and the features above**.

We define a prediction date **t** and a forecast horizon **H = 10 trading days**.

Compute:

\[
\text{future\_return} = \frac{Close_{t+H} - Close_t}{Close_t}
\]

Then assign labels:

- **BUY** → future return > **+5%**
- **SELL** → future return < **−5%**
- **HOLD** → everything between −5% and +5%

These labels become the ground truth for training all models.

---

#  Full Pipeline Summary

### **1. Choose 200 tickers**
Stored in a Python list.

### **2. Download raw data**
Saved to `data/raw/`.

### **3. Compute features**
Using only:

- daily return  
- MA5  
- MA10  
- RSI or momentum  
- volume z-score  

### **4. Compute labels**
Buy/Hold/Sell based on +5% / −5% thresholds over a 10-day horizon.

### **5. Save processed data**
Stored in `data/processed/`.

### **6. Combine all processed files**
This forms the training dataset.

### **7. Train four models**

#### **Classical Models**
1. Logistic Regression or Linear SVM  
2. Random Forest or XGBoost  

#### **Quantum Models (Simulated)**
3. Variational Quantum Classifier (VQC)  
4. Quantum Neural Network (QNN)

### **8. Backend (FastAPI)**
Endpoints:

- `/api/tickers`
- `/api/predict`

### **9. Frontend (React)**
Displays predictions and model comparisons.

---

# 📁 Project Structure

stock-quantum-project/
backend/
app/
main.py
config.py
schemas.py
models/
classical.py
quantum.py
data/
load_data.py
requirements.txt

data/
raw/
processed/

frontend/
src/
App.tsx
components/
services/api.ts
package.json

---

# Technologies Used

### **Backend**
- Python  
- FastAPI  
- scikit-learn  
- pandas  
- numpy  
- Qiskit or PennyLane  

### **Frontend**
- React  
- TypeScript  

### **Data**
- Yahoo Finance (`yfinance`)

---

# Project Goals

- Build a clean, reproducible dataset covering 2015–2020  
- Train classical and quantum ML models on identical data  
- Evaluate and compare Buy/Hold/Sell classification accuracy  
- Provide a full-stack system with an interactive UI  