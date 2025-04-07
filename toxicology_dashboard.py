
import streamlit as st
import pandas as pd

# Load your full dataset and curated PubChem dataset
full_df = pd.read_csv("all_tox_failed_trials.csv")  # Your full 72-drug dataset
df_curated = pd.read_csv("curated_pubchem_drugs.csv")  # The 9 matched drugs

# Merge to flag matched drugs
full_df["DrugName"] = full_df["DrugName"].astype(str)
df_curated["DrugName"] = df_curated["DrugName"].astype(str)
df_merged = full_df.merge(df_curated, on="DrugName", how="left")
df_merged["Matched"] = df_merged["CID"].notna()

# Sidebar filters
st.sidebar.title("Filters")
only_matched = st.sidebar.checkbox("Show only PubChem-matched drugs", value=False)
tox_only = st.sidebar.checkbox("Show only toxicity-flagged entries", value=False)

# Main title
st.title("🧬 Drugs That Failed Based on Toxicology")
st.markdown("Use this interactive dashboard to explore failed small molecule drug trials with toxicology links. PubChem matches are highlighted and clickable.")

# Apply filters
filtered_df = df_merged.copy()
if only_matched:
    filtered_df = filtered_df[filtered_df["Matched"] == True]
if tox_only:
    filtered_df = filtered_df[filtered_df["toxicity_flag"] == True]

# Show results table
st.markdown(f"### Showing {len(filtered_df)} / {len(df_merged)} entries")

def linkify_pubchem(row):
    if row["Matched"]:
        return f"[{row['DrugName']}](https://pubchem.ncbi.nlm.nih.gov/compound/{int(row['CID'])})"
    return row["DrugName"]

# Prepare the display table
display_df = filtered_df[["NCTId", "BriefTitle", "DrugName", "WhyStopped", "toxicity_flag", "Matched"]].copy()
display_df["DrugName"] = filtered_df.apply(linkify_pubchem, axis=1)

# Show as interactive table
st.write(display_df.to_markdown(index=False), unsafe_allow_html=True)

# Optional: display structure
if only_matched and not filtered_df.empty:
    st.markdown("### Drug Structures")
    for _, row in filtered_df.iterrows():
        if row["SMILES"]:
            st.markdown(f"**{row['DrugName']}**")
            st.image(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{int(row['CID'])}/PNG", width=250)
            st.markdown("---")
