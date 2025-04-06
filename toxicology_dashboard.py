import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 🚀 Load Data
# -----------------------------
full_df = pd.read_csv("all_tox_failed_trials.csv")
df_curated = pd.read_csv("curated_pubchem_drugs.csv")

# Ensure consistent data types
full_df["DrugName"] = full_df["DrugName"].astype(str)
df_curated["DrugName"] = df_curated["DrugName"].astype(str)

# Merge curated PubChem matches
df_merged = full_df.merge(df_curated, on="DrugName", how="left")
df_merged["Matched"] = df_merged["CID"].notna()

# -----------------------------
# 🔧 Sidebar Filters
# -----------------------------
st.sidebar.title("Filters")
only_matched = st.sidebar.checkbox("Show only PubChem-matched drugs", value=False)
tox_only = st.sidebar.checkbox("Show only toxicity-flagged entries", value=False)

# -----------------------------
# 🧬 Title + Description
# -----------------------------
st.title("🧬 Failed Drug Trial Explorer")
st.markdown("Use this interactive dashboard to explore failed small molecule drug trials with toxicology links. PubChem matches are highlighted and clickable.")

# -----------------------------
# 🔍 Apply Filters
# -----------------------------
filtered_df = df_merged.copy()
if only_matched:
    filtered_df = filtered_df[filtered_df["Matched"] == True]
if tox_only:
    filtered_df = filtered_df[filtered_df["toxicity_flag"] == True]

st.markdown(f"### Showing {len(filtered_df)} / {len(df_merged)} entries")

# -----------------------------
# 🔗 Helper for PubChem links
# -----------------------------
def linkify_pubchem(row):
    if row["Matched"]:
        return f"[{row['DrugName']}](https://pubchem.ncbi.nlm.nih.gov/compound/{int(row['CID'])})"
    return row["DrugName"]

# -----------------------------
# 📄 Display Table
# -----------------------------
display_df = filtered_df[["NCTId", "BriefTitle", "DrugName", "WhyStopped", "toxicity_flag", "Matched"]].copy()
display_df["DrugName"] = filtered_df.apply(linkify_pubchem, axis=1)

st.dataframe(display_df)

# -----------------------------
# 🧪 Optional: Show Molecule Images
# -----------------------------
if only_matched and not filtered_df.empty:
    st.markdown("### Drug Structures")
    for _, row in filtered_df.iterrows():
        if row["SMILES"]:
            st.markdown(f"**{row['DrugName']}**")
            st.image(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{int(row['CID'])}/PNG", width=250)
            st.markdown("---")

# -----------------------------
# 📊 Visual Insights
# -----------------------------
st.markdown("## 📊 Visual Insights")

# 🔘 Pie chart: PubChem Match Rate
match_counts = df_merged["Matched"].value_counts().rename({True: "Matched", False: "Unmatched"})
fig1, ax1 = plt.subplots()
ax1.pie(match_counts, labels=match_counts.index, autopct="%1.1f%%", startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

# 📊 Bar chart: Toxicology Keywords
st.markdown("### Top Toxicology Keywords")
tox_reasons = filtered_df["WhyStopped"].dropna().str.lower().str.cat(sep=" ")
keywords = ["toxicity", "adverse", "side effect", "liver", "renal", "cardiac", "fatal", "qt", "safety"]
counts = {kw: tox_reasons.count(kw) for kw in keywords}
fig2, ax2 = plt.subplots()
ax2.bar(counts.keys(), counts.values())
ax2.set_ylabel("Frequency")
ax2.set_title("Toxicology-related Keywords in 'WhyStopped'")
st.pyplot(fig2)
