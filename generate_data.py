from pathlib import Path
import numpy as np
import pandas as pd

# Generates synthetic demo data. It is NOT actual mandi prices.
OUT = Path("data")
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)
markets = {
    "Mumbai": ("Maharashtra", 1.05), "Pune": ("Maharashtra", 1.00),
    "Nashik": ("Maharashtra", 0.94), "Nagpur": ("Maharashtra", 0.97),
    "Delhi": ("Delhi", 1.08), "Jaipur": ("Rajasthan", 0.91),
    "Indore": ("Madhya Pradesh", 0.95), "Bengaluru": ("Karnataka", 1.03)
}
crops = {"Onion": (2200, .22), "Tomato": (1800, .34), "Potato": (1600, .12),
         "Wheat": (2600, .08), "Rice": (3200, .10), "Soybean": (4500, .15),
         "Cotton": (6800, .13), "Gram": (5200, .12)}
rows = []
for crop, (base, seasonal_strength) in crops.items():
    for market, (state, market_factor) in markets.items():
        for date in pd.date_range("2022-01-01", "2025-12-31", freq="7D"):
            angle = 2*np.pi*(date.month-1)/12
            trend = 1 + .045*((date.year-2022) + date.dayofyear/365)
            price = max(300, base*market_factor*(1+seasonal_strength*np.sin(angle+.8))*trend*rng.normal(1,.075))
            modal = round(price/10)*10
            rows.append({"date": date.strftime("%Y-%m-%d"), "state": state, "market": market,
                         "crop": crop, "min_price": round(modal*rng.uniform(.88,.97),2),
                         "max_price": round(modal*rng.uniform(1.03,1.15),2), "modal_price": float(modal),
                         "arrival_tonnes": round(float(rng.uniform(20,650)),2),
                         "rainfall_mm": round(float(max(0,rng.normal(5+15*np.sin(angle),12))),1)})
df = pd.DataFrame(rows).sort_values(["date","crop","market"])
df.to_csv(OUT/"market_prices.csv", index=False)
print(f"Created {len(df):,} synthetic records in {OUT/'market_prices.csv'}")
print("Demo data only — not live or official market prices.")
