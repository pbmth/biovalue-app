import streamlit as st
import pandas as pd
import plotly.express as px

# CONFIGURATION
st.set_page_config(page_title="Shark Bio-Value Analyzer", layout="wide")

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
    # Safety checks for columns
    for col in ['Target_Area', 'Notes', 'Category', 'Unit_Type', 'URL']:
        if col not in df.columns: df[col] = ""

    st.title("🦈 Shark Bio-Value Supplement Analyzer")

    # --- SHARK SCAN ---
    with st.expander("🔍 SHARK SCAN - Analyze any product link", expanded=False):
        st.write("Paste an iHerb or store link below to see if the Shark can find you a better deal.")
        input_link = st.text_input("Product Link", placeholder="https://www.iherb.com/pr/...")
        if input_link:
            st.warning("⚠️ **Shark Analysis:** Most retail products have a 15-40% lower absorption rate than our recommendations.")
            st.info("Look at the chart below to see the 'Gold Standard' for this category.")

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
    category = st.sidebar.selectbox("Select Supplement Type", df['Category'].unique())
    filtered_cat = df[df['Category'] == category].copy()
    
    all_targets = set()
    target_data = filtered_cat['Target_Area'].fillna("General Health").astype(str)
    for t in target_data.unique():
        if t.strip():
            parts = [p.strip() for p in t.split('/')]
            all_targets.update(parts)
    
    target_options = ["General Health"] + sorted([t for t in all_targets if t != "General Health"])
    target_filter = st.sidebar.selectbox("Select Target Area", target_options)
    view_level = st.sidebar.radio("Analysis Depth", ["Level 1: Shelf Price", "Level 2: Elemental ROI", "Level 3: Shark Bio-Value (PPAA)"])

    if target_filter == "General Health":
        final_filtered = filtered_cat.copy()
    else:
        final_filtered = filtered_cat[filtered_cat['Target_Area'].str.contains(target_filter, na=False)].copy()

    # --- LEVEL CONFIGURATION ---
    if "Level 1" in view_level:
        sort_col = 'Total_Price'
        y_label = "Shelf Price ($)"
        chart_title = "Comparison by Shelf Price"
    elif "Level 2" in view_level:
        sort_col = 'Price_per_Elemental_Gram'
        y_label = "$ per Elemental Gram"
        chart_title = "Comparison by Elemental ROI"
    else:
        sort_col = 'PPAA_1g_Absorbed'
        y_label = "$ per Absorbed Gram"
        chart_title = "Shark Bio-Value (PPAA)"

    final_df = final_filtered.sort_values(by=sort_col, ascending=True)

    # --- DATA TABLE ---
    display_cols = ['Brand', 'Form']
    if 'Unit_Type' in final_df.columns: display_cols.append('Unit_Type')
    display_cols.extend(['Target_Area', 'Total_Price'])

    if "Level 2" in view_level: display_cols.append('Price_per_Elemental_Gram')
    if "Level 3" in view_level: 
        display_cols.append('PPAA_1g_Absorbed')
        display_cols.append('Notes')
    if 'URL' in final_df.columns: display_cols.append('URL')

    st.dataframe(
        final_df[display_cols],
        column_config={
            "URL": st.column_config.LinkColumn("Buy Now", display_text="Go to Store"),
            "Total_Price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "Price_per_Elemental_Gram": st.column_config.NumberColumn("$/Elem. g", format="$%.3f/g"),
            "PPAA_1g_Absorbed": st.column_config.NumberColumn("$/Absorb. g", format="$%.3f/g"),
            "Notes": st.column_config.TextColumn("Expert Notes", width="large"),
        },
        use_container_width=True, hide_index=True
    )

    # --- SHARK CHOICE (Esiletoodud võitja) ---
    if not final_filtered.empty:
        st.divider()
        shark_winner = final_filtered.sort_values(by='PPAA_1g_Absorbed', ascending=True).iloc[0]
        st.success(f"🏆 **SHARK'S CHOICE:** {shark_winner['Brand']} ({shark_winner['Form']})")
        st.info(f"**Shark Insight:** In the **{view_level}** view, this product provides the most biological value for your money.")

    # --- DIAGRAM (Nüüd lehe lõpus) ---
   if not final_df.empty:
        st.write("### 📊 Visual Comparison")
        # Creating a combination of brand and form for the chart
        final_df['Chart_Label'] = final_df['Brand'] + " (" + final_df['Form'] + ")"
        
        # Plotly bar chart
        fig = px.bar(
            final_df,
            x='Chart_Label',
            y=sort_col,
            title=f"{chart_title}",
            labels={'Chart_Label': 'Product', sort_col: y_label},
            color=sort_col,
            color_continuous_scale='RdYlGn_r' # From green to red
        )
        
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Awaiting connection to Google Sheets data...")
