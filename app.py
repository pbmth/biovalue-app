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
        data = {
            'Category': ['Magnesium', 'Magnesium', 'Magnesium'],
            'Brand': ['Budget Corp', 'Mid-Range', 'Bio-Value Pick'],
            'Form': ['Oxide', 'Citrate', 'Bisglycinate'],
            'Unit_Type': ['Capsule', 'Capsule', 'Capsule'],
            'Price_Bottle': [10.00, 20.00, 35.00],
            'Shipping': [5.00, 0.00, 0.00],
            'Units_Total': [100, 100, 100],
            'Mg_per_Unit': [500, 500, 500],
            'Yield_Coeff': [0.60, 0.16, 0.14],
            'Absorb_Coeff': [0.04, 0.25, 0.45],
            'Notes': ['Cheap but raw', 'Standard', 'Premium Absorption'],
            'URL': ['#', '#', '#']
        }
        return pd.DataFrame(data)

df = load_data()

# --- CALCULATIONS ---
df['Total_Cost'] = df['Price_Bottle'] + df['Shipping']
# Step 1: Total raw compound in bottle
df['Total_Mg_Compound'] = df['Units_Total'] * df['Mg_per_Unit']
# Step 2: Elemental Magnesium (The "Skeptic" level)
df['Elemental_Mg_Total'] = df['Total_Mg_Compound'] * df['Yield_Coeff']
df['Price_Per_Elemental_Mg'] = df['Total_Cost'] / df['Elemental_Mg_Total']
# Step 3: Absorbed Magnesium (The "Expert" level)
df['Absorbed_Mg_Total'] = df['Elemental_Mg_Total'] * df['Absorb_Coeff']
df['PPAA'] = df['Total_Cost'] / df['Absorbed_Mg_Total']

# --- UI SETTINGS ---
st.title("🧬 Bio-Value Strategy Engine")

# Sidebar
st.sidebar.header("Navigation")
if 'Category' in df.columns:
    category = st.sidebar.selectbox("Select Supplement:", df['Category'].unique())
    df_filtered = df[df['Category'] == category]
else:
    df_filtered = df

# THE THREE-LEVEL LOGIC
view_mode = st.sidebar.radio(
    "Optimization Level:",
    [
        "1. Market Price (Basic)", 
        "2. Elemental ROI (Skeptic)", 
        "3. Expert Bio-Value (PPAA)"
    ]
)

# Sorting and Feedback based on level
if "1." in view_mode:
    df_sorted = df_filtered.sort_values('Total_Cost')
    st.info("Level 1: Products sorted by shelf price. This is how most people shop.")
elif "2." in view_mode:
    df_sorted = df_filtered.sort_values('Price_Per_Elemental_Mg')
    st.warning("Level 2: Sorted by price per elemental mg. This filters out fillers but ignores biology.")
else:
    df_sorted = df_filtered.sort_values('PPAA')
    st.success("Level 3: Optimized for actual cellular absorption. This is the ultimate Bio-Value.")

# --- DISPLAY ---
st.data_editor(
    df_sorted[['Brand', 'Form', 'Total_Cost', 'Price_Per_Elemental_Mg', 'PPAA', 'Notes', 'URL']],
    column_config={
        "Total_Cost": st.column_config.NumberColumn("Shelf Price (€)", format="%.2f"),
        "Price_Per_Elemental_Mg": st.column_config.NumberColumn("Cost/Elemental mg", format="%.4f €"),
        "PPAA": st.column_config.NumberColumn("Real Cost (PPAA)", format="%.4f €"),
        "URL": st.column_config.LinkColumn("Purchase", display_text="View Store")
    },
    hide_index=True,
    use_container_width=True
)
