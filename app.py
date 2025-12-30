import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bio-Value Engine", layout="wide")

# --- ANDMETE LAADIMINE ---
SHEET_URL = "SINU_GOOGLE_SHEETS_CSV_LINK_SIIA"

@st.cache_data(ttl=60) 
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except:
        # Näidisandmed, kui Sheets pole veel ühendatud
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
            'Absorb_Coeff': [0.04, 0.45, 0.99, 0.70], # Kreatiin monohüdraat imendub tegelikult väga hästi (~99%)
            'Notes': ['Basic', 'High Quality', 'Pure Powder', 'Concentrated'],
            'URL': ['#', '#', '#', '#']
        }
        return pd.DataFrame(data)

df = load_data()

# --- ARVUTUSED ---
df['Total_Cost'] = df['Price_Bottle'] + df['Shipping']
df['Elemental_Mg_Total'] = df['Units_Total'] * df['Mg_per_Unit'] * df['Yield_Coeff']
df['Absorbed_Mg_Total'] = df['Elemental_Mg_Total'] * df['Absorb_Coeff']
df['Bio_Value_PPAA'] = df['Total_Cost'] / df['Absorbed_Mg_Total']

# --- UI ---
st.title("🧬 Bio-Value Strategy Engine")

# Kategooria valik
category = st.sidebar.selectbox("Vali toidulisand:", df['Category'].unique())
view_mode = st.sidebar.radio("Vaade:", ["Tavaline hind", "Expert Bio-Value (PPAA)"])

# Filtreerime andmed vastavalt valikule
df_filtered = df[df['Category'] == category]

if "Expert" in view_mode:
    df_sorted = df_filtered.sort_values('Bio_Value_PPAA')
    st.success(f"Expert View: Parimad {category} tooted bioloogilise väärtuse järgi.")
else:
    df_sorted = df_filtered.sort_values('Total_Cost')

# --- TABEL ---
st.data_editor(
    df_sorted[['Brand', 'Form', 'Total_Cost', 'Bio_Value_PPAA', 'Notes', 'URL']],
    column_config={
        "URL": st.column_config.LinkColumn("Buy Now", display_text="View Store"),
        "Bio_Value_PPAA": st.column_config.NumberColumn("PPAA (Real Cost)", format="%.4f €"),
        "Total_Cost": st.column_config.NumberColumn("Full Price", format="%.2f €")
    },
    hide_index=True,
    use_container_width=True
)
