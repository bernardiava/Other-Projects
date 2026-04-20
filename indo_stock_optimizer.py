"""Indonesian Stock Market Optimizer & Forecaster"""
import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta
import warnings
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
from scipy.optimize import minimize
import arch
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")
np.random.seed(42)

IDX_TICKERS = {
    "BBCA.JK": "Bank Central Asia", "BBRI.JK": "Bank Rakyat Indonesia",
    "BMRI.JK": "Bank Mandiri", "TLKM.JK": "Telkom Indonesia",
    "ICBP.JK": "Indofood CBP", "UNVR.JK": "Unilever Indonesia",
    "ASII.JK": "Astra International", "ADRO.JK": "Adaro Energy",
}

@st.cache_data(ttl=3600)
def fetch_stocks(start_date, end_date):
    data = {}
    for t in list(IDX_TICKERS.keys())[:8]:
        try:
            df = yf.download(t, start=start_date, end=end_date, progress=False, threads=True)
            if len(df) > 30: data[t] = df
        except: pass
    return data

def preprocess(df):
    df = df.ffill().bfill()
    df["Returns"] = df["Close"].pct_change()
    return df.dropna()

class RiskMetrics:
    @staticmethod
    def sharpe(r, rf=0.05):
        e = r - rf/252
        return (e.mean()*252)/(r.std()*np.sqrt(252)) if r.std()>0 else 0
    @staticmethod
    def max_dd(p):
        return abs(((p-p.cummax())/p.cummax()).min()*100)
    @staticmethod
    def var(r): return abs(np.percentile(r.dropna(), 5)*100)
    @staticmethod
    def cvar(r):
        v = RiskMetrics.var(r)
        t = r[r<=-v/100]
        return v if len(t)==0 else abs(t.mean()*100)

class PortfolioOptimizer:
    def __init__(self, rets):
        self.rets = rets
        self.n = len(rets.columns)
        self.mu = rets.mean()*252
        self.cov = rets.cov()*252
    def neg_sharpe(self, w):
        r = np.dot(w, self.mu)
        v = np.sqrt(np.dot(w.T, np.dot(self.cov, w)))
        return -(r/v) if v>0 else -np.inf
    def variance(self, w): return np.dot(w.T, np.dot(self.cov, w))
    def optimize(self, strat="max_sharpe"):
        cons = {"type":"eq", "fun":lambda x: np.sum(x)-1}
        bounds = tuple((0.,1.) for _ in range(self.n))
        init = np.array([1/self.n]*self.n)
        if strat=="min_volatility": res = minimize(self.variance, init, method="SLSQP", bounds=bounds, constraints=cons)
        else: res = minimize(self.neg_sharpe, init, method="SLSQP", bounds=bounds, constraints=cons)
        w = res.x
        pr = np.dot(self.rets, w)
        pp = (1+pr).cumprod()
        return {"weights":w, "expected_return":np.dot(w,self.mu), "volatility":np.sqrt(np.dot(w.T,np.dot(self.cov,w))),
                "sharpe_ratio":-self.neg_sharpe(w), "max_drawdown":RiskMetrics.max_dd(pp),
                "var_95":RiskMetrics.var(pr), "cvar_95":RiskMetrics.cvar(pr), "returns_series":pr, "prices_series":pp}

class ForecastingEngine:
    def __init__(self, data): self.data = data.dropna()
    def forecast_arima(self, days=30):
        m = SARIMAX(self.data, order=(2,1,2), seasonal_order=(1,1,1,5), enforce_stationarity=False)
        f = m.fit(disp=False).get_forecast(steps=days)
        d = pd.date_range(start=self.data.index[-1]+timedelta(days=1), periods=days, freq="B")
        r = f.predicted_mean[:days]; r.index = d[:len(r)]; return r
    def forecast_garch(self, days=30):
        rets = self.data.pct_change().dropna()*100
        g = arch.arch_model(rets, vol="GARCH", p=1, q=1).fit(disp="off")
        fc = g.forecast(horizon=days).variance.iloc[-1].values
        lp, mr = self.data.iloc[-1], rets.mean()
        prices = [lp]
        for i in range(days):
            dv = np.sqrt(fc[i]) if i<len(fc) else np.sqrt(fc[-1])
            prices.append(prices[-1]*(1+mr/100+np.random.normal(0,dv/100)))
        d = pd.date_range(start=self.data.index[-1]+timedelta(days=1), periods=days, freq="B")
        return pd.Series(prices[1:], index=d)
    def ensemble(self, days=30):
        res = {}
        try: res["ARIMA"] = self.forecast_arima(days)
        except: res["ARIMA"] = None
        try: res["GARCH"] = self.forecast_garch(days)
        except: res["GARCH"] = None
        valid = [v for v in res.values() if v is not None and len(v)>0]
        if valid: res["Ensemble"] = pd.DataFrame(valid).mean(axis=0)
        return res

def main():
    st.set_page_config(page_title="IDX Optimizer", page_icon="📈", layout="wide")
    st.markdown("# 🇮🇩 Indonesian Stock Market Optimizer")
    with st.sidebar:
        st.header("⚙️ Config")
        ds = st.date_input("Start", datetime.now()-timedelta(days=730))
        de = st.date_input("End", datetime.now())
        profile = st.selectbox("Risk", ["Conservative","Moderate","Aggressive"])
        strat = st.selectbox("Strategy", ["max_sharpe","min_volatility","balanced"])
        fc_days = st.selectbox("Forecast Days", [5,10,20,30])
        run = st.button("🚀 Run Analysis", use_container_width=True)
    if run:
        with st.spinner("Fetching..."): data = fetch_stocks(ds.strftime("%Y-%m-%d"), de.strftime("%Y-%m-%d"))
        if not data: st.error("No data"); return
        proc = {t:preprocess(df) for t,df in data.items()}
        rets_df = pd.DataFrame({t:df["Returns"] for t,df in proc.items()})
        metrics = []
        for t,df in proc.items():
            metrics.append({"Ticker":t, "Return (%)":((df["Close"].iloc[-1]/df["Close"].iloc[0])-1)*100,
                           "Sharpe":RiskMetrics.sharpe(df["Returns"]), "MaxDD (%)":RiskMetrics.max_dd(df["Close"]),
                           "Vol (%)":df["Returns"].std()*np.sqrt(252)*100, "VaR":RiskMetrics.var(df["Returns"])})
        met_df = pd.DataFrame(metrics).set_index("Ticker")
        opt = PortfolioOptimizer(rets_df)
        ports = {s:opt.optimize(s) for s in ["max_sharpe","min_volatility","balanced"]}
        sel = ports[strat]
        st.subheader("📊 Metrics")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Return", f"{sel['expected_return']*100:.2f}%")
        c1.metric("Sharpe", f"{sel['sharpe_ratio']:.2f}")
        c2.metric("Volatility", f"{sel['volatility']*100:.2f}%")
        c3.metric("Max DD", f"{sel['max_drawdown']:.2f}%")
        c4.metric("VaR 95%", f"{sel['var_95']:.2f}%")
        col1,col2 = st.columns(2)
        with col1:
            fig = go.Figure(data=[go.Pie(labels=list(proc.keys()), values=sel["weights"], hole=0.4)])
            fig.update_layout(title="Allocation", height=400)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            vols = [p["volatility"] for p in ports.values()]
            rets = [p["expected_return"] for p in ports.values()]
            fig = go.Figure(data=[go.Scatter(x=vols, y=rets, mode="markers+text", text=list(ports.keys()))])
            fig.update_layout(title="Risk-Return", height=400)
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("🔮 Forecasting")
        top3 = met_df.nlargest(3,"Sharpe").index.tolist()
        tabs = st.tabs(top3)
        all_fc = {}
        for i,t in enumerate(top3):
            with tabs[i]:
                eng = ForecastingEngine(proc[t]["Close"])
                fcs = eng.ensemble(fc_days)
                all_fc[t] = fcs
                if "Ensemble" in fcs and fcs["Ensemble"] is not None:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=proc[t]["Close"].tail(100).index, y=proc[t]["Close"].tail(100).values, name="Actual"))
                    for n,fc in fcs.items():
                        if fc is not None: fig.add_trace(go.Scatter(x=fc.index, y=fc.values, name=n, line=dict(dash="dash")))
                    fig.update_layout(title=f"{t} Forecast", height=400)
                    st.plotly_chart(fig, use_container_width=True)
        st.subheader("💡 Recommendations")
        recs = []
        for t,m in met_df.iterrows():
            sc = 0
            if m["Sharpe"]>1.5: sc+=3
            elif m["Sharpe"]>1: sc+=2
            elif m["Sharpe"]>0.5: sc+=1
            if m["MaxDD (%)"]<15: sc+=2
            elif m["MaxDD (%)"]<25: sc+=1
            recs.append({"Ticker":t, "Score":sc, "Rec":"BUY" if sc>=5 else "HOLD" if sc>=3 else "AVOID",
                        "Sharpe":m["Sharpe"], "MaxDD":m["MaxDD (%)"]})
        st.dataframe(pd.DataFrame(recs).sort_values("Score", ascending=False))
        st.info("⚠️ Educational only. Consult advisor.")
    else:

if __name__ == "__main__": main()
