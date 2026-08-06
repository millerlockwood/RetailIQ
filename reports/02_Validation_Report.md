# RetailIQ Validation Report

## Executive Summary

- Pipeline status: **PASSED**
- Validation score: **100/100**
- Checks passed: **13**
- Checks failed: **0**

> The validation score is based on documented rule-based checks and should be reviewed alongside the detailed results.

## Validation Summary

| Category | Check | Status | Severity | Result |
|---|---|---|---|---|
| Dataset Checks | Calendar duplicate rows | PASS | High | Calendar: No duplicate rows |
| Dataset Checks | Sales duplicate rows | PASS | High | Sales: No duplicate rows |
| Dataset Checks | Prices duplicate rows | PASS | High | Prices: No duplicate rows |
| Missing-Value Checks | Calendar missing values | PASS | Medium | Calendar: 7,542 expected missing values in event columns; no unexpected missing values |
| Missing-Value Checks | Sales missing values | PASS | Medium | Sales: No missing values |
| Missing-Value Checks | Prices missing values | PASS | Medium | Prices: No missing values |
| Business-Rule Checks | Negative selling prices | PASS | High | Sell Prices: No negative prices |
| Business-Rule Checks | Negative sales values | PASS | High | Sales: No negative sales |
| Relationship Checks | Calendar-pricing week relationship | PASS | High | All pricing weeks exist in Calendar |
| Relationship Checks | Price-item relationship | PASS | High | All priced items exist in Sales |
| Relationship Checks | Price-store relationship | PASS | High | All priced stores exist in Sales |
| Relationship Checks | Product-store pair relationship | PASS | High | All priced product-store pairs exist in Sales |
| Relationship Checks | Price business-key uniqueness | PASS | High | Prices: No duplicate business keys |

## Failed Checks

- No failed checks were detected.

## Recommendation

The primary raw datasets passed all current validation checks and may proceed to the cleaning stage.