# Executive Summary: Surge Pricing Policy Review

**Prepared for:** Head of Operations  
**Date:** May 2026  
**Data:** 50,000 orders · 7 cities · 90 days (Jan–Mar 2025\)

---

## The Problem

The current surge pricing policy over-pays rider incentives during periods that don't require them and under-prepares supply for predictable demand spikes. Three structural inefficiencies are costing an estimated **₹4.1 lakh annually** in unnecessary rider incentives.

---

## Three Findings → Three Fixes

### 1\. Off-Peak Surge Is Wasteful (₹1.2L/year)

5.4% of orders during off-peak hours (midnight–11am, 2pm–5pm, 10pm–midnight) trigger surge pricing. Demand during these hours is 3–7× lower than peak. Delivery times are at baseline (37 min). There is no supply constraint.

**Fix:** Zero surge for hours outside 12–1pm and 6–9pm. Implement Monday. No risk.

---

### 2\. Weekend Dinner Surge Is 60% Higher Than Weekday — For the Same Demand (₹89K/year)

Weekend dinner (7–9pm) surge rate is **72%** vs weekday dinner at **45%**. But order volume per day is nearly identical: \~160 dinner orders/day on both weekdays and weekends. The over-surge is a supply problem (fewer riders on weekends), not a demand problem.

**Fix:** Cap weekend dinner surge at 50% immediately. Introduce a flat weekend shift bonus (₹200–300/day) to structurally improve weekend rider supply. Monitor p95 delivery time — if it exceeds 70 min, raise cap to 55%.

---

### 3\. The Pre-Dinner Ramp Is Reactive, Not Predictive (₹2.4L/year)

Demand jumps 52% from 6pm to 7pm. Surge rate jumps from 5.7% to 52.1% in the same hour. The system waits for supply exhaustion before triggering surge. Delivery times spike \+6 minutes at peak.

**Fix:** Use 5–6pm order velocity as a leading indicator. Send pre-position notifications to off-duty riders at 6:30pm, offering a dinner bonus (₹10–15/order — cheaper than ₹20 surge). A/B test in Bangalore for 4 weeks before rolling out.

---

## Combined Impact

| Recommendation | Annual Savings | Risk | Time to Implement |
| :---- | :---- | :---- | :---- |
| Eliminate off-peak surge | ₹1.2L | None | 1 day |
| Cap weekend dinner surge | ₹89K | Low | 1 week |
| Pre-position dinner riders | ₹2.4L | Medium (needs A/B test) | 4–6 weeks |
| **Total** | **₹4.1L** |  |  |

---

## 7-Day Forecast (April 1–7)

Demand is stable at \~550 orders/day with no growth trend. Day-of-week effects are small (±9 orders). The forecast for next week: 539–556 orders/day, with a 95% confidence interval of ±45 orders.

**Implication for rider scheduling:** No need to increase or decrease overall fleet capacity. Focus on redistributing existing supply to cover peak hours more efficiently — that's where the savings live.

---

## What I Need From You

1. **Real rider incentive data** — The ₹20 surge premium assumption should be calibrated with actuals.  
2. **Rider availability data** — Online riders per hour per city would let me confirm the supply-side interpretation directly.  
3. **Approval to A/B test Recommendation 3** in Bangalore starting next month.

