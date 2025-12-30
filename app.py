import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bio-Value Engine", layout="wide")

# --- DATA LOADING ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS_D60I8P9Qh7zH_7L6_Vn4YgN4W4v9G7_G6v4v/pub?output=csv"

@st.cache_data(ttl=60) 
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except:
        # Placeholder data logic
        data = {
            'Category': ['Magnesium', 'Creatine'],
            'Brand': ['Thorne', 'BulkPowders'],
            'Form': ['Bisglycinate', 'Monohydrate'],
            'Unit_Type': ['Capsule', 'Gram'],
            'Price_Bottle': [40.00, 25.00],
            'Shipping': [0.00, 5.00],
            'Units_Total': [60, 500],
            'Amount_per_Unit': [200, 1000],
            'Yield_Coeff': [1.0, 0.88],
            'Absorb_Coeff': [0.45, 0.99],
            'Notes': ['Premium', 'Best Seller'],
            'URL': ['#', '#']
        }
        return pd.DataFrame(data)

df = load_data()

# --- CALCULATIONS (Universal Logic) ---
df['Total_Cost'] = df['Price_Bottle'] + df['Shipping']

# Step 1: Total Raw Substance (Total units * Amount per unit)
df['Total_Raw_Amount'] = df['Units_Total'] * df['Amount_per_Unit']

# Step 2: Total Elemental Substance (Skeptic Filter)
df['Elemental_Amount_Total'] = df['Total_Raw_Amount'] * df['Yield_Coeff']
df['Cost_per_Elemental'] = df['Total_Cost'] / df['Elemental_Amount_Total']

# Step 3: Actually Absorbed Amount (Expert Filter)
df['Absorbed_Amount_Total'] = df['Elemental_Amount_Total'] * df['Absorb_Coeff']
df['PPAA'] = df['Total_Cost'] / df['Absorbed_Amount_Total']

# --- UI SETTINGS ---
st.title("🧬 Bio-Value Strategy Engine")

# Sidebar navigation
st.sidebar.header("Navigation")
if 'Category' in df.columns:
    cat_list = df['Category'].unique()
    category = st.sidebar.selectbox("Select Supplement Category:", cat_list)
    df_filtered = df[df['Category'] == category]
else:
    category = "Supplements"
    df_filtered = df

view_mode = st.sidebar.radio(
    "Optimization Level:",
    [
        "1. Market Price (Basic)", 
        "2. Elemental ROI (Skeptic)", 
        "3. Expert Bio-Value (PPAA)"
    ]
)

# Sorting logic
if "1." in view_mode:
    df_sorted = df_filtered.sort_values('Total_Cost')
    st.info(f"Level 1: {category} sorted by shelf price. Standard retail view.")
elif "2." in view_mode:
    df_sorted = df_filtered.sort_values('Cost_per_Elemental')
    st.warning(f"Level 2: {category} sorted by cost per elemental mg. Filtering fillers.")
else:
    df_sorted = df_filtered.sort_values('PPAA')
    st.success(f"Level 3: {category} sorted by actual absorption. Maximum Bio-Value.")

# --- DISPLAY TABLE ---
st.data_editor(
    df_sorted[['Brand', 'Form', 'Total_Cost', 'Cost_per_Elemental', 'PPAA', 'Notes', 'URL']],
    column_config={
        "Total_Cost": st.column_config.NumberColumn("Shelf Price (€)", format="%.2f"),
        "Cost_per_Elemental": st.column_config.NumberColumn("Cost/Elemental mg", format="%.4f €"),
        "PPAA": st.column_config.NumberColumn("Real Cost (PPAA)", format="%.4f €"),
        "URL": st.column_config.LinkColumn("Purchase", display_text="View Store")
    },
    hide_index=True,
    use_container_width=True
)

st.write("---")
st.caption("Bio-Value Engine | Scaling nutrition transparency through mathematics.")
