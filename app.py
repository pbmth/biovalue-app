import streamlit as st
import pandas as pd

# CONFIGURATION
st.set_page_config(page_title="Bio-Value Supplement Analyzer", layout="wide")

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

# Safety check for Target_Area column
if df is not None and 'Target_Area' not in df.columns:
    df['Target_Area'] = 'General'

if df is not None:
    st.title("🦈 Shark Bio-Value Supplement Analyzer")
    
    # --- CALCULATION ENGINE ---
    df['Total_Price'] = pd.to_numeric(df['Price_Bottle'], errors='coerce') + pd.to_numeric(df['Shipping'], errors='coerce')
    df['Elemental_Amount_mg'] = df['Units_Total'] * df['Amount_per_Unit'] * df['Yield_Coeff']
    df['Absorbed_Amount_mg'] = df['Elemental_Amount_mg'] * df['Absorb_Coeff']
    
    # Cost per 1g of elemental substance (Level 2)
    df['Price_per_Elemental_Gram'] = (df['Total_Price'] / (df['Elemental_Amount_mg'] / 1000))
    
    # Cost per 1g of absorbed substance (Level 3 - PPAA)
    df['PPAA_1g_Absorbed'] = (df['Total_Price'] / df['Absorbed_Amount_mg']) * 1000

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter & Analyze")
    category = st.sidebar.selectbox("Select Supplement Type", df['Category'].unique())
    filtered_cat = df[df['Category'] == category].copy()
    
    target_options = ["All Targets"] + sorted(list(filtered_cat['Target_Area'].unique()))
    target_filter = st.sidebar.selectbox("Select Target Area", target_options)

    view_level = st.sidebar.radio("Analysis Depth", 
                                 ["Level 1: Shelf Price", 
                                  "Level 2: Elemental ROI", 
                                  "Level 3: Shark Bio-Value (PPAA)"])

    # Apply filters
    if target_filter != "All Targets":
        final_filtered = filtered_cat[filtered_cat['Target_Area'] == target_filter].copy()
    else:
        final_filtered = filtered_cat.copy()

    # --- SORTING LOGIC ---
    if "Level 1" in view_level:
        sort_col = 'Total_Price'
        st.subheader(f"Level 1: Cheapest {category} for {target_filter}")
    elif "Level 2" in view_level:
        sort_col = 'Price_per_Elemental_Gram'
        st.subheader(f"Level 2: Best Elemental ROI for {target_filter}")
    else:
        sort_col = 'PPAA_1g_Absorbed'
        st.subheader(f"🦈 Level 3: {target_filter} Value Leader (Cost per Absorbed Gram)")

    final_df = final_filtered.sort_values(by=sort_col, ascending=True)

    # --- DATA DISPLAY ---
    # We use column configuration to make the URL a clickable button
    display_cols = ['Brand', 'Form', 'Target_Area', 'Total_Price']
    
    if "Level 2" in view_level:
        display_cols.append('Price_per_Elemental_Gram')
    if "Level 3" in view_level:
        display_cols.append('PPAA_1g_Absorbed')
    
    display_cols.append('URL') # Add URL at the end

    st.dataframe(
        final_df[display_cols],
        column_config={
            "URL": st.column_config.LinkColumn("Buy Now", display_text="Go to Store"),
            "Total_Price": st.column_config.NumberColumn("Total Price", format="$%.2f"),
            "Price_per_Elemental_Gram": st.column_config.NumberColumn("$/Elemental Gram", format="$%.3f/g"),
            "PPAA_1g_Absorbed": st.column_config.NumberColumn("$/Absorbed Gram", format="$%.3f/g"),
        },
        use_container_width=True,
        hide_index=True
    )

    # --- SHARK STRATEGIC ANALYSIS ---
    if len(final_df) > 0:
        st.divider()
        best_product = final_df.iloc[0]
        st.success(f"🏆 **CATEGORY LEADER for {target_filter}:** {best_product['Brand']} ({best_product['Form']})")
        st.info(f"**Shark Insight:** This product provides the most efficient investment for your health target.")
    else:
        st.warning("No products found for this specific filter.")

else:
    st.info("Awaiting connection to Google Sheets data...")
