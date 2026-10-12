import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

def load_dataset(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at: {file_path}")
    df = pd.read_csv(file_path)
    return df


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    n1, n2 = len(group1), len(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def compute_eta_squared(groups: list) -> float:
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)
    ss_total = float(np.sum((all_data - grand_mean) ** 2))
    ss_between = float(sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups))
    return float(ss_between / ss_total) if ss_total > 0 else 0.0


def compute_kruskal_eta_squared(h_stat: float, k: int, n: int) -> float:
    if n <= k:
        return 0.0
    return float((h_stat - k + 1) / (n - k))


def run_two_group_comparison(df: pd.DataFrame, value_col: str, group_col: str, label_map: dict = None):
    print("=" * 70)
    print(f"COMPARISON (2 GROUPS): {value_col} by {group_col}")
    print("=" * 70)

    unique_groups = df[group_col].dropna().unique()
    if len(unique_groups) != 2:
        raise ValueError(f"Expected exactly 2 groups, found {len(unique_groups)}")

    g1_val, g2_val = unique_groups[0], unique_groups[1]
    name1 = label_map.get(g1_val, str(g1_val)) if label_map else str(g1_val)
    name2 = label_map.get(g2_val, str(g2_val)) if label_map else str(g2_val)

    s1 = df[df[group_col] == g1_val][value_col].dropna().to_numpy()
    s2 = df[df[group_col] == g2_val][value_col].dropna().to_numpy()

    print("Sample Sizes and Group Statistics:")
    print(f"  - {name1}: n = {len(s1):,}, Mean = {np.mean(s1):.2f}, Median = {np.median(s1):.2f}, Std = {np.std(s1, ddof=1):.2f}")
    print(f"  - {name2}: n = {len(s2):,}, Mean = {np.mean(s2):.2f}, Median = {np.median(s2):.2f}, Std = {np.std(s2, ddof=1):.2f}")

    levene_res = stats.levene(s1, s2)
    equal_variances = levene_res.pvalue >= 0.05

    print("\n1. Test of Homogeneity of Variances (Levene):")
    print(f"   Statistic = {levene_res.statistic:.4f}, p-value = {levene_res.pvalue:.4e}")
    if equal_variances:
        print("   Result: Variances are equal (p >= 0.05).")
    else:
        print("   Result: Variances are NOT equal (p < 0.05, heteroscedasticity).")

    t_res = stats.ttest_ind(s1, s2, equal_var=False)
    print("\n2. Parametric Test (Welch's t-test, unequal variance):")
    print(f"   t-statistic = {t_res.statistic:.4f}, df = {t_res.df:.1f}, p-value = {t_res.pvalue:.4e}")

    mw_res = stats.mannwhitneyu(s1, s2, alternative="two-sided")
    print("\n3. Non-Parametric Test (Mann-Whitney U):")
    print(f"   U-statistic = {mw_res.statistic:.1f}, p-value = {mw_res.pvalue:.4e}")

    d_val = compute_cohens_d(s1, s2)
    print(f"\n4. Effect Size (Cohen's d): {d_val:.4f}")
    print(f"   Interpretation: {'Small' if abs(d_val) < 0.5 else 'Medium' if abs(d_val) < 0.8 else 'Large'} practical effect")
    print("-" * 70)


def run_multi_group_comparison(df: pd.DataFrame, value_col: str, group_col: str, group_order: list = None):
    print("=" * 70)
    print(f"COMPARISON (MULTI-GROUP): {value_col} by {group_col}")
    print("=" * 70)

    if group_order is None:
        groups_list = df[group_col].dropna().unique().tolist()
    else:
        groups_list = [g for g in group_order if g in df[group_col].unique()]

    samples = [df[df[group_col] == g][value_col].dropna().to_numpy() for g in groups_list]

    print("Sample Sizes and Group Statistics:")
    for name, sample in zip(groups_list, samples):
        print(f"  - {name}: n = {len(sample):,}, Mean = {np.mean(sample):.2f}, Median = {np.median(sample):.2f}, Std = {np.std(sample, ddof=1):.2f}")

    levene_res = stats.levene(*samples)
    equal_variances = levene_res.pvalue >= 0.05

    print("\n1. Test of Homogeneity of Variances (Levene):")
    print(f"   Statistic = {levene_res.statistic:.4f}, p-value = {levene_res.pvalue:.4e}")
    if equal_variances:
        print("   Result: Variances are equal (p >= 0.05).")
    else:
        print("   Result: Variances are NOT equal (p < 0.05, heteroscedasticity).")

    f_res = stats.f_oneway(*samples)
    print("\n2. Parametric Test (One-Way ANOVA):")
    print(f"   F-statistic = {f_res.statistic:.4f}, p-value = {f_res.pvalue:.4e}")

    kw_res = stats.kruskal(*samples)
    print("\n3. Non-Parametric Test (Kruskal-Wallis):")
    print(f"   H-statistic = {kw_res.statistic:.4f}, p-value = {kw_res.pvalue:.4e}")

    eta_sq_anova = compute_eta_squared(samples)
    eta_sq_kw = compute_kruskal_eta_squared(kw_res.statistic, len(samples), sum(len(s) for s in samples))

    print("\n4. Effect Sizes:")
    print(f"   Eta-squared (ANOVA): {eta_sq_anova:.4f} ({eta_sq_anova * 100:.2f}% of variance explained)")
    print(f"   Eta-squared (Kruskal-Wallis): {eta_sq_kw:.4f} ({eta_sq_kw * 100:.2f}% of variance explained)")
    print("-" * 70)


def generate_boxplots(df: pd.DataFrame, output_path: str = "analysis_boxplots.png"):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=150)

    exp_order = [False, True]
    exp_labels = ["Clean", "Explicit"]
    data_exp = [df[df["explicit"] == val]["track_popularity"].dropna() for val in exp_order]
    bp1 = axes[0].boxplot(data_exp, tick_labels=exp_labels, patch_artist=True)
    for box in bp1["boxes"]:
        box.set_facecolor("#2b7bba")
        box.set_alpha(0.85)
    axes[0].set_title("Track Popularity by Content (Explicit vs Clean)", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Content Type", fontsize=10)
    axes[0].set_ylabel("Track Popularity (pts)", fontsize=10)
    axes[0].grid(True, linestyle="--", alpha=0.5)

    album_order = ["album", "single", "compilation"]
    data_alb_pop = [df[df["album_type"] == val]["track_popularity"].dropna() for val in album_order]
    bp2 = axes[1].boxplot(data_alb_pop, tick_labels=album_order, patch_artist=True)
    for box in bp2["boxes"]:
        box.set_facecolor("#2b7bba")
        box.set_alpha(0.85)
    axes[1].set_title("Track Popularity by Album Type", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Album Type", fontsize=10)
    axes[1].set_ylabel("Track Popularity (pts)", fontsize=10)
    axes[1].grid(True, linestyle="--", alpha=0.5)

    data_alb_dur = [df[df["album_type"] == val]["track_duration_ms"].dropna() for val in album_order]
    bp3 = axes[2].boxplot(data_alb_dur, tick_labels=album_order, patch_artist=True)
    for box in bp3["boxes"]:
        box.set_facecolor("#2b7bba")
        box.set_alpha(0.85)
    axes[2].set_title("Track Duration (ms) by Album Type", fontsize=11, fontweight="bold")
    axes[2].set_xlabel("Album Type", fontsize=10)
    axes[2].set_ylabel("Duration (ms)", fontsize=10)
    axes[2].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    csv_file = "track_data_cleaned.csv"
    if not os.path.exists(csv_file):
        csv_file = os.path.join(os.path.dirname(__file__), "track_data_cleaned.csv")

    df = load_dataset(csv_file)
    print(f"Loaded dataset: {csv_file} with {len(df):,} tracks and {len(df.columns)} columns.\n")

    run_two_group_comparison(
        df=df,
        value_col="track_popularity",
        group_col="explicit",
        label_map={False: "Clean (False)", True: "Explicit (True)"}
    )

    run_multi_group_comparison(
        df=df,
        value_col="track_popularity",
        group_col="album_type",
        group_order=["album", "single", "compilation"]
    )

    run_multi_group_comparison(
        df=df,
        value_col="track_duration_ms",
        group_col="album_type",
        group_order=["album", "single", "compilation"]
    )

    generate_boxplots(df, "analysis_boxplots.png")

main()