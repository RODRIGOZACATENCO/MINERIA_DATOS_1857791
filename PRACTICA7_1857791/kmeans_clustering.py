import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

os.makedirs("img", exist_ok=True)

columns = [
    "track_popularity",
    "track_duration_ms",
    "artist_popularity",
    "artist_followers",
    "album_total_tracks",
    "track_number",
    "explicit",
]
skewed_columns = ["artist_followers", "album_total_tracks", "track_number"]

df = pd.read_csv("track_data_final.csv", usecols=columns)
df = df.dropna()
df["explicit"] = df["explicit"].astype(int)

df_log = df.copy()
df_log[skewed_columns] = np.log1p(df_log[skewed_columns])

attempts = {
    "Attempt 1 (StandardScaler)": StandardScaler().fit_transform(df),
    "Attempt 2 (log1p + StandardScaler)": StandardScaler().fit_transform(df_log),
}

k_values = range(2, 11)
results = {}
for name, data in attempts.items():
    inertias = []
    silhouettes = []
    print(f"{name}:")
    for k_val in k_values:
        kmeans_eval = KMeans(n_clusters=k_val, random_state=42, n_init=10)
        labels = kmeans_eval.fit_predict(data)
        inertias.append(kmeans_eval.inertia_)
        silhouettes.append(silhouette_score(data, labels))
        print(f"k = {k_val:2d} | Inertia = {inertias[-1]:10.2f} | Silhouette = {silhouettes[-1]:.4f}")
    results[name] = (inertias, silhouettes)
    print()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for axis, (name, (inertias, silhouettes)) in zip(axes, results.items()):
    silhouette_axis = axis.twinx()
    axis.plot(k_values, inertias, marker="o", color="#1f77b4")
    silhouette_axis.plot(k_values, silhouettes, marker="s", color="#d62728")
    axis.set_xlabel("Number of clusters (k)")
    axis.set_ylabel("Inertia", color="#1f77b4")
    silhouette_axis.set_ylabel("Silhouette", color="#d62728")
    axis.set_title(name)
plt.tight_layout()
plt.savefig("img/metodo_codo_silhouette.png", dpi=300)
plt.close()

k = 4
scaled = attempts["Attempt 2 (log1p + StandardScaler)"]
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(scaled)

print(f"Final model (Attempt 2, k = {k}):")
print(f"Inertia = {kmeans.inertia_:.2f} | Silhouette = {silhouette_score(scaled, df['cluster']):.4f}")
print()
print("Tracks per cluster:")
print(df["cluster"].value_counts().sort_index())
print()
print("Cluster means (original values):")
print(df.groupby("cluster").mean().round(2).to_string())

df_scaled = pd.DataFrame(scaled, columns=columns)
df_scaled["cluster"] = df["cluster"].values

plt.figure(figsize=(10, 5))
sns.heatmap(df_scaled.groupby("cluster").mean(), annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title(f"Standardized Means per Cluster (k = {k})")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("img/promedios_cluster.png", dpi=300)
plt.close()

components = PCA(n_components=2, random_state=42).fit_transform(scaled)
plt.figure(figsize=(9, 6))
scatter_plot = plt.scatter(components[:, 0], components[:, 1], c=df["cluster"], cmap="viridis", alpha=0.4, s=10)
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title(f"K-Means Clusters Projected with PCA (k = {k})")
plt.legend(*scatter_plot.legend_elements(), title="Cluster")
plt.tight_layout()
plt.savefig("img/clusters_pca.png", dpi=300)
plt.close()

