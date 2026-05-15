# Case 3: Food Delivery Demand Pulse 📊

**Live demo:** https://huggingface.co/spaces/Bhoumik007/food-demand-dashboard  

## What This Is

A one-day investigation into surge pricing inefficiency for a regional food delivery company operating across 7 Indian cities. Analysed 50,000 orders over 90 days to identify when demand truly spikes, where surge pricing is misaligned with actual supply constraints, and what the Ops Head should change on Monday morning.

## The Headline Finding

**Weekend dinner surge is 72% vs weekday 45% — but order volumes are nearly identical.** The company is overpaying riders by \~₹89K/year on weekend dinner alone. Combined with off-peak surge waste and a reactive (not predictive) dinner ramp-up, three policy changes could save ₹4.1L annually.

## How to Run Locally

git clone https://github.com/YOUR\_USERNAME/case3-food-delivery-demand-pulse.git

cd case3-food-delivery-demand-pulse

pip install \-r requirements.txt

streamlit run app.py

Open [http://localhost:8501](http://localhost:8501)

## Deliverables

| Deliverable | File |
| :---- | :---- |
| Interactive Dashboard | `app.py` (Streamlit) |
| Analysis Notebook | `analysis_notebook.ipynb` |
| Forecast Output | `forecast_output.csv` |
| Exec Summary | `exec_summary.md` |
| Slide Deck | `deck.pdf` |
| Decisions Log | `DECISIONS.md` |

## Stack

| Tool | Why |
| :---- | :---- |
| **Python \+ Pandas** | Core analysis — fast, expressive, industry standard |
| **Plotly** | Interactive charts that work in both notebook and dashboard |
| **Streamlit** | Fastest path to a deployed, interactive dashboard the Ops Head can use |
| **Matplotlib/Seaborn** | Static charts for the notebook and deck |
| **NumPy** | Trend decomposition and forecast calculations |

## What's NOT Done

- **No external data augmentation** (weather, holidays, events) — justified in DECISIONS.md  
- **No advanced forecasting model** (Prophet, ARIMA) — the data is too stable to benefit; justified in the notebook  
- **No real-time pipeline** — this is a one-day analysis, not a production system

## In Production, I Would Also Add

- Real-time anomaly detection on daily order counts (alert when actuals deviate \>2σ from forecast)  
- Weather and holiday covariates in the forecast model  
- Rider supply data integration (online riders per hour per city) for direct supply-demand matching  
- City-level dynamic surge engine replacing fixed rules with real-time demand/supply ratio  
- Automated weekly reporting pipeline with Slack alerts for metric movements

## License

MIT  
