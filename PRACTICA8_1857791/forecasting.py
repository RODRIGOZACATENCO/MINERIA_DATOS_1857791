import os
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error

os.makedirs("img", exist_ok=True)

df = pd.read_csv("track_data_final.csv", usecols=["album_release_date"])
df = df[df["album_release_date"].str.len() == 10]
months = pd.to_datetime(df["album_release_date"]).dt.to_period("M")

full_range = pd.period_range("2018-01", "2025-10", freq="M")
counts = months.value_counts().reindex(full_range, fill_value=0)

future_range = pd.period_range("2025-08", periods=12, freq="M")
all_periods = full_range[:91].append(future_range)
design = pd.DataFrame({"x": range(len(all_periods))}, index=all_periods)
dummies = pd.get_dummies(all_periods.month, prefix="m", drop_first=True).astype(int)
dummies.index = all_periods
design = sm.add_constant(design.join(dummies))

series = pd.DataFrame({"y": counts.values}, index=full_range).join(design)
trend_cols = ["const", "x"]
season_cols = list(design.columns)

train = series.iloc[:82]
test = series.iloc[82:]

trend_model = sm.OLS(train["y"], train[trend_cols]).fit()
season_model = sm.OLS(train["y"], train[season_cols]).fit()

results = pd.DataFrame(index=test.index.astype(str))
results["Actual"] = test["y"].values
results["Trend"] = trend_model.predict(test[trend_cols]).round(1).values
results["Trend + Month"] = season_model.predict(test[season_cols]).round(1).values
results["Naive"] = train["y"].iloc[-1]

print(f"Trend line: y = {trend_model.params['const']:.2f} + {trend_model.params['x']:.4f}x | p-value (x) = {trend_model.pvalues['x']:.4f}")
print(f"Trend + Month R2 (train) = {season_model.rsquared:.4f} | Trend R2 (train) = {trend_model.rsquared:.4f}")
print()
print("Test predictions:")
print(results.to_string())
print()

print("MAE (all 12 test months / first 9 months, without Aug-Oct 2025):")
for name in ["Trend", "Trend + Month", "Naive"]:
    mae_all = mean_absolute_error(results["Actual"], results[name])
    mae_9 = mean_absolute_error(results["Actual"].iloc[:9], results[name].iloc[:9])
    print(f"{name:14s} | MAE 12 = {mae_all:6.2f} | MAE 9 = {mae_9:6.2f}")
print()

errors = results[["Trend", "Trend + Month", "Naive"]].rsub(results["Actual"], axis=0)
errors.plot(kind="bar", figsize=(11, 5))
plt.axhline(0, color="black")
plt.ylabel("Error (actual - predicted)")
plt.title("Test Error per Month")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("img/error_por_mes.png", dpi=300)
plt.close()

final_data = series.iloc[:91]
final_model = sm.OLS(final_data["y"], final_data[trend_cols]).fit()
future = design.loc[future_range]
forecast = final_model.get_prediction(future[trend_cols]).summary_frame(alpha=0.05)
forecast = forecast[["mean", "obs_ci_lower", "obs_ci_upper"]].round(1)
forecast.columns = ["Forecast", "Lower 95%", "Upper 95%"]
forecast.index = future_range.astype(str)

print(f"Final model (2018-01 to 2025-07): y = {final_model.params['const']:.2f} + {final_model.params['x']:.4f}x | p-value (x) = {final_model.pvalues['x']:.4f}")
print("Forecast:")
print(forecast.to_string())
print(f"Total forecast = {forecast['Forecast'].sum():.0f} tracks")

excluded = series.iloc[91:]
plt.figure(figsize=(11, 6))
plt.scatter(final_data["x"], final_data["y"], alpha=0.6, label="Months used in fit")
plt.scatter(excluded["x"], excluded["y"], color="gray", alpha=0.6, label="Actual months excluded")
plt.plot(final_data["x"], final_model.predict(final_data[trend_cols]), color="red", label="Fit")
plt.plot(future["x"], forecast["Forecast"], color="green", linestyle="--", label="Forecast")
plt.fill_between(future["x"], forecast["Lower 95%"], forecast["Upper 95%"], color="green", alpha=0.2, label="95% prediction")
plt.axvline(90.5, color="black", linestyle=":")
labels = all_periods.astype(str)
plt.xticks(ticks=range(0, len(all_periods), 6), labels=labels[::6], rotation=90)
plt.title("Tracks Released per Month")
plt.xlabel("Year-month")
plt.ylabel("Number of tracks")
plt.legend()
plt.tight_layout()
plt.savefig("img/forecasting.png", dpi=300)
plt.close()
