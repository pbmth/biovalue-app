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
    st.title("🦈 Shark Bio-Value Supplement Analyzer")
    
    # --- CALCULATION ENGINE ---
    df['Total_Price'] = pd.to_numeric(df['Price_Bottle'], errors='coerce') + pd.to_numeric(df['Shipping'], errors='coerce')
    df['Elemental_Amount_mg'] = df['Units_Total'] * df['Amount_per_Unit'] * df['Yield_Coeff']
    df['Absorbed_Amount_mg'] = df['Elemental_Amount_mg'] * df['Absorb_Coeff']
    df['Price_per_Elemental_Gram'] = (df['Total_Price'] / (df['Elemental_Amount_mg'] / 1000))
    df['PPAA_1g_Absorbed'] = (df['Total_Price'] / (df['Absorbed_Amount_mg'] + 0.000001)) * 1000

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter & Analyze")
    category = st.sidebar.selectbox("Select Supplement Type", df['Category'].unique())
    filtered_cat = df[df['Category'] == category].copy()
    
    # SMART TAG SYSTEM (split by '/')
    all_targets = set()
    for t in filtered_cat['Target_Area'].dropna().unique():
        parts = [p.strip() for p in str(t).split('/')]
        all_targets.update(parts)
    
    # Vaikimisi valik on "General Health", mis näitab kõike
    target_options = ["General Health"] + sorted(list(all_targets))
    target_filter = st.sidebar.selectbox("Select Target Area (Purpose)", target_options)

    view_level = st.sidebar.radio("Analysis Depth", 
                                 ["Level 1: Shelf Price", 
                                  "Level 2: Elemental ROI", 
                                  "Level 3: Shark Bio-Value (PPAA)"])

    # FILTREERIMISE LOOGIKA: "General Health" näitab kõike, muud filtrid on spetsiifilised
    if target_filter == "General Health":
        final_filtered = filtered_cat.copy()
    else:
        final_filtered = filtered_cat[filtered_cat['Target_Area'].str.contains(target_filter, na=False)].copy()

    # --- DESCRIPTION ---
    st.divider()
    if "Level 1" in view_level:
        sort_col = 'Total_Price'
        st.write("💡 **Level 1 (Shelf Price):** Comparing prices as seen on the shelf. Does not account for dosage or quality.")
    elif "Level 2" in view_level:
        sort_col = 'Price_per_Elemental_Gram'
        st.write("🔍 **Level 2 (Elemental ROI):** Shows the price of the raw active ingredient before absorption.")
    else:
        sort_col = 'PPAA_1g_Absorbed'
        st.write("🚀 **Level 3 (Shark Bio-Value):** The absolute truth. Cost per gram of ingredient that actually reaches your system.")

    final_df = final_filtered.sort_values(by=sort_col, ascending=True)

    # --- DATA DISPLAY ---
    display_cols = ['Brand', 'Form', 'Target_Area', 'Total_Price']
    if "Level 2" in view_level: display_cols.append('Price_per_Elemental_Gram')
    if "Level 3" in view_level: 
        display_cols.append('PPAA_1g_Absorbed')
        display_cols.append('Notes')
    display_cols.append('URL')

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
        st.info(f"**Shark Insight:** Based on mathematical data, this is the most efficient way to invest in your health for this specific goal.")

else:
    st.info("Awaiting connection to Google Sheets data...")
