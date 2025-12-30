import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bio-Value Engine", layout="wide")

# --- DATA LOADING ---
# Asenda see oma päris Google Sheetsi CSV lingiga!
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS_D60I8P9Qh7zH_7L6_Vn4YgN4W4v9G7_G6v4v/pub?output=csv"

@st.cache_data(ttl=60) 
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except:
        # Placeholder data if Sheets is not yet connected
        data = {
            'Category': ['Magnesium', 'Magnesium', 'Creatine', 'Creatine'],
            'Brand': ['BudgetHealth', 'Thorne', 'BulkPowders', 'Con-Cret'],
            'Form': ['Oxide', 'Bisglycinate', 'Monohydrate', 'HCL'],
            'Unit_Type': ['Capsule', 'Capsule', 'Gram', 'Capsule'],
            'Price_Bottle': [12.00, 48.00, 25.00, 35.00],
            'Shipping': [4.00, 0.00, 5.00, 0.00],
            'Units_Total': [120, 60, 500, 64],
            'Mg_per_Unit': [500, 200, 1000, 750],
            'Yield_Coeff': [0.60, 1.0, 1.0, 1.0],
            'Absorb_Coeff': [0.04, 0.45, 0.99, 0.70],
            'Notes': ['Basic formula', 'High Bioavailability', 'Purest form', 'Concentrated HCL'],
            'URL': ['#', '#', '#', '#']
        }
        return pd.DataFrame(data)

df = load_data()

# --- CALCULATIONS ---
df['Total_Cost'] = df['Price_Bottle'] + df['Shipping']
# General logic for absorbed amount
df['Absorbed_Amount_Total'] = (df['Units_Total'] * df['Mg_per_Unit'] * df['Yield_Coeff'] * df['Absorb_Coeff'])
# Price Per Actually Absorbed mg (PPAA)
df['PPAA'] = df['Total_Cost'] / df['Absorbed_Amount_Total']

# --- UI SETTINGS ---
st.title("🧬 Bio-Value Strategy Engine")
st.markdown("### Maximizing Nutritional ROI")

# Sidebar for controls
st.sidebar.header("Navigation")
if 'Category' in df.columns:
    available_categories = df['Category'].unique()
    category = st.sidebar.selectbox("Select Supplement:", available_categories)
    df_filtered = df[df['Category'] == category]
else:
    df_filtered = df

view_mode = st.sidebar.radio("Optimization Mode:", ["Traditional Price", "Expert Bio-Value (PPAA)"])

# Sorting logic
if "Expert" in view_mode:
    df_sorted = df_filtered.sort_values('PPAA')
    st.success(f"Ranking {category} by Biological Value (PPAA)")
else:
    df_sorted = df_filtered.sort_values('Total_Cost')

# --- DISPLAY TABLE ---
st.data_editor(
    df_sorted[['Brand', 'Form', 'Total_Cost', 'PPAA', 'Notes', 'URL']],
    column_config={
        "Brand": "Brand Name",
        "Form": "Compound",
        "Total_Cost": st.column_config.NumberColumn("List Price (€)", format="%.2f"),
        "PPAA": st.column_config.NumberColumn("PPAA (Real Cost)", format="%.4f €"),
        "Notes": "Key Features",
        "URL": st.column_config.LinkColumn("Purchase", display_text="View Store")
    },
    hide_index=True,
    use_container_width=True
)

st.write("---")
st.caption("PPAA (Price Per Actually Absorbed mg) reveals the true cost of supplements by accounting for compound yield and bioavailability.")
