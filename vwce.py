import atproto
import datetime
import io
import numpy as np
import os
import yfinance as yf
from zoneinfo import ZoneInfo

USER = "boglebot.bsky.social"
PASS = os.environ["VWCE_PASS"]
BSKY_CLIENT = atproto.Client()
BSKY_CLIENT.login(USER, PASS)

ticker_list = [
    "VWCE.DE",
    "IWDA.AS",
    "VUAA.MI",
    "CSPX.AS"
]
df = yf.download(ticker_list, period="1y")

ticker_columns = [("Close", x) for x in ticker_list]
df = df[ticker_columns]

now = datetime.datetime.now()
df["time_delta"] = (now - df.index).days

time_delta_sel = np.array([0,30,365])
index_sel = np.empty_like(time_delta_sel)

for i, dt in enumerate(time_delta_sel):
    df_i = np.argmin(np.abs(df.time_delta - dt))
    index_sel[i] = df_i

price_sel = df.iloc[index_sel]["Close"].to_numpy()
price_now = price_sel[0]
diff = (price_sel[0] / price_sel[1:]) - 1
diff *= 100

post_string = ""

for i, ticker in enumerate(ticker_columns):
    post_string += (
        f"{ticker[1][:4]} €{price_now[i]:.2f} (1M {diff[0,i]:+.1f}% | 1Y {diff[1,i]:+.1f}%)\n"
    )

post_response = BSKY_CLIENT.send_post(
    text=post_string[:-1],
    langs=["en"]
)
