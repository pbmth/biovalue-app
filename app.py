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
        # Kui faili veel pole või tulp puudub, tekitame näidis-URL-id
        data = {
            'Brand': ['BudgetHealth', 'Thorne', 'NOW Foods'],
            'Form': ['Oxide', 'Bisglycinate', 'Citrate'],
            'Price_Bottle': [12.00, 48.00, 18.00],
            'Shipping': [4.00, 0.00, 5.00],
            'Capsules': [120, 60, 90],
            'Mg_per_Cap': [500, 200, 200],
            'Yield_Coeff': [0.60, 0.14, 0.16],
            'Absorb_Coeff': [0.04, 0.50, 0.25],
            'URL': ['https://google.com', 'https://google.com', 'https://google.com']
        }
        return pd.DataFrame(data)

df = load_data()

# --- ARVUTUSED ---
df['Total_Cost'] = df['Price_Bottle'] + df['Shipping']
df['Elemental_Mg_Total'] = df['Capsules'] * df['Mg_per_Cap'] * df['Yield_Coeff']
df['Absorbed_Mg_Total'] = df['Elemental_Mg_Total'] * df['Absorb_Coeff']
df['Bio_Value_PPAA'] = df['Total_Cost'] / df['Absorbed_Mg_Total']

# --- UI ---
st.title("🧬 Bio-Value Strategy Engine")

logic = st.sidebar.radio("View Mode:", ["Bottle Price", "Expert Bio-Value (PPAA)"])

if "Expert" in logic:
    df_sorted = df.sort_values('Bio_Value_PPAA')
    st.success("Expert View: Products ranked by true biological value.")
else:
    df_sorted = df.sort_values('Total_Cost')

# --- LINKIDE EKRAANI KUVAMINE ---
# Kasutame Streamliti uut "Link Column" funktsiooni
st.data_editor(
    df_sorted[['Brand', 'Form', 'Total_Cost', 'Bio_Value_PPAA', 'URL']],
    column_config={
        "URL": st.column_config.LinkColumn(
            "Buy Now",
            help="Direct link to the store",
            validate=r"^https://",
            display_text="View Store"
        ),
        "Bio_Value_PPAA": st.column_config.NumberColumn("PPAA Cost", format="%.4f €"),
        "Total_Cost": st.column_config.NumberColumn("Price", format="%.2f €")
    },
    hide_index=True,
    use_container_width=True
)

st.info("💡 **Affiliate Tip:** These 'View Store' links can be your affiliate links, creating an immediate revenue stream.")
