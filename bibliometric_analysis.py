# ===============================
# Bibliometric Analysis Script
# Incretin Hormone Research
# ===============================

# -------- IMPORTS --------
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from itertools import combinations
import plotly.express as px

# -------- SETTINGS --------
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
CURRENT_YEAR = 2025

# -------- DATA LOAD --------
df = pd.read_excel("Wos Dataset.xlsx")

# Sayısal dönüşümler
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Total Citations (All)"] = pd.to_numeric(df["Total Citations (All)"], errors="coerce")
df["5-Year IF"] = pd.to_numeric(df["5-Year IF"], errors="coerce")

# 2026'yı çıkar
df = df[df["Year"] != 2026]

# ===============================
# 1. ANNUAL PUBLICATION TREND
# ===============================
pub_by_year = (
    df.groupby("Year")
    .size()
    .reset_index(name="Publication Count")
)

sns.lineplot(
    data=pub_by_year,
    x="Year",
    y="Publication Count",
    marker="o"
)

plt.title("Annual Publication Trend")
plt.xlabel("Year")
plt.ylabel("Number of Publications")
plt.tight_layout()
plt.show()

# ===============================
# 2. JOURNAL IMPACT ANALYSIS
# ===============================
journal_stats = (
    df.groupby("Journal Name")
    .agg(
        Publications=("Article Title", "count"),
        Avg_Citations=("Total Citations (All)", "mean"),
        Avg_IF=("5-Year IF", "mean")
    )
    .dropna()
    .reset_index()
)

top10_journals = journal_stats.sort_values(
    "Publications", ascending=False
).head(10)

sns.scatterplot(
    data=top10_journals,
    x="Avg_IF",
    y="Avg_Citations",
    size="Publications",
    sizes=(200, 1200),
    alpha=0.8
)

plt.title("Impact Landscape of Top Journals")
plt.xlabel("Average 5-Year Impact Factor")
plt.ylabel("Average Citations")
plt.tight_layout()
plt.show()

# ===============================
# 3. KEYWORD TEMPORAL ANALYSIS
# ===============================
df_kw = df.copy()
df_kw["Author Keywords"] = df_kw["Author Keywords"].fillna("")

kw = (
    df_kw.assign(Keyword=df_kw["Author Keywords"].str.split(";"))
    .explode("Keyword")
)

kw["Keyword"] = kw["Keyword"].str.strip().str.lower()

top10_kw = kw["Keyword"].value_counts().head(10).index

kw_year = (
    kw[kw["Keyword"].isin(top10_kw)]
    .groupby(["Keyword", "Year"])
    .size()
    .unstack(fill_value=0)
)

sns.heatmap(
    kw_year,
    cmap="viridis",
    linewidths=0.3
)

plt.title("Temporal Evolution of Top Keywords")
plt.xlabel("Year")
plt.ylabel("Keyword")
plt.tight_layout()
plt.show()

# ===============================
# 4. KEYWORD CO-OCCURRENCE NETWORK
# ===============================
G = nx.Graph()

for kws in df["Author Keywords"].dropna():
    kw_list = [k.strip().lower() for k in kws.split(";") if k.strip()]
    for a, b in combinations(kw_list, 2):
        if G.has_edge(a, b):
            G[a][b]["weight"] += 1
        else:
            G.add_edge(a, b, weight=1)

top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:25]
top_nodes = [k for k, _ in top_nodes]

H = G.subgraph(top_nodes)
pos = nx.spring_layout(H, seed=42)

plt.figure(figsize=(14, 14))
nx.draw(
    H,
    pos,
    with_labels=True,
    node_size=1200,
    node_color="skyblue",
    edge_color="gray",
    font_size=9,
    alpha=0.85
)

plt.title("Keyword Co-occurrence Network")
plt.axis("off")
plt.show()

# ===============================
# 5. COUNTRY IMPACT (3D)
# ===============================
country_stats = (
    df.groupby("Country")
    .agg(
        Publications=("Article Title", "count"),
        Avg_Citations=("Total Citations (All)", "mean"),
        Avg_Year=("Year", "mean")
    )
    .dropna()
    .reset_index()
)

country_stats["Velocity"] = (
    country_stats["Avg_Citations"] /
    (CURRENT_YEAR - country_stats["Avg_Year"] + 1)
)

fig = px.scatter_3d(
    country_stats,
    x="Publications",
    y="Avg_Citations",
    z="Velocity",
    size="Publications",
    color="Country",
    title="3D Country Impact Landscape"
)

fig.show()

# ===============================
# 6. GLOBAL MAP
# ===============================
fig = px.scatter_geo(
    country_stats,
    locations="Country",
    locationmode="country names",
    size="Publications",
    color="Avg_Citations",
    projection="natural earth",
    title="Global Knowledge Power Map"
)

fig.show()
