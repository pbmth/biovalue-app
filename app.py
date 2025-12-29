import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bio-Value Live Engine", layout="wide")

# --- ANDMETE LAADIMINE ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS_D60I8P9Qh7zH_7L6_Vn4YgN4W4v9G7_G6v4v/pub?output=csv"

@st.cache_data(ttl=60) 
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except:
        # Näidisandmed juhuks kui Sheets pole veel valmis
        data = {
            'Brand': ['BudgetHealth', 'Thorne', 'Bulk Powder'],
            'Form': ['Oxide', 'Bisglycinate', 'Citrate'],
            'Unit_Type': ['Capsule', 'Capsule', 'Gram'],
            'Price_Bottle': [12.00, 48.00, 25.00],
            'Shipping': [4.00, 0.00, 5.00],
            'Units_Total': [120, 60, 500], # 500g pulbrit
            'Mg_per_Unit': [500, 200, 300], # 300mg 1g pulbri kohta
            'Yield_Coeff': [0.60, 0.14, 0.16],
            'Absorb_Coeff': [0.04, 0.50, 0.25],
            'URL': ['https://google.com', 'https://google.com', 'https://google.com']
        }
        return pd.DataFrame(data)

df = load_data()

# --- ARVUTUSED (Universaalne loogika) ---
df['Total_Cost'] = df['Price_Bottle'] + df['Shipping']
# Arvutame kogu elementaarse magneesiumi: ühikud * mg ühiku kohta * saagis
df['Elemental_Mg_Total'] = df['Units_Total'] * df['Mg_per_Unit'] * df['Yield_Coeff']
# Arvutame imenduva osa
df['Absorbed_Mg_Total'] = df['Elemental_Mg_Total'] * df['Absorb_Coeff']
# Bio-Value PPAA (Price Per Actually Absorbed mg)
df['Bio_Value_PPAA'] = df['Total_Cost'] / df['Absorbed_Mg_Total']

# --- UI ---
st.title("🧬 Bio-Value Strategy Engine")
st.markdown("Comparing Supplements by Biological Reality")

logic = st.sidebar.radio("View Mode:", ["Traditional Price", "Expert Bio-Value (PPAA)"])

if "Expert" in logic:
    df_sorted = df.sort_values('Bio_Value_PPAA')
    st.success("Expert View: Rankings adjusted for Bioavailability.")
else:
    df_sorted = df.sort_values('Total_Cost')

# --- TABEL ---
st.data_editor(
    df_sorted[['Brand', 'Form', 'Unit_Type', 'Total_Cost', 'Bio_Value_PPAA', 'URL']],
    column_config={
        "Unit_Type": "Type",
        "URL": st.column_config.LinkColumn(
            "Buy Now",
            display_text="View Store"
        ),
        "Bio_Value_PPAA": st.column_config.NumberColumn("PPAA (Real Cost)", format="%.4f €"),
        "Total_Cost": st.column_config.NumberColumn("Full Price", format="%.2f €")
    },
    hide_index=True,
    use_container_width=True
)

st.write("---")
st.caption("PPAA = Price Per Actually Absorbed milligram of elemental magnesium.")
