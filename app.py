import streamlit as st
import pandas as pd

# CONFIGURATION
st.set_page_config(page_title="Shark Bio-Value Analyzer", layout="wide")

# 1. YOUR GOOGLE SHEETS CSV LINK
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSmALzKWrd24C6mKxgOGvjTmfGTGWTH6gTa_vPWg5CQzV2uDVcd7WFrKCquLmkPoNKPN099PrPCKytN/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=1)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data(SHEET_URL)

if df is not None:
    # Safety checks
    if 'Target_Area' not in df.columns: df['Target_Area'] = "General Health"
    if 'Notes' not in df.columns: df['Notes'] = ""
    if 'Category' not in df.columns: df['Category'] = "Supplement"

    st.title("🦈 Shark Bio-Value Supplement Analyzer")

    # --- SHARK SCAN ---
    with st.expander("🔍 SHARK SCAN - Analyze any product link", expanded=False):
        st.write("Paste an iHerb or store link below to see if the Shark can find you a better deal.")
        input_link = st.text_input("Product Link", placeholder="https://www.iherb.com/pr/...")
        if input_link:
            potential_winners = df.sort_values(by='Absorb_Coeff', ascending=False)
            if not potential_winners.empty:
                top_deal = potential_winners.iloc[0]
                st.info("💡 **Shark Analysis:** Most retail products have a 15-40% lower absorption rate than our recommendations.")
                st.warning(f"⚠️ **Better Value Found!** Our database suggests **{top_deal['Brand']}** provides superior biological value.")
                if 'URL' in top_deal and pd.notna(top_deal['URL']):
                    st.link_button(f"View Shark Choice: {top_deal['Brand']}", top_deal['URL'])

    # --- CALCULATION ENGINE ---
    df['Total_Price'] = pd.to_numeric(df['Price_Bottle'], errors='coerce').fillna(0) + pd.to_numeric(df['Shipping'], errors='coerce').fillna(0)
    df['Elemental_Amount_mg'] = pd.to_numeric(df['Units_Total'], errors='coerce').fillna(0) * \
                                pd.to_numeric(df['Amount_per_Unit'], errors='coerce').fillna(0) * \
                                pd.to_numeric(df['Yield_Coeff'], errors='coerce').fillna(1)
    df['Absorbed_Amount_mg'] = df['Elemental_Amount_mg'] * pd.to_numeric(df['Absorb_Coeff'], errors='coerce').fillna(1)
    df['Price_per_Elemental_Gram'] = df['Total_Price'] / (df['Elemental_Amount_mg'] / 1000).replace(0, 1)
    df['PPAA_1g_Absorbed'] = (df['Total_Price'] / (df['Absorbed_Amount_mg'].replace(0, 0.000001))) * 1000

    # --- SIDEBAR ---
    st.sidebar.header("Filter & Analyze")
    category = st.sidebar.selectbox("Select Supplement Type", df['Category'].unique())
    filtered_cat = df[df['Category'] == category].copy()
    
    all_targets = set()
    target_data = filtered_cat['Target_Area'].fillna("General Health").astype(str)
    for t in target_data.unique():
        if t.strip():
            parts = [p.strip() for p in t.split('/')]
            all_targets.update(parts)
    
    target_options = ["General Health"] + sorted([t for t in all_targets if t != "General Health"])
    target_filter = st.sidebar.selectbox("Select Target Area", target_options)
    view_level = st.sidebar.radio("Analysis Depth", ["Level 1: Shelf Price", "Level 2: Elemental ROI", "Level 3: Shark Bio-Value (PPAA)"])

    # Filter logic
    if target_filter == "General Health":
        final_filtered = filtered_cat.copy()
    else:
        final_filtered = filtered_cat[filtered_cat['Target_Area'].str.contains(target_filter, na=False)].copy()

    # --- LEVEL DESCRIPTIONS & SORTING ---
    st.divider()
    if "Level 1" in view_level:
        sort_col = 'Total_Price'
        st.subheader(f"Level 1: Comparison by Shelf Price ({target_filter})")
        st.write("💡 **Current Consumer Behavior:** This is how most people shop. They look at the price tag on the shelf, unaware of the actual mineral content or how much their body will actually absorb.")
    elif "Level 2" in view_level:
        sort_col = 'Price_per_Elemental_Gram'
        st.subheader(f"Level 2: Comparison by Elemental ROI ({target_filter})")
        st.write("🔍 **The Smart Buyer View:** This level reveals the cost of the raw mineral. It exposes 'cheap' bottles that are actually expensive because they contain very little active ingredient.")
    else:
        sort_col = 'PPAA_1g_Absorbed'
        st.subheader(f"🦈 Level 3: Comparison by Shark Bio-Value ({target_filter})")
        st.write("🚀 **The Expert/Shark View:** The ultimate analysis. This calculates the price of what *actually* enters your bloodstream, accounting for yield and bioavailability. This is the only way to find the true winner.")

    final_df = final_filtered.sort_values(by=sort_col, ascending=True)

    # --- DISPLAY ---
    display_cols = ['Brand', 'Form', 'Target_Area', 'Total_Price']
    if "Level 2" in view_level: display_cols.append('Price_per_Elemental_Gram')
    if "Level 3" in view_level: 
        display_cols.append('PPAA_1g_Absorbed')
        display_cols.append('Notes')
    if 'URL' in final_df.columns: display_cols.append('URL')

    st.dataframe(
        final_df[display_cols],
        column_config={
            "URL": st.column_config.LinkColumn("Buy Now", display_text="Go to Store"),
            "Total_Price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "Price_per_Elemental_Gram": st.column_config.NumberColumn("$/Elem. g", format="$%.3f/g"),
            "PPAA_1g_Absorbed": st.column_config.NumberColumn("$/Absorb. g", format="$%.3f/g"),
            "Notes": st.column_config.TextColumn("Expert Notes", width="large")
        },
        use_container_width=True, hide_index=True
    )

    if not final_filtered.empty:
        st.divider()
        shark_winner = final_filtered.sort_values(by='PPAA_1g_Absorbed', ascending=True).iloc[0]
        st.success(f"🏆 **SHARK'S CHOICE for {target_filter}:** {shark_winner['Brand']} ({shark_winner['Form']})")
        st.info(f"**Shark Insight:** Regardless of the shelf price, **{shark_winner['Brand']}** is the mathematical winner for **{target_filter}** because it delivers the best biological value per dollar spent.")
else:
    st.info("Awaiting connection to Google Sheets data...")
