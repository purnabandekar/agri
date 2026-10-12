from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Agricultural Price Intelligence", page_icon="🌾", layout="wide")
st.title("🌾 Agricultural Price Intelligence")
st.caption("BDA project • Crop price trends • Market comparison • Experimental forecasting")
path = Path("data/market_prices.csv")
if not path.exists():
    st.error("Dataset missing. Run `python generate_data.py` in the project folder.")
    st.stop()

@st.cache_data
def load():
    d = pd.read_csv(path, parse_dates=["date"])
    for c in ["min_price","max_price","modal_price","arrival_tonnes","rainfall_mm"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.dropna(subset=["date","crop","market","modal_price"])
df = load()
st.warning("The included data is SYNTHETIC demo data, not real or live mandi prices. Replace it with verified data before making real-world recommendations.")
st.sidebar.header("Filters")
crops = sorted(df.crop.unique())
states = sorted(df.state.unique())
markets = sorted(df.market.unique())
sc = st.sidebar.multiselect("Crop", crops, default=crops[:3])
ss = st.sidebar.multiselect("State", states, default=states)
sm = st.sidebar.multiselect("Market", markets, default=markets)
dmin, dmax = df.date.min().date(), df.date.max().date()
dr = st.sidebar.date_input("Date range", value=(dmin,dmax), min_value=dmin, max_value=dmax)
f = df[df.crop.isin(sc) & df.state.isin(ss) & df.market.isin(sm)].copy()
if isinstance(dr,(tuple,list)) and len(dr)==2:
    f = f[(f.date.dt.date>=dr[0]) & (f.date.dt.date<=dr[1])]
if f.empty:
    st.info("No data matches these filters. Choose at least one crop, state, and market.")
    st.stop()
latest_date = f.date.max()
a,b,c,d = st.columns(4)
a.metric("Selected records", f"{len(f):,}")
b.metric("Average modal price", f"₹{f.modal_price.mean():,.0f}/quintal")
c.metric("Highest observed price", f"₹{f.modal_price.max():,.0f}/quintal")
d.metric("Latest record", latest_date.strftime("%d %b %Y"))
left,right = st.columns(2)
with left:
    st.subheader("Price trend over time")
    trend = f.groupby(["date","crop"],as_index=False).modal_price.mean()
    st.plotly_chart(px.line(trend,x="date",y="modal_price",color="crop",
        labels={"date":"Date","modal_price":"Modal price (₹/quintal)","crop":"Crop"}),use_container_width=True)
with right:
    st.subheader("Average price by market")
    avg = f.groupby("market",as_index=False).modal_price.mean().sort_values("modal_price",ascending=False)
    st.plotly_chart(px.bar(avg,x="market",y="modal_price",color="modal_price",
        labels={"market":"Market","modal_price":"Average price (₹/quintal)"}),use_container_width=True)
left,right = st.columns(2)
with left:
    st.subheader("Price distribution by crop")
    st.plotly_chart(px.box(f,x="crop",y="modal_price",color="crop",
        labels={"crop":"Crop","modal_price":"Modal price (₹/quintal)"}),use_container_width=True)
with right:
    st.subheader("Market arrivals vs price")
    st.plotly_chart(px.scatter(f,x="arrival_tonnes",y="modal_price",color="crop",
        hover_data=["market","date"],labels={"arrival_tonnes":"Arrivals (tonnes)","modal_price":"Modal price (₹/quintal)"}),use_container_width=True)
st.subheader("Selected market records")
st.dataframe(f.sort_values("date",ascending=False)[["date","state","market","crop","min_price","max_price","modal_price","arrival_tonnes"]],use_container_width=True,hide_index=True)
st.download_button("Download filtered CSV",data=f.to_csv(index=False).encode("utf-8"),
    file_name="filtered_agricultural_prices.csv",mime="text/csv")
with st.expander("Experimental model results (run analysis.py first)"):
    mf = Path("outputs/model_metrics.csv")
    pf = Path("outputs/test_predictions.csv")
    if mf.exists():
        st.dataframe(pd.read_csv(mf),use_container_width=True,hide_index=True)
        st.caption("Synthetic-data evaluation is for software demonstration only.")
        if pf.exists():
            st.dataframe(pd.read_csv(pf).head(100),use_container_width=True,hide_index=True)
    else:
        st.info("Run `python analysis.py` to create model reports.")
