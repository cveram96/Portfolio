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

## ✅ PHASE 1 + PHASE 2 + PHASE 3: Fundamentals, Validation, and CUPED (COMPLETED)

### 📌 File: `experiments/01_synthetic.ipynb`

In this notebook, we built the **fundamentals of A/B testing** (PHASE 1) and its **statistical validation** (PHASE 2):

#### **Step 1: Import Libraries**
- pandas → Data manipulation
- numpy → Numerical operations
- matplotlib → Visualizations

#### **Step 2: Create Synthetic Dataset**
- Generated 10,000 users
- Random assignment: 50% control, 50% treatment
- Conversions based on binomial distribution
- **Probabilities used** (customizable):
  - Control: 10% conversion
  - Treatment: 12% conversion

#### **Step 3: `run_ab_test()` Function**
Implemented a function that calculates:
- **Conversion Rate**: Percentage of users who converted
- **Uplift**: Relative change in the metric
- Descriptive statistics per group

#### **Step 4: Run Experiment**
Executed the analysis and showed:
- Conversions per group
- Conversion rates
- Percentage uplift

#### **Step 5: Visualization**
Created a bar chart clearly comparing control vs treatment.

#### **Step 6: Explain the Problem** (PHASE 2)
Why uplift is not enough? Introducing the concept of "noise vs real effect".

#### **Step 7: Import scipy.stats** (PHASE 2)
Import advanced statistical library for hypothesis testing.

#### **Step 8: Implement T-Test** (PHASE 2)
Create `perform_t_test()` function to run the statistical test.
- Explains what a t-test does
- Defines p-value
- Teaches how to interpret results

#### **Step 9: Apply the Test** (PHASE 2)
Execute the function with control and treatment data.
- Show t-statistic
- Show p-value
- Provide initial interpretation

#### **Step 10: Interpretation of Results** (PHASE 2)
Explain the golden rule: p < 0.05 = significant.
- Type I Error (false positive)
- Type II Error (false negative)
- How to communicate results

#### **Step 11: Full Report** (PHASE 2)
Combine all metrics into a professional report:
- Conversion rates
- Uplift
- P-value
- Clear conclusion (Launch or not?)

#### **Step 12: Enhanced Visualization** (PHASE 2)
Chart with 95% confidence intervals.
- Show bars with error bars
- Visual indicator of significance
- Communicate uncertainty

#### **Step 13: CUPED Conceptual Explanation** (PHASE 3)
Introduction to variance reduction.
- What problem does CUPED solve?
- Noise vs real effect
- Intuition behind the algorithm

#### **Step 14: Pre-Experiment Variable** (PHASE 3)
Create covariate for CUPED.
- Simulate historical user behavior
- Create correlation between pre and post

#### **Step 15: Implement CUPED** (PHASE 3)
Function to adjust the metric.
- Explain θ (theta)
- Show the 3-step math
- Implement `apply_cuped()`

#### **Step 16: Apply CUPED** (PHASE 3)
Execute the adjustment.
- Calculate θ
- Create adjusted metric
- Show variance reduction

#### **Step 17: Repeat A/B Test** (PHASE 3)
Analysis with adjusted metric.
- Run t-test with CUPED data
- Compare p-values and t-statistics

#### **Step 18: Comparison Before vs After** (PHASE 3)
Comparison table.
- Show changes in all metrics
- Visualize CUPED impact

#### **Step 19: Impact Visualization** (PHASE 3)
Charts to show improvements.
- P-value reduction
- T-statistic improvement
- Reduced variance
- Distributions before/after

#### **Step 20: Deep Interpretation** (PHASE 3)
Full analysis of CUPED.
- Did the decision change?
- Is it more reliable?
- Answer critical questions
- Final recommendations

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
