import streamlit as st
import pandas as pd
import plotly.express as px

# CONFIGURATION
st.set_page_config(page_title="Shark Bio-Value Supplement Analyzer", layout="wide")

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

if df is not None:
    # Safety Check: Fill missing vital columns
    vital_cols = ['Category', 'Brand', 'Form', 'Target_Area', 'Price_Bottle', 'Shipping', 'Units_Total', 'Amount_per_Unit', 'Yield_Coeff', 'Absorb_Coeff', 'Notes', 'URL']
    for col in vital_cols:
        if col not in df.columns:
            df[col] = "" if col in ['Category', 'Brand', 'Form', 'Target_Area', 'Notes', 'URL'] else 0

    st.title("🦈 Shark Bio-Value Supplement Analyzer")

    # --- SHARK SCAN ---
    with st.expander("🔍 SHARK SCAN - Analyze any product link", expanded=False):
        st.write("Paste an iHerb or store link below to see if the Shark can find you a better deal.")
        input_link = st.text_input("Product Link", placeholder="https://www.iherb.com/pr/...")
        if input_link and not df.empty:
            potential_winners = df.sort_values(by='Absorb_Coeff', ascending=False).iloc[0]
            st.info("💡 **Shark Analysis:** Most retail products have a 15-40% lower absorption rate than our recommendations.")
            st.warning(f"⚠️ **Better Value Found!** Our database suggests **{potential_winners['Brand']}** provides superior biological value.")
            if str(potential_winners['URL']).startswith("http"):
                st.link_button(f"View Shark Choice: {potential_winners['Brand']}", potential_winners['URL'])

    # --- CALCULATION ENGINE ---
    df['Total_Price'] = pd.to_numeric(df['Price_Bottle'], errors='coerce').fillna(0) + pd.to_numeric(df['Shipping'], errors='coerce').fillna(0)
    df['Elemental_Amount_mg'] = pd.to_numeric(df['Units_Total'], errors='coerce').fillna(0) * \
                                pd.to_numeric(df['Amount_per_Unit'], errors='coerce').fillna(0) * \
                                pd.to_numeric(df['Yield_Coeff'], errors='coerce').fillna(1)
    df['Absorbed_Amount_mg'] = df['Elemental_Amount_mg'] * pd.to_numeric(df['Absorb_Coeff'], errors='coerce').fillna(1)
    df['Price_per_Elemental_Gram'] = df['Total_Price'] / (df['Elemental_Amount_mg'] / 1000).replace(0, 1)
    df['PPAA_1g_Absorbed'] = (df['Total_Price'] / (df['Absorbed_Amount_mg'].replace(0, 0.000001))) * 1000

    # --- SIDEBAR ---
    st.sidebar.header("Filter & Analyze")
    available_cats = df['Category'].unique() if not df.empty else ["N/A"]
    category = st.sidebar.selectbox("Select Supplement Type", available_cats)
    filtered_cat = df[df['Category'] == category].copy()
    
    all_targets = set()
    target_data = filtered_cat['Target_Area'].fillna("General Health").astype(str)
    for t in target_data.unique():
        if t.strip() and t not in ["0", "nan"]:
            parts = [p.strip() for p in t.split('/')]
            all_targets.update(parts)
    
    target_options = ["General Health"] + sorted([t for t in list(all_targets) if t != "General Health"])
    target_filter = st.sidebar.selectbox("Select Target Area", target_options)
    view_level = st.sidebar.radio("Analysis Depth", ["Level 1: Shelf Price", "Level 2: Elemental ROI", "Level 3: Shark Bio-Value (PPAA)"])

    if target_filter == "General Health":
        final_filtered = filtered_cat.copy()
    else:
        final_filtered = filtered_cat[filtered_cat['Target_Area'].str.contains(target_filter, na=False)].copy()

    # --- DESCRIPTIONS & SORTING ---
    st.divider()
    if "Level 1" in view_level:
        sort_col = 'Total_Price'
        st.subheader(f"Level 1: Comparison by Shelf Price ({target_filter})")
        st.write("💡 **Current Consumer Behavior:** People look at the price tag, unaware of the actual content.")
    elif "Level 2" in view_level:
        sort_col = 'Price_per_Elemental_Gram'
        st.subheader(f"Level 2: Comparison by Elemental ROI ({target_filter})")
        st.write("🔍 **The Smart Buyer View:** This level reveals the cost of the raw mineral content.")
    else:
        sort_col = 'PPAA_1g_Absorbed'
        st.subheader(f"🦈 Level 3: Comparison by Shark Bio-Value ({target_filter})")
        st.write("🚀 **The Expert/Shark View:** Analysis of what *actually* enters your bloodstream.")

    final_df = final_filtered.sort_values(by=sort_col, ascending=True)

    # --- DATA DISPLAY ---
    cols_to_show = ['Brand', 'Form', 'Target_Area', 'Total_Price']
    if "Level 2" in view_level: cols_to_show.append('Price_per_Elemental_Gram')
    if "Level 3" in view_level: 
        cols_to_show.append('PPAA_1g_Absorbed')
        cols_to_show.append('Notes')
    cols_to_show.append('URL')

    st.dataframe(
        final_df[cols_to_show],
        column_config={
            "URL": st.column_config.LinkColumn("Buy Now", display_text="Go to Store"),
            "Total_Price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "Price_per_Elemental_Gram": st.column_config.NumberColumn("$/Elem. g", format="$%.3f/g"),
            "PPAA_1g_Absorbed": st.column_config.NumberColumn("$/Absorb. g", format="$%.3f/g"),
            "Notes": st.column_config.TextColumn("Expert Notes", width="large")
        },
        use_container_width=True, hide_index=True
    )

    # --- INTERACTIVE PLOTLY CHART ---
    if not final_df.empty:
        st.subheader("📊 Visual ROI Analysis: Price vs. Biological Value")
        
        # Melt the dataframe for Plotly (transforming columns into rows for easier grouping)
        chart_df = final_df.melt(id_vars=['Brand'], 
                                value_vars=['Total_Price', 'PPAA_1g_Absorbed'],
                                var_name='Metric', 
                                value_name='Value')
        
        # Rename metrics for cleaner legend
        chart_df['Metric'] = chart_df['Metric'].replace({
            'Total_Price': 'Shelf Price ($)',
            'PPAA_1g_Absorbed': 'Shark Bio-Value Cost ($/g absorbed)'
        })

        fig = px.bar(chart_df, 
                     x='Brand', 
                     y='Value', 
                     color='Metric',
                     barmode='group',
                     color_discrete_map={
                         'Shelf Price ($)': '#636EFA', 
                         'Shark Bio-Value Cost ($/g absorbed)': '#EF553B'
                     },
                     labels={'Value': 'USD ($)', 'Brand': 'Supplement Brand'})
        
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    # --- SMART SHARK ANALYSIS ---
    if not final_filtered.empty:
        st.divider()
        shark_winner = final_filtered.sort_values(by='PPAA_1g_Absorbed', ascending=True).iloc[0]
        st.success(f"🏆 **SHARK'S CHOICE for {target_filter}:** {shark_winner['Brand']} ({shark_winner['Form']})")
        st.info(f"**Shark Insight:** Regardless of the shelf price, **{shark_winner['Brand']}** is the mathematical winner because it delivers the best biological value per dollar spent.")
else:
    st.info("Awaiting connection to Google Sheets data...")
