import atproto
import datetime
import io
import numpy as np
import os
import yfinance as yf
from zoneinfo import ZoneInfo

USER = "vwce.bsky.social"
PASS = os.environ["VWCE_PASS"]
BSKY_CLIENT = atproto.Client()
BSKY_CLIENT.login(USER, PASS)

df = yf.Ticker("VWCE.DE").history(period='5y')
now = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
df["time_delta"] = (now - df.index).days
df = df[["time_delta", "Close"]]

time_delta_sel = np.array([0,30,365,5*365])
index_sel = np.empty_like(time_delta_sel)

for i, dt in enumerate(time_delta_sel):
    df_i = np.argmin(np.abs(df.time_delta - dt))
    index_sel[i] = df_i

price_sel = df.iloc[index_sel]["Close"].to_numpy()
price_now = price_sel[0]
diff = (price_sel[0] / price_sel[1:]) - 1
diff *= 100

date_string = now.strftime("%Y-%m-%d")

post_response = BSKY_CLIENT.send_post(
    text=(
        f"VWCE {date_string} closed at €{price_now:.2f}\n"
        f"1M {diff[0]:+.2f}% | 1Y {diff[1]:+.2f}% | 5Y {diff[2]:+.2f}%"
    ),
    langs=["en"]
)
