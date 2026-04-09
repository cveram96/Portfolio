# Experimentation Platform 🧪

An educational and professional project focused on **A/B Testing** and digital experimentation. Built from scratch to learn and apply data science concepts to business decisions.

---

## 📋 What is this project?

**Experimentation Platform** is a didactic platform that teaches how to design, execute, and analyze A/B tests. It is ideal for:

- 📚 **Data Science Students**: Learn experimentation fundamentals
- 💼 **Product Managers**: Understand the statistics behind decisions
- 📊 **Data Analysts**: Implement tests in production
- 🎯 **Anyone interested in data-driven decisions**

---

## 🎯 What is an A/B Test?

An **A/B test** is a controlled experiment where:

1. **The audience is divided** into two groups randomly
2. **The current version (Control)** is shown to one group and a variant (Treatment) to the other
3. **A metric is measured** (e.g., conversion rate, time on site, etc.)
4. **Results are compared** to make data-driven decisions

### Real Example:
An online store wants to know if changing the "Buy" button color from blue to orange increases sales.

- **Control (A)**: Blue button → 10% conversion
- **Treatment (B)**: Orange button → 12% conversion
- **Conclusion**: The orange button is better (+20% uplift)

---

## 📁 Project Structure

```
experimentation-platform/
├── data/                          # Dataset storage
│   └── [synthetic and real datasets]
├── src/                           # Reusable code
│   └── [modules and utilities]
├── experiments/                   # Experiment notebooks
│   ├── 01_synthetic.ipynb         # ← THEORETICAL PHASE: Synthetic Data (1-3) ✓
│   ├── 02_retail_ab_test.ipynb    # ← APPLIED PHASE: Real Data (UCI) 🆕
│   └── ...
├── app/                           # Web application (Streamlit)
│   └── [UI code]
└── README.md                      # This file
```

---

## ✅ PHASE 1 + PHASE 2 + PHASE 3 + PHASE 4: Fundamentals, Validation, CUPED and Sizing (COMPLETED)

### 📌 File: `experiments/01_synthetic.ipynb`

In this notebook, we built a complete experimentation workflow:

#### **PHASE 1: A/B Testing Fundamentals**
- Synthetic data generation (10,000 users)
- Binomial distribution modeling
- Basic metrics: Conversion Rate & Uplift
- Visualization of results

#### **PHASE 2: Statistical Validation**
- T-Test implementation with `scipy.stats`
- P-value interpretation (The Golden Rule: α = 0.05)
- Understanding Type I and Type II errors
- Enhanced visualization with 95% Confidence Intervals

#### **PHASE 3: Variance Reduction (CUPED)**
- Implementation of CUPED algorithm
- Covariate adjustment using pre-experiment data
- Mathematical intuition behind θ (theta)
- Impact analysis: p-value reduction and precision improvement

#### **PHASE 4: Experiment Design (Sizing) 🆕**
- Statistical Power Analysis with `statsmodels`
- Calculation of required sample size
- Understanding MDE (Minimum Detectable Effect)
- Pre-experiment planning to avoid underpowered tests

### 📊 Expected Results

| Metric | Result |
|---------|-----------|
| Control Users | ~5,000 |
| Treatment Users | ~5,000 |
| Conversion Rate (Control) | ~10% |
| Conversion Rate (Treatment) | ~12% |
| Uplift | +20% |

---

## 🔬 APPLIED PHASE: A/B Testing with Real Data 🆕

### 📌 File: `experiments/02_retail_ab_test.ipynb`

This notebook takes everything learned in PHASE 1-3 and **applies it to a real e-commerce dataset**.

**Business Question:**
> "Should we launch a UX/UI change that could increase the repeat purchase rate? For all customers or only for some?"

#### **Dataset: Online Retail (UCI Machine Learning Repository)**

Real data from a UK-based online store:
- 📊 541,909 transactions
- 👥 4,372 unique customers  
- 🛍️ 3,684 products
- 📅 Period: January 2010 - December 2011
