- **Returns**: Executed trade price if successful, otherwise `None`.

---

## Trading Strategy

The bot runs continuously and adapts over **4 periods**:

### **Period 1** (0–1200s)
- Builds a baseline average price.
- After 5 minutes (`300s`), starts **selling**:
  - If `sell_avg < current_price < baseline_avg`: proportional sell.
  - If `current_price < sell_avg`: full sell of `100,000`.

---

### **Period 2** (1200–2400s)
- Builds new averages from scratch.
- After 2 minutes (`120s`), starts **buying**:
  - If `buy_avg > current_price > baseline_avg`: proportional buy.
  - If `current_price > buy_avg`: full buy of `100,000`.

---

### **Period 3** (2400–3480s)
- Similar to Period 2 but trades **both buy and sell**:
  - Buys if `current_price > baseline_avg`.
  - Sells if `current_price < baseline_avg`.
- Trades stop **2 minutes before the end (at 1080s).**

---

### **Period 4** (after 3480s)
- Final portfolio adjustment:
  - Converts 30% of total GBP equivalent holdings into EUR via `buy`.

---

## Key Variables
- `baseline_avg`: Rolling average of prices.
- `sell_avg`, `buy_avg`: Conditional averages for trade thresholds.
- `period`: Current trading phase (1–4).
- `GBP`, `EUR`: Current positions in each currency.

---

## Example Output
When running:
```
Expected to trade at: <latest price>
Effectively traded at: <executed price>
```

---

## Notes
- Each trading period **resets averages** at the start.
- Quantities are scaled proportionally depending on distance from averages.
- Trades are executed every second (`time.sleep(1)` loop).
