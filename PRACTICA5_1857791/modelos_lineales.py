import os
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

DATASET_PATH = "track_data_cleaned.csv"
OUTPUT_DIR = "img"


def load_data(file_path: str) -> pd.DataFrame:
    """Load cleaned dataset from CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    return pd.read_csv(file_path)


def fit_linear_regression(x: pd.Series, y: pd.Series):
    """Fit an Ordinary Least Squares (OLS) linear model with intercept."""
    x_with_const = sm.add_constant(x)
    model = sm.OLS(y, x_with_const).fit()
    return model


def plot_regression(
    x: pd.Series,
    y: pd.Series,
    model,
    x_label: str,
    y_label: str,
    title: str,
    output_path: str,
):
    """Generate and save a scatter plot with fitted linear regression line."""
    plt.figure(figsize=(9, 6))
    plt.scatter(x, y, alpha=0.3, color="#1f77b4", label="Observed data")

    intercept, slope = model.params
    x_sorted = x.sort_values()
    y_pred = intercept + slope * x_sorted

    label_text = f"Linear Fit (R² = {model.rsquared:.4f})"
    plt.plot(x_sorted, y_pred, color="#d62728", linewidth=2, label=label_text)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved plot: {output_path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data(DATASET_PATH)

    print("Loaded dataset with", len(df), "rows.\n")

    # Define linear regression comparisons
    models_config = [
        {
            "id": 1,
            "name": "Model 1: Artist Popularity -> Track Popularity",
            "x_col": "artist_popularity",
            "y_col": "track_popularity",
            "x_label": "Artist Popularity",
            "y_label": "Track Popularity",
            "title": "Track Popularity vs Artist Popularity",
            "filename": "regression_artist_popularity_vs_track_popularity.png",
        },
        {
            "id": 2,
            "name": "Model 2: Artist Followers -> Track Popularity",
            "x_col": "artist_followers",
            "y_col": "track_popularity",
            "x_label": "Artist Followers",
            "y_label": "Track Popularity",
            "title": "Track Popularity vs Artist Followers",
            "filename": "regression_artist_followers_vs_track_popularity.png",
        },
        {
            "id": 3,
            "name": "Model 3: Artist Followers -> Artist Popularity",
            "x_col": "artist_followers",
            "y_col": "artist_popularity",
            "x_label": "Artist Followers",
            "y_label": "Artist Popularity",
            "title": "Artist Popularity vs Artist Followers",
            "filename": "regression_artist_followers_vs_artist_popularity.png",
        },
    ]

    for cfg in models_config:
        x = df[cfg["x_col"]]
        y = df[cfg["y_col"]]

        model = fit_linear_regression(x, y)

        intercept = model.params["const"]
        slope = model.params[cfg["x_col"]]
        p_val = model.pvalues[cfg["x_col"]]
        r_squared = model.rsquared

        print("=" * 60)
        print(cfg["name"])
        print("=" * 60)
        print(f"Observations: {int(model.nobs)}")
        print(f"R-squared:    {r_squared:.4f}")
        print(f"Intercept:    {intercept:.4f}")
        print(f"Slope:        {slope:.6e}")
        print(f"P-value:      {p_val:.4e}")
        print()

        plot_path = os.path.join(OUTPUT_DIR, cfg["filename"])
        plot_regression(
            x=x,
            y=y,
            model=model,
            x_label=cfg["x_label"],
            y_label=cfg["y_label"],
            title=cfg["title"],
            output_path=plot_path,
        )
        print()


if __name__ == "__main__":
    main()
