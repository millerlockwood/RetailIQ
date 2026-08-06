# RetailIQ Business Requirements

## 1. Project Overview

RetailIQ is an end-to-end retail analytics platform designed to improve demand forecasting and inventory replenishment decisions.

The platform will use historical sales, product, store, pricing, calendar, and event data to predict future product demand and recommend inventory order quantities.

The project will combine Python, SQL, machine learning, inventory optimization, and business intelligence reporting.

---

## 2. Business Problem

Retailers must determine how much inventory each store should carry for thousands of products.

Ordering too little inventory can lead to:

- Stockouts
- Lost sales
- Reduced customer satisfaction
- Emergency replenishment costs

Ordering too much inventory can lead to:

- Excess holding costs
- Cash tied up in inventory
- Product markdowns
- Storage constraints
- Unsold or obsolete products

RetailIQ will address the following business question:

> How much of each product should each store order for the next 28 days to reduce stockouts while minimizing excess inventory costs?

---

## 3. Business Objectives

The primary objectives of RetailIQ are to:

1. Forecast product demand at the store and item level.
2. Identify products with high stockout risk.
3. Calculate recommended inventory order quantities.
4. Estimate safety stock and reorder points.
5. Compare current inventory policies with forecast-driven policies.
6. Measure the financial impact of improved inventory decisions.
7. Provide management with an interactive dashboard for decision-making.

---

## 4. Stakeholders

### Inventory Planning Manager

Uses demand forecasts and reorder recommendations to determine how much inventory should be purchased.

### Store Operations Manager

Monitors product availability, stockout risk, and inventory performance at individual stores.

### Merchandising Manager

Evaluates product performance, category trends, pricing behavior, and seasonal demand.

### Finance Manager

Reviews inventory carrying costs, lost sales, estimated savings, and return on inventory investment.

### Executive Leadership

Uses high-level KPIs and financial outcomes to evaluate whether the proposed inventory strategy should be adopted.

### Data and Analytics Team

Maintains the data pipeline, forecasting models, SQL warehouse, and reporting system.

---

## 5. Key Business Questions

RetailIQ will answer the following questions:

1. What is the expected demand for each product and store over the next 28 days?
2. Which products are most likely to experience a stockout?
3. Which products are carrying excessive inventory?
4. How much inventory should be ordered for each product and store?
5. How do holidays, events, prices, and seasonal patterns affect demand?
6. Which products have stable, volatile, intermittent, or declining demand?
7. Which forecasting model produces the most accurate predictions?
8. Does the most accurate forecasting model also produce the lowest inventory cost?
9. How much could the retailer save using forecast-driven inventory decisions?
10. Which inventory recommendations should be reviewed manually?

---

## 6. Project Scope

### In Scope

The first version of RetailIQ will include: 

- Historical daily sales data
- Product and category information
- Store and geographic information
- Historical product prices
- Calendar and event data
- Demand forecasting
- Forecast evaluation
- Inventory policy simulation
- Safety stock calculations
- Reorder point calculations
- Recommended order quantities
- SQL analytical queries
- Executive reporting
- Power BI and Streamlit dashboards

### Out of Scope

The first version will not include:

- Real-time point-of-sale data
- Actual supplier contracts
- Actual warehouse capacity data
- Actual shipment tracking
- Automated purchase order creation
- Employee scheduling
- Customer-level purchasing data
- Live production deployment
- Actual Walmart inventory records

These features may be included as future enhancements.

---

## 7. Initial Project Scope

To make the first version manageable, the initial model will focus on:

- One retail product category
- Three to five stores
- Approximately 100 to 300 products
- A 28-day forecast horizon
- Historical daily demand
- Two baseline forecasting methods
- One machine-learning forecasting model
- One inventory simulation

The platform may later be expanded to additional stores, categories, and products.

---

## 8. Key Performance Indicators

### Forecasting KPIs

- Mean Absolute Error
- Root Mean Squared Error
- Weighted Mean Absolute Percentage Error
- Forecast Bias
- Forecast Accuracy by Store
- Forecast Accuracy by Product Category

### Inventory KPIs

- Stockout Rate
- Fill Rate
- Estimated Lost Sales
- Excess Inventory Units
- Inventory Holding Cost
- Stockout Cost
- Total Inventory Cost
- Inventory Turnover
- Days of Inventory
- Recommended Order Quantity
- Safety Stock
- Reorder Point

### Financial KPIs

- Revenue at Risk
- Estimated Cost Savings
- Estimated Lost Revenue
- Inventory Investment
- Percentage Reduction in Inventory Cost
- Percentage Reduction in Stockouts

---

## 9. Success Criteria

The project will be considered successful if it:

1. Produces a repeatable Python data pipeline.
2. Loads cleaned and validated data into a relational SQL database.
3. Produces demand forecasts at the product-store level.
4. Outperforms at least one simple baseline forecast.
5. Converts forecasts into inventory recommendations.
6. Simulates the financial effect of alternative inventory policies.
7. Produces a dashboard that supports business decision-making.
8. Clearly documents assumptions, limitations, and model performance.
9. Can be reproduced by another analyst using the GitHub repository.
10. Provides clear recommendations that can be explained to nontechnical stakeholders.

---

## 10. Business Rules

The initial version of RetailIQ will use the following business rules:

1. Demand cannot be negative.
2. Recommended order quantity cannot be negative.
3. Products with missing or insufficient history may require a fallback forecasting method.
4. Safety stock will depend on forecast uncertainty, supplier lead time, and service-level targets.
5. Order recommendations will account for available inventory.
6. Forecasts will be evaluated using time-based validation.
7. Inventory policies will be compared using both statistical and financial metrics.
8. Products with highly irregular demand may require specialized treatment.
9. All simulated inventory values and costs must be clearly identified as assumptions.
10. The complete raw dataset will not be uploaded to GitHub.

---

## 11. Assumptions

Because the dataset does not include all operational inventory information, the first version will use documented assumptions for:

- Beginning inventory
- Supplier lead time
- Holding cost per unit
- Stockout cost per unit
- Target service level
- Ordering frequency
- Inventory review period
- Supplier reliability
- Replenishment timing

These assumptions will be stored separately so they can be changed during scenario analysis.

---

## 12. Constraints and Risks

### Data Limitations

The dataset contains sales history but does not provide complete real-world inventory records, supplier details, or actual ordering costs.

### Forecasting Risk

Unexpected events, promotions, shortages, and changes in customer behavior may reduce forecast accuracy.

### Modeling Risk

A model with strong forecast accuracy may not necessarily produce the lowest inventory cost.

### Scalability Risk

Modeling every product-store combination may require substantial processing time and memory.

### Assumption Risk

Inventory recommendations will depend on simulated operational assumptions that may differ from real retailer conditions.

---

## 13. Proposed Solution

RetailIQ will use the following workflow:

```text
Raw Retail Data
        |
        v
Python Data Validation and Transformation
        |
        v
SQL Data Warehouse
        |
        v
Exploratory Analysis and Feature Engineering
        |
        v
Demand Forecasting Models
        |
        v
Inventory Optimization Engine
        |
        v
Inventory Policy Simulation
        |
        v
Power BI and Streamlit Dashboards
        |
        v
Executive Recommendations