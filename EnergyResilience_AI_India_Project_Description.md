# EnergyResilience AI — India

## 1. Project Overview

### Hackathon Problem Statement

**Problem Statement 1: AI-Driven Energy Supply Chain Resilience for Import-Dependent Economies**

The hackathon problem will implement the solution **specifically for India**.

India is a strong prototype target because the problem statement itself uses India's crude-import dependence and exposure to the Strait of Hormuz as its motivating context.

The prototype focuses on two illustrative directions:

1. **Geopolitical Risk Intelligence Agent**
2. **Adaptive Procurement Orchestrator**

The architecture and core algorithms should be designed cleanly enough that another economy could theoretically be added later.

---

# 2. Core Objective

Build an **AI-powered decision-intelligence platform for India's crude-oil supply chain** that answers:

> **When a geopolitical or logistics disruption threatens India's crude-oil imports, how severe is the risk, how much of India's procurement is exposed, and what alternative procurement strategy should be adopted?**

The core intelligence loop is:

```text
PUBLIC DATA
    ↓
GEOPOLITICAL EVENT DETECTION
    ↓
AI EVENT EXTRACTION
    ↓
RISK SCORING + CONFIDENCE
    ↓
INDIA SUPPLY-CHAIN EXPOSURE
    ↓
PROCUREMENT OPTIMIZATION
    ↓
STRATEGY COMPARISON
    ↓
EXPLAINABLE RECOMMENDATION
```

The project is specifically about **India's imported crude-oil procurement**

---

# 3. India-Specific Scope

The system should model:

- India's major crude-oil suppliers
- India's relevant import ports
- major maritime corridors and chokepoints affecting Indian crude imports
- supplier-to-India trade relationships
- route availability
- supplier capacity
- route capacity
- estimated procurement cost
- transit time
- geopolitical risk
- sanctions exposure
- India's crude demand/procurement requirement

The number of suppliers and routes should be determined from **India's actual/publicly available trade structure**.

Model these:

```text
India
  ↓
Identify major crude suppliers
  ↓
Select a manageable subset for the prototype
  ↓
Build India's procurement network
```

The prototype should contain enough major suppliers/routes to make optimization meaningful, while avoiding an attempt to model the entire global oil market.

India's supplier mix changes over time. For example, EIA reports Russia as India's largest crude source in 2023, with Middle Eastern countries supplying much of the remainder, demonstrating why the supplier network should be derived from data rather than hardcoded as a universal list. 

---

# 4. System Architecture

```text
                    PUBLIC DATA
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
      NEWS           SANCTIONS         TRADE /
      DATA             DATA          ENERGY DATA
        │                │                │
        └────────────────┼────────────────┘
                         ↓
              ┌─────────────────────┐
              │ GEOPOLITICAL RISK   │
              │ INTELLIGENCE AGENT  │
              └──────────┬──────────┘
                         ↓
                  RISK ASSESSMENT
                         ↓
              ┌─────────────────────┐
              │ INDIA CRUDE         │
              │ SUPPLY-CHAIN GRAPH  │
              └──────────┬──────────┘
                         ↓
                  SUPPLY EXPOSURE
                         ↓
              ┌─────────────────────┐
              │ PROCUREMENT         │
              │ OPTIMIZER           │
              └──────────┬──────────┘
                         ↓
               STRATEGY COMPARISON
                         ↓
              ┌─────────────────────┐
              │ EXPLAINABLE         │
              │ RECOMMENDATION      │
              └─────────────────────┘
```

---

# 5. Data Layer

This project should use **multiple public/free data sources** rather than relying on one large training dataset.

The core system is primarily a **data-fusion + risk-modelling + optimization system**, so a large supervised training dataset is not required.

## 5.1 News and Geopolitical Events

Potential sources:

- GDELT
- public RSS/news feeds
- other publicly available news/event datasets

Relevant topics include:

- Strait of Hormuz
- Red Sea
- Suez Canal
- crude oil
- sanctions
- tanker/shipping disruption
- geopolitical conflict
- port disruptions
- oil exports

The system should retrieve relevant events and convert them into structured geopolitical signals.

---

## 5.2 Sanctions Data

Use publicly available sanctions information, such as UN sanctions data.


Sanctions information should contribute a **sanctions exposure signal** for Indian suppliers/routes.

Example:

```text
Supplier / Country
       ↓
Relevant sanctions exposure
       ↓
Sanctions Risk Score
       ↓
Overall Supplier / Route Risk
```

---

## 5.3 India's Trade and Energy Data

Potential sources include:

- UN Comtrade
- U.S. Energy Information Administration (EIA)
- World Bank commodity-price data
- Indian government/public energy data where appropriate

Useful information includes:

- India's crude imports by origin country
- import volumes
- supplier shares
- historical changes in supplier mix
- crude production/import/export information
- oil prices
- relevant energy-market indicators

EIA's India analysis provides a useful baseline for India's crude-import structure and identifies major source regions.

---

## 5.4 India's Route and Supplier Dataset

Construct a focused representation of India's crude procurement network.

Each supplier/route should contain fields such as:

```text
supplier
supplier_country
origin_port
destination_port
corridor
distance
transit_time
capacity
estimated_cost
baseline_risk
sanctions_risk
current_allocation
```

Where exact public values are unavailable, estimated values may be used **only if explicitly documented as assumptions**.

The system must distinguish:

```text
Public fact
vs.
Derived value
vs.
Prototype assumption
```

---

# 6. Geopolitical Risk Intelligence Agent

## Objective

Convert unstructured geopolitical information into structured risk signals specifically relevant to **India's crude-oil supply chain**.

### Example input

> "Tensions have escalated around the Strait of Hormuz, raising concerns about crude-oil shipping disruptions."

### Example structured output

```json
{
  "event_type": "geopolitical_tension",
  "location": "Strait of Hormuz",
  "commodity": "crude_oil",
  "severity": 0.85,
  "disruption_probability": 0.72,
  "expected_duration_days": 14,
  "affected_corridor": "Hormuz",
  "india_relevance": 0.91
}
```

The AI layer should perform:

- event extraction
- event classification
- location identification
- commodity identification
- severity estimation
- disruption-probability estimation
- affected-corridor identification
- India-specific relevance assessment
- evidence summarization

The LLM should not determine India's final procurement allocation. It should provide structured geopolitical signals that are passed to the deterministic risk engine and procurement optimizer.

---

# 7. India-Specific ML Risk Engine

The system should use a machine-learning model to estimate the probability that an India-relevant crude-oil supply corridor will experience a significant disruption within a defined future window (for example, the next 7 days).

The ML model should learn from historical geopolitical, sanctions, logistics/shipping, energy-market, and corridor-level signals.

## Model Input Features

Potential features include:

- geopolitical event count
- conflict event count
- average/minimum GDELT Goldstein score
- geopolitical/news tone
- energy-related event frequency
- sanctions-related events
- events near the corridor
- events in relevant supplier countries
- sanctions exposure
- shipping/logistics activity changes where available
- oil-price changes/volatility
- historical corridor disruption frequency
- time since previous disruption

Features must only use information available before the prediction window to avoid data leakage.

## Prediction Target

The primary prediction target should be:

> Probability that the relevant corridor experiences a significant disruption within the next N days.

Example:

```text
Strait of Hormuz
P(disruption within 7 days) = 0.78

---

# 8. Evidence Confidence

Distinguish between:

- **Risk score** — severity of the estimated threat to India's supply.
- **Confidence** — strength/consistency of the evidence supporting that estimate.

Example:

```text
Hormuz Risk for India: 87/100
Confidence: 78%

Evidence:
News signals            82%
Sanctions signals       71%
Historical similarity   76%
India supply exposure   91%
```

---

# 9. Signal Conflict Detection

If different signals disagree, explicitly identify the conflict.

Example:

```text
⚠ CONFLICTING SIGNALS

News reports indicate severe disruption,
but available logistics indicators do not yet
show a comparable reduction in traffic.

Risk confidence reduced from 84% → 59%.
```

This should be implemented through structured signals/rules/statistical comparisons rather than relying entirely on an LLM.

---

# 10. India Crude Supply-Chain Graph

Represent India's crude procurement network as a graph.

Example:

```text
Saudi Arabia
      ↓
Ras Tanura
      ↓
Hormuz
      ↓
Indian Ocean
      ↓
Indian Port
      ↓
Indian Refinery / Demand
```

Alternative example:

```text
USA
 ↓
US Export Port
 ↓
Atlantic
 ↓
Cape of Good Hope
 ↓
Indian Ocean
 ↓
Indian Port
 ↓
Indian Refinery / Demand
```

Use **NetworkX** for the graph representation.

Nodes and edges should contain relevant attributes:

```text
supplier
country
port
corridor
capacity
distance
transit_time
cost
geopolitical_risk
sanctions_exposure
```

---

# 11. Supply Exposure Analysis

When a geopolitical disruption occurs, determine its impact specifically on India's crude procurement.

Calculate:

- affected suppliers
- affected routes
- percentage of India's modeled procurement exposed
- affected supply capacity
- additional expected cost
- additional transit time
- alternative available capacity

Example:

```text
Hormuz Risk for India: 87

Affected suppliers:
Supplier A ✓
Supplier B ✓
Supplier C ✗

Affected routes:
Route 1 ✗
Route 2 ✗
Route 3 ✓

India procurement exposed:
18%
```

The actual values must be calculated from the India-specific dataset.

---

# 12. Adaptive Procurement Orchestrator

Convert India's supply-chain risk into an actionable procurement strategy.

## Inputs

- India's crude demand/procurement requirement
- supplier capacity
- route capacity
- current supplier allocation
- procurement cost
- transit time
- geopolitical risk
- sanctions risk
- supplier concentration
- route availability

## Constraints

At minimum:

```text
Total supply >= India's required demand

Supplier allocation <= supplier capacity

Route allocation <= route capacity

Blocked routes = unavailable
```

---

# 13. Procurement Optimization

Formulate India's crude procurement as a constrained optimization problem.

Conceptually:

```text
Minimize:

    procurement cost
  + geopolitical risk penalty
  + transit-time penalty
  + supplier concentration penalty
```

Subject to:

```text
Total supply >= demand

Supplier allocation <= supplier capacity

Route allocation <= route capacity

Blocked routes = 0
```

Use **Google OR-Tools**.

The optimizer must produce the numerical supplier/route allocation.

---

# 14. Multi-Strategy Procurement

Generate multiple feasible procurement strategies for India instead of presenting one black-box answer.

## Cheapest Strategy

```text
Cost: ₹X
Risk: Y/100
Transit: Z days
```

## Balanced Strategy

```text
Cost: ₹X
Risk: Y/100
Transit: Z days
```

## Safest Strategy

```text
Cost: ₹X
Risk: Y/100
Transit: Z days
```

The system should recommend one strategy according to the selected objective and risk tolerance.

---

# 15. Risk-Tolerance Optimization

Allow the decision-maker to specify India's acceptable risk level.

```text
LOW ─────────●──────── HIGH
              35
```

Changing the risk tolerance should alter the optimization objective and potentially change India's procurement allocation.

Example:

### Low risk tolerance

```text
Supplier B → 50%
Supplier C → 30%
Supplier D → 20%
```

### High risk tolerance

```text
Supplier A → 60%
Supplier B → 25%
Supplier C → 15%
```

The actual allocations must be produced by the optimizer.

---

# 16. Supplier Diversification

The optimizer should avoid excessive dependence on a single crude supplier when diversification provides meaningful resilience.

Example:

### Concentrated strategy

```text
Supplier A  80%
Supplier B  10%
Supplier C  10%
```

### Diversified strategy

```text
Supplier A  45%
Supplier B  35%
Supplier C  20%
```

Quantify the tradeoff between:

- additional procurement cost
- reduced supplier concentration
- reduced geopolitical exposure
- increased resilience

---

# 17. Explainable Recommendation

Every recommendation should expose:

- supplier allocation
- route allocation
- expected cost change
- risk reduction
- transit-time impact
- constraints satisfied
- reasons for selection

Example:

```text
RECOMMENDED STRATEGY FOR INDIA

Supplier A → 30%
Supplier B → 45%
Supplier C → 25%

Cost impact: +6.2%
Risk reduction: 38%
Transit impact: +2.1 days

WHY?

✓ Reduced exposure to the affected corridor
✓ Maintained required crude supply
✓ Avoided excessive supplier concentration
✓ Lower sanctions exposure
✓ Fits selected risk tolerance
```

The explanation should be generated from actual risk and optimization outputs.

The LLM may convert structured results into natural language, but must not invent numerical results.

---

# 18. Recommendation Change Explanation

If feasible, compare the current procurement recommendation with a previous optimization result.

Example:

```text
Recommendation changed because:

+18  Hormuz risk increased
+11  Supplier A route exposure increased
 +7  Supplier A capacity decreased
 -5  Supplier B risk decreased
```

This allows the user to understand how changing geopolitical conditions affect India's procurement strategy.

---

# 19. Decision Window

Optionally estimate how urgently India should act.

Example:

```text
DECISION WINDOW: ~36 HOURS

0–12h
Monitor

12–24h
Secure alternative capacity

24–36h
Execute rerouting

>36h
Higher shortage exposure
```

Keep the model simple and transparent.

---

# 20. Frontend Requirements

Use:

- Angular
- TypeScript
- Apache ECharts
- Leaflet + OpenStreetMap
- Cytoscape.js for the interactive supply-chain graph;

The application should function as a **decision-intelligence command center specifically for India's crude procurement**.

## Main Dashboard

```text
ENERGY RESILIENCE AI
INDIA CRUDE SUPPLY

India Supply Risk: 71/100

Critical Chokepoints
Hormuz     87  HIGH
Red Sea    63  MEDIUM
Suez       41  MEDIUM

Latest Events
[Event cards]

India Procurement Exposure
18%

[ ANALYZE IMPACT ]
```

## Event Analysis

Display:

- event
- location
- severity
- disruption probability
- expected duration
- India relevance
- risk score
- confidence
- evidence
- conflicting signals where applicable

## Supply-Chain View

Display:

- Indian crude suppliers
- origin ports
- Indian destination ports
- routes
- chokepoints
- affected routes
- supply exposure

## Procurement View

Display:

- risk tolerance
- cheapest strategy
- balanced strategy
- safest strategy
- recommended strategy
- supplier allocation
- route allocation
- cost/risk/transit tradeoffs
- recommendation explanation

---

# 21. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Angular + TypeScript + Vite |
| Backend | Python + FastAPI |
| LLM | Local open-source model via Ollama |
| NLP | Hugging Face / lightweight NLP tools |
| Data processing | Pandas + NumPy |
| ML if required | scikit-learn / XGBoost |
| Graph | NetworkX |
| Optimization | Google OR-Tools |
| Database | SQLite |
| Vector search if required | FAISS |
| Maps | Leaflet + OpenStreetMap |
| Charts | Recharts |
| Version control | Git + GitHub |



---

# 22. LLM vs Algorithmic Responsibilities

Maintain a clear separation.

## LLM / NLP

Responsible for:

- understanding unstructured news
- extracting structured geopolitical events
- classifying events
- identifying affected corridors
- summarizing evidence
- explaining recommendations

## Deterministic code / algorithms

Responsible for:

- India-specific risk scoring
- supply exposure
- graph calculations
- route feasibility
- procurement optimization
- supplier diversification
- cost/risk tradeoffs

### Core principle

```text
LLM = Understand + Explain

Algorithms = Calculate + Optimize + Decide
```

The LLM must not be the source of truth for numerical procurement decisions.

---

# 23. MVP Definition

The MVP is complete when it can reliably execute this workflow for **India**:

```text
1. Retrieve or select a geopolitical event
             ↓
2. Extract structured event information using AI
             ↓
3. Calculate India-specific supplier/corridor risk
             ↓
4. Determine India's supply-chain exposure
             ↓
5. Identify feasible alternative suppliers/routes
             ↓
6. Optimize India's procurement allocation
             ↓
7. Generate cheapest/balanced/safest strategies
             ↓
8. Explain the recommended strategy
```


The prototype should focus deeply on **India's crude-oil supply chain**.

---

# 25. Data and Modelling Principles

The project should clearly distinguish between:

### Public facts

Directly obtained from public datasets or authoritative sources.

### Derived values

Calculated from public data.

Example:

```text
Supplier share
Route exposure
Risk contribution
```

### Prototype assumptions

Estimated values used where public data is unavailable.

Example:

```text
Estimated route cost
Estimated transit time
Assumed route capacity
```

Assumptions should be documented rather than presented as real-world facts.

---

# 26. Final Project Description

### Short Description

> **EnergyResilience AI** is an AI-powered decision-intelligence platform for India's crude-oil supply chain. It fuses public geopolitical, sanctions, trade, and energy signals to assess disruption risk and uses constrained optimization to generate explainable, risk-aware procurement and rerouting strategies for India.

### Technical Description

> Built an AI-driven India-specific energy supply-chain resilience platform that extracts geopolitical disruption signals from public data, computes supplier and corridor risk, models India's crude procurement exposure, and formulates procurement rerouting as a constrained optimization problem using cost, capacity, transit time, geopolitical risk, and supplier concentration.

### Core Technical Areas

- LLM/NLP
- data ingestion and fusion
- India-specific risk modelling
- graph algorithms
- constrained optimization
- supply-chain modelling
- explainable AI
- full-stack development
- data visualization
- decision-support systems

---

# 27. Guiding Principle

Build the **smallest system that convincingly demonstrates the complete India-specific intelligence loop**:

> **Detect → Assess → Expose → Optimize → Explain → Act**
