# Kraken Product Analytics — Insights Summary

This document contains key findings from the simulated Kraken Growth/Product Analytics project.

---

## 1) Activation Funnel KPIs (7-Day)

We measured early activation metrics for new users:

- **Deposit Conversion (7D):** 30.66%  
- **Trade Conversion (7D):** 21.40%  
- **Deposit → Trade Activation:** 69.81%

### Funnel Insight
A meaningful portion of users deposit but do not trade within their first week, representing an opportunity for onboarding and trading activation improvements.

---

## 2) Acquisition Channel Performance

### Deposit Conversion (7D)
Affiliate users had the strongest deposit conversion (~32%), while most channels clustered around ~30%.

### Trade Conversion (7D)
Paid Social and Affiliate showed the strongest early trading activation (~22%), while Influencer was the lowest (~19.7%).

### Deposit → Trade Activation
Paid Social achieved the highest deposit-to-trade activation (~71.8%), suggesting higher trading intent after funding.

---

## 3) Revenue & Monetization Insights

We analyzed trading fee revenue by acquisition channel.

- **Organic** drove the largest total fee volume due to scale.
- **Paid Social** delivered strong monetization efficiency (high ARPU).
- **Influencer** showed the highest ARPT, suggesting fewer but higher-value traders.

### Business Takeaway
Influencer traffic may attract high-value traders despite lower activation rate, making it a channel worth optimizing for quality rather than volume.

---

## 4) Retention (Cohorts + Curve)

We built retention cohorts (by signup week) and a retention curve for activated users:

- Retention shows sharp drop after Day 0, with gradual decay afterward.
- Weekly cohorts enable identifying onboarding/seasonality shifts impacting D1/D7/D30 retention.

### Business Takeaway
Retention is a key lever after activation; improving early lifecycle engagement is likely to compound into higher trading and fee outcomes.

---

## 5) Experiment Analysis — Onboarding A/B Test

We simulated an onboarding experiment measuring **7-day deposit conversion**.  
Observed results showed **no statistically significant lift** (z-test on proportions).

### Decision
The treatment onboarding flow does not support shipping as a conversion improvement without further iteration or targeting.

---

## 6) Experiment Planning (Power & Duration)

We estimated experiment requirements to detect a **+1pp lift** in deposit conversion at **95% confidence** and **80% power**:

- **Required sample size:** ~32,842 users per group (~65,684 total)
- Based on simulated signup volume (~166/day), this would require a long runtime, highlighting why:
  - larger expected lifts are easier to measure
  - high-traffic surfaces are preferred for experimentation

---

## Deliverables

- Multi-page **Streamlit dashboard** (Home, Funnel, Channels, Retention, Experiments)
- Gold tables in `/outputs` supporting dashboard + reproducible analysis
- End-to-end analytics workflow: KPI design → funnel → segmentation → monetization → retention → experimentation

---
