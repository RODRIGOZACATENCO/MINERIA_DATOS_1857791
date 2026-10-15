import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

os.makedirs("img", exist_ok=True)

columns = [
    "track_popularity",
    "track_duration_ms",
    "artist_popularity",
    "artist_followers",
    "album_total_tracks",
    "track_number",
    "album_type",
    "explicit",
]

df = pd.read_csv("track_data_cleaned.csv", usecols=columns)
df = df.dropna()

df["explicit"] = df["explicit"].astype(int)
df_encoded = pd.get_dummies(df, columns=["album_type"], drop_first=True)

X = df_encoded.drop(columns="explicit")
y = df_encoded["explicit"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Hyperparameter Evaluation:")
for k_val in [3, 5, 15, 31]:
    knn_eval = KNeighborsClassifier(n_neighbors=k_val)
    knn_eval.fit(X_train_scaled, y_train)
    pred_eval = knn_eval.predict(X_test_scaled)
    acc = accuracy_score(y_test, pred_eval)
    f1_macro = f1_score(y_test, pred_eval, average="macro")
    print(f"k = {k_val:2d} | Accuracy = {acc:.4f} | Macro F1 = {f1_macro:.4f}")
print()

k = 15
knn = KNeighborsClassifier(n_neighbors=k)
knn.fit(X_train_scaled, y_train)

y_pred = knn.predict(X_test_scaled)

print("Classification Report (k = 15):")
print(classification_report(y_test, y_pred, target_names=["Clean", "Explicit"], digits=4))

matrix = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(7, 5))
sns.heatmap(
    matrix,
    annot=True,
    fmt="d",
    xticklabels=["Clean", "Explicit"],
    yticklabels=["Clean", "Explicit"],
    cmap="Blues",
)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("KNN Confusion Matrix (k = 15)")
plt.tight_layout()
plt.savefig("img/matriz_confusion.png", dpi=300)
plt.close()
