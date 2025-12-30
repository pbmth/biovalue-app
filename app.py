import streamlit as st
import pandas as pd

# CONFIGURATION
st.set_page_config(page_title="Bio-Value Supplement Analyzer", layout="wide")

# 1. PASTE YOUR GOOGLE SHEETS CSV LINK HERE
SHEET_URL = "YOUR_CSV_LINK_HERE"

@st.cache_data
def load_data(url):
    try:
        # Load data and strip whitespace from column headers
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data(SHEET_URL)

if df is not None:
    st.title("🦈 Shark Bio-Value Supplement Analyzer")
    st.write("Exposing the true biological value of supplements by cutting through marketing noise.")

    # --- CALCULATION ENGINE ---
    # Calculating total price, elemental amount, and absorbed amount
    df['Total_Price'] = df['Price_Bottle'] + df['Shipping']
    df['Elemental_Amount_mg'] = df['Units_Total'] * df['Amount_per_Unit'] * df['Yield_Coeff']
    df['Absorbed_Amount_mg'] = df['Elemental_Amount_mg'] * df['Absorb_Coeff']
    
    # PPAA (Price Per Absorbed Amount) - Cost of 1 gram of absorbed substance
    df['PPAA_1g_Absorbed'] = (df['Total_Price'] / df['Absorbed_Amount_mg']) * 1000

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Analysis Settings")
    category = st.sidebar.selectbox("Select Category", df['Category'].unique())
    view_level = st.sidebar.radio("Analysis Depth (Complexity)", 
                                 ["Level 1: Shelf Price", 
                                  "Level 2: Elemental ROI", 
                                  "Level 3: Shark Bio-Value (PPAA)"])

    filtered_df = df[df['Category'] == category].copy()

    # --- SORTING LOGIC ---
    if "Level 1" in view_level:
        sort_col = 'Total_Price'
        ascending = True
        st.subheader(f"Level 1: Cheapest Products on Shelf ({category})")
    elif "Level 2" in view_level:
        filtered_df['Price_per_Elemental_Gram'] = (filtered_df['Total_Price'] / (filtered_df['Elemental_Amount_mg'] / 1000))
        sort_col = 'Price_per_Elemental_Gram'
        ascending = True
        st.subheader(f"Level 2: Best Price per Elemental Gram ({category})")
    else:
        sort_col = 'PPAA_1g_Absorbed'
        ascending = True
        st.subheader(f"🦈 Level 3: Shark Bio-Value - Cost per Absorbed Gram ({category})")

    final_df = filtered_df.sort_values(by=sort_col, ascending=ascending)

    # --- DATA DISPLAY ---
    # Selecting columns to display based on the selected level
    display_cols = ['Brand', 'Form', 'Total_Price', 'Notes']
    if "Level 3" in view_level:
        display_cols.insert(3, 'PPAA_1g_Absorbed')
    
    st.dataframe(final_df[display_cols].style.format({
        'Total_Price': '${:.2f}',
        'PPAA_1g_Absorbed': '${:.3f}/g'
    }), use_container_width=True)

    # --- SHARK STRATEGIC ANALYSIS ---
    st.divider()
    best_product = final_df.iloc[0]
    worst_product = final_df.iloc[-1]

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ **TOP PICK:** {best_product['Brand']} ({best_product['Form']})")
        st.write(f"This product offers the lowest cost per milligram of biologically available active ingredient.")
    with col2:
        st.error(f"❌ **POOR DEAL:** {worst_product['Brand']} ({worst_product['Form']})")
        st.write(f"This product's price is misleading. The absorbed gram is {worst_product[sort_col] / best_product[sort_col]:.1f}x more expensive than the top pick.")

else:
    st.info("Awaiting connection to Google Sheets data...")
