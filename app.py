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
        # Clean column names (remove hidden spaces)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data(SHEET_URL)

# Safety check for when you haven't added the 'Target_Area' column to Sheets yet
if df is not None and 'Target_Area' not in df.columns:
    df['Target_Area'] = 'General'

if df is not None:
    st.title("🦈 Shark Bio-Value Supplement Analyzer")
    st.write("Exposing the true biological value of supplements by segmenting them by their specific targets.")

    # --- CALCULATION ENGINE ---
    # Convert potential string numbers to floats and calculate
    df['Total_Price'] = pd.to_numeric(df['Price_Bottle'], errors='coerce') + pd.to_numeric(df['Shipping'], errors='coerce')
    df['Elemental_Amount_mg'] = df['Units_Total'] * df['Amount_per_Unit'] * df['Yield_Coeff']
    df['Absorbed_Amount_mg'] = df['Elemental_Amount_mg'] * df['Absorb_Coeff']
    
    # Cost per 1 gram (1000mg) of absorbed active ingredient
    df['PPAA_1g_Absorbed'] = (df['Total_Price'] / df['Absorbed_Amount_mg']) * 1000

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter & Analyze")
    
    # Filter 1: Supplement Category
    category = st.sidebar.selectbox("Select Supplement Type", df['Category'].unique())
    filtered_cat = df[df['Category'] == category].copy()
    
    # Filter 2: Target Area (Brain, Muscle, etc.)
    target_options = ["All Targets"] + sorted(list(filtered_cat['Target_Area'].unique()))
    target_filter = st.sidebar.selectbox("Select Target Area", target_options)

    # Filter 3: Complexity Level
    view_level = st.sidebar.radio("Analysis Depth", 
                                 ["Level 1: Shelf Price", 
                                  "Level 2: Elemental ROI", 
                                  "Level 3: Shark Bio-Value (PPAA)"])

    # Apply filters to the dataframe
    if target_filter != "All Targets":
        final_filtered = filtered_cat[filtered_cat['Target_Area'] == target_filter].copy()
    else:
        final_filtered = filtered_cat.copy()

    # --- SORTING LOGIC ---
    if "Level 1" in view_level:
        sort_col = 'Total_Price'
        st.subheader(f"Level 1: Cheapest {category} for {target_filter}")
    elif "Level 2" in view_level:
        final_filtered['Price_per_Elemental_Gram'] = (final_filtered['Total_Price'] / (final_filtered['Elemental_Amount_mg'] / 1000))
        sort_col = 'Price_per_Elemental_Gram'
        st.subheader(f"Level 2: Best Elemental ROI for {target_filter}")
    else:
        sort_col = 'PPAA_1g_Absorbed'
        st.subheader(f"🦈 Level 3: {target_filter} Value Leader (Cost per Absorbed Gram)")

    # Sort the data
    final_df = final_filtered.sort_values(by=sort_col, ascending=True)

    # --- DATA DISPLAY ---
    # Columns to show
    display_cols = ['Brand', 'Form', 'Target_Area', 'Total_Price', 'Notes']
    if "Level 3" in view_level:
        display_cols.insert(4, 'PPAA_1g_Absorbed')
    
    # Format currency
    st.dataframe(final_df[display_cols].style.format({
        'Total_Price': '${:.2f}',
        'PPAA_1g_Absorbed': '${:.3f}/g',
        'Price_per_Elemental_Gram': '${:.3f}/g'
    }), use_container_width=True)

    # --- SHARK STRATEGIC ANALYSIS ---
    if len(final_df) > 0:
        st.divider()
        best_product = final_df.iloc[0]
        st.success(f"🏆 **CATEGORY LEADER for {target_filter}:** {best_product['Brand']} ({best_product['Form']})")
        st.info(f"**Shark Insight:** When targeting **{best_product['Target_Area']}**, this product provides the most efficient absorption for your investment.")
    else:
        st.warning("No products found for this specific filter combination.")

else:
    st.info("Awaiting connection to Google Sheets data...")
