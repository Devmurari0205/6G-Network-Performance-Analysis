# 🚀 6G Network Performance Analysis for Smart Manufacturing

## 📌 Project Overview

This project analyzes the **impact of 6G network performance** (latency & packet loss) on **manufacturing efficiency, production speed, and product quality** in smart factories.

It provides **data-driven insights** using:

* Python (EDA & Analysis)
* SQL (Data querying)
* Tableau (Interactive dashboards)

---

## 📊 Dashboard Preview

### 🔹 Network Impact on Manufacturing Efficiency

![Dashboard 1](https://github.com/Devmurari0205/6G-Network-Performance-Analysis/blob/main/tableau/dashboard1.png)

### 🔹 Network Performance Overview

![Dashboard 2](images/dashboard2.png)

---

## 🎯 Problem Statement

Modern smart factories depend on **ultra-low latency communication**.
However, organizations struggle to identify:

* Whether efficiency loss is caused by **network issues or machine faults**
* Acceptable **latency thresholds**
* Impact of **packet loss on defects and errors**

---

## 📂 Dataset Features

* Machine performance metrics
* Network latency & packet loss
* Production speed & efficiency status
* Error rate & defect rate
* Operation modes (Active, Idle, Maintenance)

---

## 📈 Key KPIs

* **Avg Network Stability Index → 16.33**
* **Avg Network Latency → 25.6 ms**
* **High Efficiency Rate → 2.99%**
* **Avg Production Speed → 275.9 units/hr**
* **Avg Error Rate → 7.5%**

---

## 📊 Key Insights

### 🔴 Network Risk Analysis

* ⚠️ WARNING: 46,371 events
* 🟢 NORMAL: 41,488 events
* 🔴 CRITICAL: 12,141 events

➡️ Significant portion of operations are at **risk level**

---

### ⚡ Latency Impact

* Production speed slightly increases from low → high latency
* But **efficiency drops significantly at higher latency**

---

### 📉 Packet Loss Impact

* Higher packet loss leads to:

  * Increased error rate
  * Increased defect rate
* Strong correlation between **packet loss & quality issues**

---

### ⚙️ Operation Mode Insights

* **Active mode** contributes highest efficiency
* **Maintenance mode** is most sensitive to network instability

---

### 📊 Efficiency Distribution

* High Efficiency: 2,986
* Medium Efficiency: 19,189
* Low Efficiency: 77,825

➡️ Majority of operations fall under **low efficiency**

---

## 📊 Dashboard Features

### 🔹 Filters

* Operation Mode
* Packet Loss Category
* Latency Band
* Network Quality Tier
* Machine ID
* Time (Month/Date)

### 🔹 Visualizations

* Speed by Latency Band
* Efficiency by Latency Band
* Latency vs Speed Scatter
* Defect vs Packet Loss Scatter
* Network Stability Heatmap
* Risk Event Distribution
* Network Trend Analysis

---

## 🛠️ Tools & Technologies

* **Python** → Pandas, NumPy, Seaborn, Matplotlib
* **SQL** → Data transformation & querying
* **Tableau** → Interactive dashboard
* **Streamlit** → (Optional Web App)

---

## 🚀 How to Run

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/6G-Network-Performance-Analysis.git
cd 6G-Network-Performance-Analysis
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Notebook

```bash
jupyter notebook
```

### 4️⃣ (Optional) Run Streamlit App

```bash
streamlit run app/app.py
```

---

## 📌 Business Impact

* Helps optimize **network investments**
* Reduces **production inefficiencies**
* Prevents **misdiagnosis of machine failures**
* Improves **quality control & operational stability**

---

## 🔮 Future Enhancements

* Real-time IoT data integration
* Machine learning prediction model
* Automated alert system for network risks

---

## 👨‍💻 Author

**Harsh Devmurari**
📊 Aspiring Data Analyst | Data Science Enthusiast

---

## ⭐ Support

If you found this project useful, please ⭐ star the repository!
