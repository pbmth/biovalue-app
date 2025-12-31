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
    # --- TURVAPADI: Kui tulpa veel pole, loo see ajutiselt ---
    if 'Target_Area' not in df.columns:
        df['Target_Area'] = ""
    if 'Notes' not in df.columns:
        df['Notes'] = ""

    st.title("🦈 Shark Bio-Value Supplement Analyzer")
    
    # --- CALCULATION ENGINE ---
    df['Total_Price'] = pd.to_numeric(df['Price_Bottle'], errors='coerce').fillna(0) + pd.to_numeric(df['Shipping'], errors='coerce').fillna(0)
    df['Elemental_Amount_mg'] = df['Units_Total'] * df['Amount_per_Unit'] * df['Yield_Coeff']
    df['Absorbed_Amount_mg'] = df['Elemental_Amount_mg'] * df['Absorb_Coeff']
    
    # Vältimaks jagamist nulliga
    df['Price_per_Elemental_Gram'] = df['Total_Price'] / (df['Elemental_Amount_mg'] / 1000).replace(0, 1)
    df['PPAA_1g_Absorbed'] = (df['Total_Price'] / (df['Absorbed_Amount_mg'].replace(0, 0.000001))) * 1000

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter & Analyze")
    category = st.sidebar.selectbox("Select Supplement Type", df['Category'].unique() if 'Category' in df.columns else ["N/A"])
    
    filtered_cat = df[df['Category'] == category].copy() if 'Category' in df.columns else df.copy()
    
    # SMART TAG SYSTEM (split by '/')
    all_targets = set()
    # Puhastame andmed, et ei tekiks vigu
    target_data = filtered_cat['Target_Area'].fillna("").astype(str)
    for t in target_data.unique():
        if t.strip():
            parts = [p.strip() for p in t.split('/')]
            all_targets.update(parts)
    
    target_options = ["General Health"] + sorted(list(all_targets))
    target_filter = st.sidebar.selectbox("Select Target Area (Purpose)", target_options)

    view_level = st.sidebar.radio("Analysis Depth", 
                                 ["Level 1: Shelf Price", 
                                  "Level 2: Elemental ROI", 
                                  "Level 3: Shark Bio-Value (PPAA)"])

    # FILTREERIMINE
    if target_filter == "General Health":
        final_filtered = filtered_cat.copy()
    else:
        final_filtered = filtered_cat[filtered_cat['Target_Area'].str.contains(target_filter, na=False)].copy()

    # --- DESCRIPTION ---
    st.divider()
    if "Level 1" in view_level:
        sort_col = 'Total_Price'
        st.write("💡 **Level 1 (Shelf Price):** Comparing prices as seen on the shelf.")
    elif "Level 2" in view_level:
        sort_col = 'Price_per_Elemental_Gram'
        st.write("🔍 **Level 2 (Elemental ROI):** Shows the price of the raw active ingredient.")
    else:
        sort_col = 'PPAA_1g_Absorbed'
        st.write("🚀 **Level 3 (Shark Bio-Value):** Cost per gram of ingredient that actually reaches your system.")

    final_df = final_filtered.sort_values(by=sort_col, ascending=True)

    # --- DATA DISPLAY ---
    # Kontrollime, mis tulbad on olemas, et vältida uusi vigu
    base_cols = ['Brand', 'Form', 'Target_Area', 'Total_Price']
    display_cols = [c for c in base_cols if c in final_df.columns]
    
    if "Level 2" in view_level: display_cols.append('Price_per_Elemental_Gram')
    if "Level 3" in view_level: 
        display_cols.append('PPAA_1g_Absorbed')
        if 'Notes' in final_df.columns: display_cols.append('Notes')
    
    if 'URL' in final_df.columns: display_cols.append('URL')

    st.dataframe(
        final_df[display_cols],
        column_config={
            "URL": st.column_config.LinkColumn("Buy Now", display_text="Go to Store"),
            "Total_Price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "Price_per_Elemental_Gram": st.column_config.NumberColumn("$/Elem. g", format="$%.3f/g"),
            "PPAA_1g_Absorbed": st.column_config.NumberColumn("$/Absorb. g", format="$%.3f/g"),
        },
        use_container_width=True, hide_index=True
    )

    # --- SMART SHARK ANALYSIS ---
    if not final_filtered.empty:
        st.divider()
        shark_winner = final_filtered.sort_values(by='PPAA_1g_Absorbed', ascending=True).iloc[0]
        st.success(f"🏆 **SHARK'S CHOICE for {target_filter}:** {shark_winner['Brand']} ({shark_winner['Form']})")
        st.info(f"**Shark Insight:** Based on mathematical data, this is the most efficient way to invest in your health.")

else:
    st.info("Awaiting connection to Google Sheets data...")
