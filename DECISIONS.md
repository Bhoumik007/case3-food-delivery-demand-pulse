# Decisions Log — Case 3: Food Delivery Demand Pulse

## Assumptions I Made

1. **Surge premium \= ₹20/order** — This is an industry-average incremental rider incentive for surge orders in Indian food delivery. The actual company's number may differ, but directionally the recommendations hold even at ₹10 or ₹30. I used ₹20 because it's the midpoint of the ₹15–25 range reported across Swiggy/Zomato rider earnings analyses.  
     
2. **Rider capacity \= \~3 orders/hour** — Used for the rider planning chart in the forecast tab. Based on typical urban delivery economics: 20 min average delivery \+ 10 min return/wait. This is conservative for high-density areas and aggressive for suburban routes.  
     
3. **Surge applied \= 1 means the rider incentive was elevated** — I interpreted this as a binary flag for whether the order triggered surge-level rider incentives, not customer-facing price surge (which may or may not be passed through). The recommendations focus on rider-side economics.  
     
4. **Off-peak hours have no genuine supply constraint** — This is an inference from delivery time data: off-peak average is 37 min vs peak 44 min, suggesting available rider supply is adequate during non-peak hours. Without direct rider availability data, this is the strongest proxy available.  
     
5. **Weekend and weekday dinner demand being identical implies the surge difference is supply-driven** — If demand is the same but surge is 27pp higher, the most likely explanation is fewer riders online on weekends, triggering the surge algorithm more aggressively. The fix should target supply (shift bonuses) not demand (pricing).

## Trade-offs

| Choice | Alternative | Why I Picked This |
| :---- | :---- | :---- |
| Trend \+ Seasonal decomposition for forecast | Prophet / ARIMA / SARIMAX | The data shows essentially no trend (-0.13 orders/day) and stable weekly patterns. Adding model complexity would not improve a 7-day forecast on this data. Simpler model \= easier for the Ops Head to understand and trust. I'd switch to Prophet if external covariates (weather, holidays) become available. |
| Streamlit for dashboard | Metabase / Looker / Jupyter widgets | Streamlit deploys in minutes to HF Spaces (free), is interactive, and produces a URL the Ops Head can bookmark. Metabase requires a database backend. Looker requires enterprise licensing. Jupyter widgets aren't shareable with non-technical stakeholders. |
| Plotly for charts | Matplotlib only / Altair / D3 | Plotly produces interactive charts (hover, zoom) that work in both the notebook and the Streamlit dashboard without code changes. Matplotlib is static. D3 is overkill for this use case. |
| ₹20 surge premium assumption | Ask for real data / use a range | A single point estimate makes the recommendations concrete and actionable. I noted the assumption explicitly and stated that the direction holds across a ₹10–30 range. A range-based recommendation ("savings of ₹15K–45K") is less actionable for a Monday morning decision. |
| No external data augmentation | Add weather API, holiday calendar | The brief said I "may augment with public data if you justify it." I chose not to because: (1) the 90-day window (Jan–Mar) has minimal weather variation in Indian metros, (2) no major national holidays fall in this window that would create demand spikes, and (3) adding weather would complicate the model without meaningfully changing the surge policy recommendations, which are structural (weekend vs weekday, off-peak waste), not weather-dependent. |

## What I De-Scoped and Why

- **City-level individual forecasts** — The hourly patterns are identical across all 7 cities (same shape, different scale). City-level forecasts would be proportional scaling of the aggregate forecast. Included city-level hourly averages in the rider planning section instead.  
- **Cuisine-level analysis** — Cuisines are evenly distributed (\~5.5K orders each) with no meaningful variation in surge rates or delivery times. Not actionable for surge pricing policy.  
- **Cohort analysis over time** — The daily order trend is flat (556 ±24 orders/day). No user acquisition or retention dynamics visible in this dataset. A cohort view would add noise, not signal.  
- **Streamlit dashboard with city-level drill-down tabs** — De-scoped in favour of sidebar filters that achieve the same result with less UI complexity.

## What I'd Do Differently With Another Day

1. **Backtest the forecast** — Hold out the last 7 days, predict from day 83, measure MAPE and CI coverage. This validates the model before the Ops Head relies on it.  
2. **Build a surge simulation tool** — Let the Ops Head adjust surge thresholds by hour and day-type, and see the impact on estimated rider costs and delivery times in real-time.  
3. **Add a Streamlit tab for city-level deep dives** — Individual city pages with city-specific recommendations (e.g., Bangalore may need different surge caps than Kolkata due to volume differences).  
4. **Implement a Prophet model** — Not for better accuracy on this data, but to have a framework ready for when external covariates (monsoon, IPL, Diwali) become available.  
5. **Statistical significance testing on the weekend vs weekday surge difference** — Run a two-proportion z-test to confirm the 72% vs 45% difference is not random variation (it almost certainly isn't given the sample sizes, but the test adds rigour).

## AI Tools Used

- Claude (Anthropic) — Used for code generation, analysis structuring, and documentation drafting. All analytical decisions, data interpretations, and business recommendations were reviewed and validated by me against the actual data outputs.

