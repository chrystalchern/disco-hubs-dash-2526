

```shell
conda create -n discovery python=3.13 streamlit pandas matplotlib numpy scipy plotly
```

```shell
python -m streamlit run Home.py
```

```
disco-hubs-dash-2526/
│
├── dashboard_engine.py         # Shared processing and UI rendering logic
├── ug_config.py             # Undergraduate configurations
├── grad_config.py           # Graduate configurations
│
├── Home.py                  # Main entry point
└── pages/
    ├── 1_Undergraduates.py  # UG UI Page
    └── 2_Graduates.py       # Grad UI Page
```