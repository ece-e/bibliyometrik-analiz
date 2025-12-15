import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
df = pd.read_excel('Wos Dataset.xlsx')
pub_by_year = (
    df[df["Year"] != 2026]
    .groupby("Year")
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
plt.show()




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

plt.figure(figsize=(10,7))
sns.scatterplot(
    data=top10_journals,
    x="Avg_IF",
    y="Avg_Citations",
    size="Publications",
    sizes=(200, 1200),
    alpha=0.8
)

plt.title("Impact Landscape of Top 10 Journals in Incretin Hormone Research")
plt.xlabel("Average 5-Year Impact Factor")
plt.ylabel("Average Citations per Article")
plt.tight_layout()
plt.show()





# Keyword analizi için SADECE 2026'yı çıkar
df_kw = df[df["Year"] != 2026].copy()

df_kw["Author Keywords"] = df_kw["Author Keywords"].fillna("")

kw = (
    df_kw.assign(Keyword=df_kw["Author Keywords"].str.split(";"))
    .explode("Keyword")
)

kw["Keyword"] = (
    kw["Keyword"]
    .str.strip()
    .str.lower()
)

# En sık geçen 10 anahtar kelime
top10_kw = kw["Keyword"].value_counts().head(10).index

kw_year = (
    kw[kw["Keyword"].isin(top10_kw)]
    .groupby(["Keyword", "Year"])
    .size()
    .unstack(fill_value=0)
)

plt.figure(figsize=(12,6))
sns.heatmap(
    kw_year,
    cmap="viridis",
    linewidths=0.3
)

plt.title(
    "Temporal Evolution of Top 10 Keywords in Incretin Hormone Research",
    fontsize=14
)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Keyword", fontsize=12)

plt.tight_layout()
plt.show()


plt.figure(figsize=(10,6))
sns.boxplot(
    data=df,
    x="Year",
    y="Total Citations (All)"
)
plt.title("Distribution of Citations by Publication Year")
plt.xlabel("Year")
plt.ylabel("Total Citations")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)


import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations

G_kw = nx.Graph()

for kws in df["Author Keywords"].dropna():
    kw_list = [k.strip().lower() for k in kws.split(";") if k.strip()]
    for a, b in combinations(kw_list, 2):
        if G_kw.has_edge(a, b):
            G_kw[a][b]["weight"] += 1
        else:
            G_kw.add_edge(a, b, weight=1)

# En güçlü 25 keyword
top_kw = sorted(G_kw.degree, key=lambda x: x[1], reverse=True)[:25]
top_kw = [k for k, _ in top_kw]

H_kw = G_kw.subgraph(top_kw)

fig, ax = plt.subplots(figsize=(14, 14))

pos = nx.spring_layout(H_kw, seed=42)

nx.draw(
    H_kw,
    pos,
    ax=ax,
    with_labels=True,
    node_size=1200,
    node_color="skyblue",
    edge_color="gray",
    font_size=9,
    alpha=0.85
)

ax.set_title(
    "Keyword Co-occurrence Network in Incretin Hormone Research",
    fontsize=16,
    pad=20
)

ax.axis("off")
plt.show()


plt.figure(figsize=(10,6))
sns.boxplot(
    data=df,
    x="Year",
    y="Total Citations (All)"
)
plt.xticks(rotation=45)
plt.title("Citation Distribution by Publication Year")
plt.tight_layout()
plt.show()




import pandas as pd
import plotly.express as px

country_3d = (
    df.groupby("Country")
    .agg(
        Publications=("Article Title", "count"),
        Avg_Citations=("Total Citations (All)", "mean"),
        Avg_Year=("Year", "mean")
    )
    .reset_index()
    .dropna()
)

country_3d["Velocity"] = country_3d["Avg_Citations"] / (CURRENT_YEAR - country_3d["Avg_Year"] + 1)

fig = px.scatter_3d(
    country_3d,
    x="Publications",
    y="Avg_Citations",
    z="Velocity",
    size="Publications",
    color="Country",
    hover_name="Country",
    title="3D Country Impact Cloud",
    size_max=50
)

fig.update_layout(
    template="plotly_dark",
    scene=dict(
        xaxis_title="Publications",
        yaxis_title="Average Citations",
        zaxis_title="Citation Velocity"
    )
)

fig.write_html("3D_Country_Impact_Cloud.html")
fig.show()








import plotly.express as px

# Sayısal güvenlik
df["Total Citations (All)"] = pd.to_numeric(df["Total Citations (All)"], errors="coerce")
df["5-Year IF"] = pd.to_numeric(df["5-Year IF"], errors="coerce")

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

top10 = journal_stats.sort_values(
    "Publications", ascending=False
).head(10)

fig = px.scatter_3d(
    top10,
    x="Avg_IF",
    y="Avg_Citations",
    z="Publications",
    color="Avg_Citations",
    size="Publications",
    title="3D Journal Impact Landscape in Incretin Hormone Research"
)

fig.update_layout(
    template="plotly_white",
    scene=dict(
        xaxis_title="5-Year Impact Factor",
        yaxis_title="Average Citations",
        zaxis_title="Number of Publications"
    )
)

fig.show()




# Keyword özet tablo
kw_stats = (
    df.assign(Keyword=df["Author Keywords"].str.split(";"))
    .explode("Keyword")
)

kw_stats["Keyword"] = kw_stats["Keyword"].str.strip().str.lower()

kw_summary = (
    kw_stats.groupby("Keyword")
    .agg(
        First_Year=("Year", "min"),
        Avg_Citations=("Total Citations (All)", "mean"),
        Frequency=("Keyword", "count")
    )
    .dropna()
    .reset_index()
)

top_kw = kw_summary.sort_values(
    "Frequency", ascending=False
).head(15)

fig = px.scatter_3d(
    top_kw,
    x="First_Year",
    y="Avg_Citations",
    z="Frequency",
    color="Avg_Citations",
    size="Frequency",
    title="3D Keyword Impact Space in Incretin Hormone Research"
)

fig.update_layout(
    template="plotly_white",
    scene=dict(
        xaxis_title="First Appearance Year",
        yaxis_title="Average Citations",
        zaxis_title="Keyword Frequency"
    )
)

fig.show()







import pandas as pd
import matplotlib.pyplot as plt

# Çalışılacak anahtar kelimeler (TOPIC gibi düşünebilirsin)
keywords = [
    "diabetes",
    "diabetes mellitus",
    "glp-1",
    "liraglutide",
    "obesity",
    "semaglutide",
    "type 2 diabetes",
    "type 2 diabetes mellitus"
]

# Year ve Author Keywords temizliği
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df_kw = df[["Year", "Author Keywords"]].dropna()

# 2026'yı çıkar
df_kw = df_kw[df_kw["Year"] != 2026]

# Keyword–Year sayım tablosu
records = []

for _, row in df_kw.iterrows():
    year = row["Year"]
    kws = [k.strip().lower() for k in row["Author Keywords"].split(";")]
    for kw in keywords:
        if kw in kws:
            records.append([year, kw])

stream_df = pd.DataFrame(records, columns=["Year", "Keyword"])

stream_table = (
    stream_df
    .groupby(["Year", "Keyword"])
    .size()
    .unstack(fill_value=0)
    .sort_index()
)

# ---- GRAFİK ----
plt.figure(figsize=(12, 7))

plt.stackplot(
    stream_table.index,
    stream_table.T,
    labels=stream_table.columns,
    alpha=0.85
)

plt.title("Conceptual Evolution Stream of Incretin Hormone Research")
plt.xlabel("Year")
plt.ylabel("Number of Publications")

plt.legend(
    loc="upper left",
    bbox_to_anchor=(1.02, 1),
    frameon=False,
    title="Keyword"
)

plt.grid(False)
plt.tight_layout()
plt.show()









import pandas as pd
import plotly.express as px

df["Total Citations (All)"] = pd.to_numeric(
    df["Total Citations (All)"], errors="coerce"
)

country_stats = (
    df.groupby("Country")
    .agg(
        Publications=("Country", "count"),
        Avg_Citations=("Total Citations (All)", "mean")
    )
    .reset_index()
    .dropna()
)
fig = px.scatter_geo(
    country_stats,
    locations="Country",
    locationmode="country names",
    size="Publications",
    color="Avg_Citations",
    projection="natural earth",
    title="Global Knowledge Power Map of Incretin Hormone Research",
    color_continuous_scale="Plasma",
    size_max=40
)

fig.update_layout(
    template="plotly_white",
    geo=dict(
        showland=True,
        landcolor="white",
        showcountries=True,
        countrycolor="gray",
        showocean=True,
        oceancolor="white",
        showcoastlines=True,
        coastlinecolor="gray",
        bgcolor="white"
    )
)

fig.show()











import pandas as pd
import plotly.express as px

# Sayısal dönüşümler
df["5-Year IF"] = pd.to_numeric(df["5-Year IF"], errors="coerce")
df["Total Citations (All)"] = pd.to_numeric(
    df["Total Citations (All)"], errors="coerce"
)

journal_stats = (
    df.groupby("Journal Name")
    .agg(
        Publications=("Journal Name", "count"),
        Avg_Citations=("Total Citations (All)", "mean"),
        Impact_Factor=("5-Year IF", "mean")
    )
    .dropna()
    .reset_index()
)

# Kalabalığı azaltmak için en üretken 25 dergi
journal_stats = journal_stats.sort_values(
    "Publications", ascending=False
).head(25)
fig = px.scatter(
    journal_stats,
    x="Impact_Factor",
    y="Avg_Citations",
    size="Publications",
    color="Journal Name",
    title="Research Gravity Map: Journals in Incretin Hormone Research",
    size_max=45
)

fig.update_layout(
    template="plotly_white",   # 🔥 BEYAZ ARKA PLAN
    xaxis_title="Impact Factor (Gravity)",
    yaxis_title="Citation Pull (Average Citations)",
    legend_title="Journal Name"
)

fig.show()
