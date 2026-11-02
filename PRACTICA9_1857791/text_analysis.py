import os
import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import STOPWORDS, WordCloud

os.makedirs("img", exist_ok=True)

df = pd.read_csv("track_data_final.csv", usecols=["track_name", "album_type"])
df = df.dropna(subset=["track_name"])

words = df["track_name"].str.lower().str.findall(r"[a-z]+")

counts = Counter()
for word_list in words:
    counts.update(word_list)

domain_stopwords = {
    "feat", "version", "remix", "edit", "ft", "live", "radio", "mix", "deluxe",
    "s", "t", "m", "don", "ve", "re", "ll", "d"
}

baseline_counts = {k: v for k, v in counts.items() if k not in STOPWORDS}
filtered_counts = {
    k: v for k, v in baseline_counts.items()
    if k not in domain_stopwords and len(k) > 1
}

print("Attempt 1 Top 15:")
for word, freq in Counter(baseline_counts).most_common(15):
    print(f"{word:12s}: {freq}")
print()

print("Attempt 2 Top 15:")
for word, freq in Counter(filtered_counts).most_common(15):
    print(f"{word:12s}: {freq}")
print()

wordcloud = WordCloud(
    background_color="white", min_font_size=5, width=1920, height=1080
).generate_from_frequencies(filtered_counts)

plt.figure(figsize=(16, 9), dpi=120)
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.tight_layout(pad=0)
plt.savefig("img/word_cloud.png")
plt.close()

vec = CountVectorizer(ngram_range=(2, 2), max_features=5000, stop_words="english")
matrix = vec.fit_transform(df["track_name"])
bigram_totals = np.asarray(matrix.sum(axis=0)).ravel()
bigram_names = vec.get_feature_names_out()
bigram_counts = dict(zip(bigram_names, bigram_totals))

print("Top 15 Bigrams:")
for bigram, freq in Counter(bigram_counts).most_common(15):
    print(f"{bigram:22s}: {freq}")
print()

wordcloud_bigrams = WordCloud(
    background_color="white", min_font_size=5, width=1920, height=1080
).generate_from_frequencies(bigram_counts)

plt.figure(figsize=(16, 9), dpi=120)
plt.imshow(wordcloud_bigrams, interpolation="bilinear")
plt.axis("off")
plt.tight_layout(pad=0)
plt.savefig("img/word_cloud_bigramas.png")
plt.close()

df["length"] = df["track_name"].str.split().str.len()

print("Title Length by Album Type:")
print(df.groupby("album_type")["length"].describe().round(2).to_string())

plt.figure(figsize=(10, 6))
df.boxplot(column="length", by="album_type", figsize=(10, 6), showfliers=False)
plt.suptitle("")
plt.title("Track Name Length by Album Type")
plt.xlabel("Album Type")
plt.ylabel("Number of Words")
plt.tight_layout()
plt.savefig("img/boxplot.png")
plt.close()

