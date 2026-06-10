---
title: SDV Multi-Link Reliability Lab
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.37.0
app_file: app.py
pinned: false
license: mit
---

# SDV Multi-Link Reliability Lab

A research-oriented synthetic reliability demo for software-defined vehicle multi-link connectivity.

This project was built as a CV-ready portfolio project for PhD/research applications related to **multi-link communications for ultra-reliable connectivity in software-defined vehicles**.

## Important scope statement

This project is **not** a real SDV, ITS-G5, 5G, 6G, ns-3, OMNeT++, SUMO, or vendor-grade simulator.

It is a **synthetic reliability demo** that uses transparent KPI models to demonstrate how a software-defined vehicle connectivity controller could compare multiple communication links, detect degradation, and select the best currently available link.

## Features

- Streamlit dashboard with a clean research-lab style interface
- Synthetic scenario generator for vehicle connectivity
- Multi-link comparison across ITS-G5, 5G, and a 6G candidate link
- KPI-based reliability scoring
- Link degradation scenarios
- Button-based analysis execution
- CSV upload support
- Graphs and result tables
- Downloadable Markdown report
- Downloadable scored CSV
- Unit tests using pytest
- Dockerfile for Hugging Face Spaces

## Project structure

```text
sdv-multilink-reliability-lab/
├── app.py
├── src/
│   ├── config.py
│   ├── generator.py
│   ├── reliability.py
│   ├── reporting.py
│   └── ui.py
├── data/
│   └── sample_scenario.csv
├── tests/
│   ├── test_generator.py
│   └── test_reliability.py
├── requirements.txt
├── Dockerfile
├── pytest.ini
└── README.md
```

## How to run locally

```bash
cd sdv-multilink-reliability-lab
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

## How to use the dashboard

1. Open the app.
2. Use the sidebar to choose one of the internal pages:
   - Decision Dashboard
   - Graphs and Results
   - About and Help
3. In Scenario setup, choose the scenario type, affected link, time steps, and random seed.
4. Optionally upload a CSV file with your own synthetic KPI data.
5. Press **Run reliability analysis**.
6. Review the selected link, rejected links, reliability decision, and warning conditions.
7. Open **Graphs and Results** for KPI plots and tables.
8. Download the Markdown report or scored CSV.

## CSV upload format

A CSV upload must include:

```text
time_step, link, latency_ms, jitter_ms, packet_loss_pct, throughput_mbps, signal_quality, availability
```

## Reliability score interpretation

The reliability score is a synthetic index from 0 to 100.

Higher scores indicate better relative suitability for link selection inside this demo. The score combines packet loss, availability, latency, jitter, signal quality, and throughput.

Hard-fail rules can reject a link regardless of its score.

## CV positioning

Suggested CV bullet:

> Built an SDV Multi-Link Reliability Lab using Python, Streamlit, Pandas, NumPy, and pytest to demonstrate synthetic ITS-G5/5G/6G candidate link selection, failover reasoning, KPI-based reliability scoring, CSV scenario upload, and downloadable engineering reports for software-defined vehicle connectivity research.

## Hugging Face Space

For Hugging Face Spaces, select **Docker** as the Space SDK and push this repository to the Space remote.

```bash
git remote add hf https://huggingface.co/spaces/yasirsiddiq/sdv-multilink-reliability-lab
git push hf main
```

## License

MIT License.
