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

# Safety check for Target_Area
if df is not None and 'Target_Area' not in df.columns:
    df['Target_Area'] = 'General'

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
    
    target_options = ["All Targets"] + sorted(list(filtered_cat['Target_Area'].unique()))
    target_filter = st.sidebar.selectbox("Select Target Area", target_options)

    view_level = st.sidebar.radio("Analysis Depth", 
                                 ["Level 1: Shelf Price", 
                                  "Level 2: Elemental ROI", 
                                  "Level 3: Shark Bio-Value (PPAA)"])

    if target_filter != "All Targets":
        final_filtered = filtered_cat[filtered_cat['Target_Area'] == target_filter].copy()
    else:
        final_filtered = filtered_cat.copy()

    # --- SORTING LOGIC & DESCRIPTIONS ---
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

    # --- DATA DISPLAY LOGIC ---
    display_cols = ['Brand', 'Form', 'Target_Area', 'Total_Price']
    if "Level 2" in view_level:
        display_cols.append('Price_per_Elemental_Gram')
    if "Level 3" in view_level:
        display_cols.append('PPAA_1g_Absorbed')
        display_cols.append('Notes')
    display_cols.append('URL')

    st.dataframe(
        final_df[display_cols],
        column_config={
            "URL": st.column_config.LinkColumn("Buy Now", display_text="Go to Store"),
            "Total_Price": st.column_config.NumberColumn("Total Price", format="$%.2f"),
            "Price_per_Elemental_Gram": st.column_config.NumberColumn("$/Elemental Gram", format="$%.3f/g"),
            "PPAA_1g_Absorbed": st.column_config.NumberColumn("$/Absorbed Gram", format="$%.3f/g"),
            "Notes": st.column_config.TextColumn("Expert Notes", width="large"),
        },
        use_container_width=True, hide_index=True
    )

    # --- SMART SHARK ANALYSIS ---
    if len(final_filtered) > 0:
        st.divider()
        shark_winner = final_filtered.sort_values(by='PPAA_1g_Absorbed', ascending=True).iloc[0]
        st.success(f"🏆 **SHARK'S CHOICE:** {shark_winner['Brand']} ({shark_winner['Form']})")
        st.info(f"**Shark Insight:** Regardless of the shelf price, **{shark_winner['Brand']}** provides the best mathematical value for **{shark_winner['Target_Area']}** because of its superior absorption and yield.")

else:
    st.info("Awaiting connection to Google Sheets data...")
