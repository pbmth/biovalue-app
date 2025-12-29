import streamlit as st
import pandas as pd

# 1. LEHE SEADISTUS
st.set_page_config(page_title="Bio-Value Live Engine", layout="wide", initial_sidebar_state="expanded")

# --- GOOGLE SHEETS ANDMETE LINK ---
# ASENDA SEE LINK OMA GOOGLE SHEETSI PUBLISHED CSV LINGIGA (File -> Share -> Publish to Web -> CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS_D60I8P9Qh7zH_7L6_Vn4YgN4W4v9G7_G6v4v/pub?output=csv"

@st.cache_data(ttl=600) # Uuendab andmeid iga 10 minuti tagant
def load_data():
    try:
        # Loeme andmed. Kui link on vigane, kasutame näidisandmeid, et äpp ei krahhiks.
        df = pd.read_csv(SHEET_URL)
        return df
    except:
        # NÄIDISANDMED (kui Google Sheets linki pole veel lisatud)
        data = {
            'Brand': ['BudgetHealth', 'Thorne', 'NOW Foods', 'Pure Encaps', 'BulkSupps'],
            'Form': ['Oxide', 'Bisglycinate', 'Citrate', 'Glycinate', 'Oxide'],
            'Price_Bottle': [12.00, 48.00, 18.00, 42.00, 9.00],
            'Shipping': [4.00, 0.00, 5.00, 0.00, 6.00],
            'Capsules': [120, 60, 90, 60, 250],
            'Mg_per_Cap': [500, 200, 200, 120, 500],
            'Yield_Coeff': [0.60, 0.14, 0.16, 0.14, 0.60],
            'Absorb_Coeff': [0.04, 0.50, 0.25, 0.50, 0.04]
        }
        return pd.DataFrame(data)

# 2. ANDMETE TÖÖTLUS
df = load_data()

# Arvutame väärtused
df['Total_Cost'] = df['Price_Bottle'] + df['Shipping']
df['Elemental_Mg_Total'] = df['Capsules'] * df['Mg_per_Cap'] * df['Yield_Coeff']
df['Absorbed_Mg_Total'] = df['Elemental_Mg_Total'] * df['Absorb_Coeff']

# Kolm strateegilist hinda
df['Price_per_Bottle'] = df['Total_Cost']
df['Price_per_Elemental_mg'] = df['Total_Cost'] / df['Elemental_Mg_Total']
df['Bio_Value_PPAA'] = df['Total_Cost'] / df['Absorbed_Mg_Total']

# 3. KASUTAJALIIDES (UI)
st.title("🧬 Bio-Value Strategy Engine")
st.markdown("---")

# Külgriba (Sidebar)
st.sidebar.header("Sorting Intelligence")
logic = st.sidebar.radio(
    "Choose how to view value:",
    ("1. Price per Bottle (Traditional)", 
     "2. Price per Elemental Mg (Skeptic)", 
     "3. Bio-Value / PPAA (Expert View)")
)

# 4. VAATED JA SELGITUSED
if "1." in logic:
    df_sorted = df.sort_values('Price_per_Bottle')
    st.subheader("🛒 Traditional View: Sorting by Bottle Price")
    st.info("Most consumers stop here. They choose the lowest sticker price, unaware of the hidden costs.")
elif "2." in logic:
    df_sorted = df.sort_values('Price_per_Elemental_mg')
    st.subheader("⚖️ Skeptic View: Sorting by Elemental Content")
    st.info("Better. This shows the cost of the raw mineral, but ignores how much your body can actually use.")
else:
    df_sorted = df.sort_values('Bio_Value_PPAA')
    st.subheader("🔬 Expert View: Bio-Value (PPAA)")
    st.success("This is the truth. We adjust the price for biological absorption. The 'cheapest' bottle is often the most expensive for your cells.")

# 5. TABELI KUVAMINE
display_cols = ['Brand', 'Form', 'Price_per_Bottle', 'Price_per_Elemental_mg', 'Bio_Value_PPAA']
st.dataframe(df_sorted[display_cols].style.highlight_min(axis=0, color='#d4edda').format({
    'Price_per_Bottle': '{:.2f} €',
    'Price_per_Elemental_mg': '{:.4f} €',
    'Bio_Value_PPAA': '{:.4f} €'
}), use_container_width=True)

st.markdown("---")
st.write("📊 **The Mission:** Turning consumers smart by exposing the real biological cost of supplementation.")
