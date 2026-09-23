# Experimentation Platform

An educational and professional project focused on **A/B Testing** and digital experimentation. Built from scratch to learn and apply data science concepts to business decisions.

---

## What is this project?

**Experimentation Platform** is a didactic platform that teaches how to design, execute, and analyze A/B tests. It is ideal for:

- **Data Science Students**: Learn experimentation fundamentals
- **Product Managers**: Understand the statistics behind decisions
- **Data Analysts**: Implement tests in production
- **Anyone interested in data-driven decisions**

---

## What is an A/B Test?

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

## Project Structure

```
experimentation-platform/
├── data/                          # Dataset storage
│   └── [synthetic and real datasets]
├── src/                           # Reusable code
│   └── [modules and utilities]
├── experiments/                   # Experimentation notebooks
│   ├── 01_synthetic.ipynb         # A/B testing fundamentals, statistical validation, CUPED, and power sizing
│   ├── 02_udacity_ab_test.ipynb   # Real-world applied A/B testing on Udacity experiment data (290,584 users)
│   └── 03_causal_inference.ipynb  # Causal inference beyond traditional A/B testing (ATE estimation)
├── app/                           # Web application (Streamlit)
│   └── [UI code]
└── README.md                      # This file
```

---

## PHASE 1 + PHASE 2 + PHASE 3 + PHASE 4: Fundamentals, Validation, CUPED and Sizing (COMPLETED)

### File: `experiments/01_synthetic.ipynb`

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

#### **PHASE 4: Experiment Design (Sizing)**
- Statistical Power Analysis with `statsmodels`
- Calculation of required sample size
- Understanding MDE (Minimum Detectable Effect)
- Pre-experiment planning to avoid underpowered tests

### Expected Results

| Metric | Result |
|---------|-----------|
| Control Users | ~5,000 |
| Treatment Users | ~5,000 |
| Conversion Rate (Control) | ~10% |
| Conversion Rate (Treatment) | ~12% |
| Uplift | +20% |

---

## APPLIED PHASE: A/B Testing with Real Data

### File: `experiments/02_udacity_ab_test.ipynb`

This notebook provides an industry-standard, end-to-end evaluation of an A/B test conducted by Udacity across **290,584 users**.

**Business Question:**
> "Does updating the landing page increase user conversion rate without compromising user experience or downstream engagement?"

#### **Methodology & Statistical Rigor:**
- Invariant metric validation (Sanity checks / Chi-Square goodness-of-fit).
- Two-proportion z-test and independent t-test comparison.
- 95% Confidence Interval estimation for Average Treatment Effect (ATE).
- Power and Minimum Detectable Effect (MDE) sizing.

---

## ADVANCED PHASE: Causal Inference Framework

### File: `experiments/03_causal_inference.ipynb`

This notebook extends traditional digital experimentation into **causal inference and observational causal modeling**:
- Potential Outcomes Framework (Rubin Causal Model).
- Average Treatment Effect (ATE) estimation.
- Addressing selection bias and unobserved confounding.
- Covariate balancing and propensity weighting intuition.
