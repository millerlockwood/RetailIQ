# RetailIQ

RetailIQ is an end-to-end retail demand forecasting and inventory optimization platform.

The project uses Python, SQL, machine learning, Power BI, and Streamlit to forecast product demand and convert those forecasts into inventory replenishment recommendations.

## Business Problem

Retailers lose revenue when products are unavailable, but carrying too much inventory creates unnecessary storage costs and ties up working capital.

RetailIQ addresses the following question:

> How much of each product should each store order for the next 28 days to reduce stockouts while minimizing excess inventory costs?

## Planned Capabilities

- Automated Python data pipeline
- Relational SQL data warehouse
- Store-item demand forecasting
- Forecast model comparison
- Safety stock calculations
- Reorder point calculations
- Inventory order recommendations
- Inventory policy simulation
- Power BI executive dashboard
- Streamlit decision-support application

## Technology Stack

- Python
- Pandas
- NumPy
- SQL
- MySQL
- Scikit-learn
- LightGBM
- Power BI
- Streamlit
- Git
- GitHub

## Project Architecture

```text
Raw Data
   |
   v
Python ETL Pipeline
   |
   v
SQL Data Warehouse
   |
   v
Feature Engineering
   |
   v
Demand Forecasting
   |
   v
Inventory Optimization
   |
   v
Business Simulation
   |
   v
Power BI and Streamlit