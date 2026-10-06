import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import shap
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import roc_auc_score


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "supplier_shipment_delay_dataset.csv"

# --- SETTINGS ---
st.set_page_config(page_title="Supplier Shipment Delay Predictor", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Global styles and typography */
    [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC;
    }
    
    /* Sidebar */
    
    
    
    
    
        /* Reset Button */
    
    
    
    /* Main Content Typography */
    .block-container {
        padding-top: 1rem !important; /* Reduce top padding */
    }
    h1 { font-size: 32px !important; font-weight: 700 !important; color: #0F172A !important; }
    h2 { font-size: 22px !important; font-weight: 600 !important; color: #0F172A !important; }
    h3, h4, h5, h6 { color: #0F172A !important; }
    
    /* KPI Cards */
    .metric-card {
        background-color: #FFFFFF;
        padding: 18px 20px;
        border-radius: 10px;
        border: 1px solid #D5DEE9;
        border-left: 3px solid #3B82F6;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: 0 1px 2px rgba(15,23,42,0.05);
        margin-bottom: 10px;
    }
    .metric-title {
        color: #64748B;
        font-size: 12px;
        margin-bottom: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: normal;
        
        
    }
    .metric-value {
        color: #0F172A;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .metric-value-text {
        color: #0F172A;
        font-size: 18px;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .metric-subtext {
        color: #64748B;
        font-size: 12px;
        margin-top: 4px;
    }
    
    /* Info Strip */
    .data-overview {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #D5DEE9;
        color: #64748B;
        font-size: 13px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 2px rgba(15,23,42,0.05);
    }
    .data-overview strong {
        color: #0F172A;
    }
    
    /* Tabs customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 32px;
        border-bottom: 1px solid #D5DEE9;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 3px solid transparent;
        color: #64748B;
        font-weight: 500;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #3B82F6 !important;
        border-bottom: 3px solid #3B82F6 !important;
        font-weight: 600;
    }
    
    /* Hide Deploy and Footer */
    header[data-testid="stHeader"] .stAppDeployButton {
        display: none !important;
    }
    footer[data-testid="stFooter"] {
        display: none !important;
    }
    
    /* AI Prediction colors */
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #3B82F6 !important;
    }
    .stSlider [data-baseweb="slider"] div[data-baseweb="slider-track"] > div:first-child {
        background-color: #3B82F6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA AND TRAIN MODEL ---
@st.cache_data
def load_data(mtime):
    df = pd.read_csv(DATA_PATH)
    df['origin_city'] = df['origin_city'].astype(str).str.strip()
    df['destination_city'] = df['destination_city'].astype(str).str.strip()
    df['transit_mode'] = df['transit_mode'].astype(str).str.strip()
    df['delay_days'] = pd.to_numeric(df['delay_days'], errors='coerce')
    df['departure_date'] = pd.to_datetime(df['departure_date'])
    return df

@st.cache_resource
def train_model(df, mtime):
    features = ['weather_severity_index', 'traffic_congestion_level', 'route_risk_score', 'supplier_reliability_score', 'distance_km', 'transit_mode']
    X = df[features].copy()
    y = (df['delayed'] == 'Yes').astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['transit_mode'])
        ],
        remainder='passthrough'
    )
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42, class_weight='balanced'))
    ])
    
    param_grid = {
        'classifier__n_estimators': [50, 100],
        'classifier__max_depth': [10, 20, None],
        'classifier__min_samples_split': [2, 5],
        'classifier__min_samples_leaf': [1, 2]
    }
    
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    search = RandomizedSearchCV(pipeline, param_distributions=param_grid, n_iter=5, cv=cv, scoring='f1', random_state=42, n_jobs=-1)
    search.fit(X_train, y_train)
    
    model = search.best_estimator_
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'training_rows': len(X_train),
        'testing_rows': len(X_test),
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_prob),
        'confusion_matrix': confusion_matrix(y_test, y_pred)
    }
    
    rf = model.named_steps['classifier']
    cat_encoder = model.named_steps['preprocessor'].named_transformers_['cat']
    encoded_cats = list(cat_encoder.get_feature_names_out(['transit_mode']))
    numeric_features = [f for f in features if f != 'transit_mode']
    feature_names = encoded_cats + numeric_features
    importances = rf.feature_importances_
    
    feature_imp = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
    feature_imp = feature_imp.sort_values(by='Importance', ascending=False)
    
    # Fix mapping for SHAP names
    feature_mapping = {}
    for feat in feature_names:
        if feat.startswith('transit_mode_'):
            feature_mapping[feat] = 'Transit Mode'
        elif feat == 'weather_severity_index':
            feature_mapping[feat] = 'Weather Severity'
        elif feat == 'traffic_congestion_level':
            feature_mapping[feat] = 'Traffic Congestion'
        elif feat == 'route_risk_score':
            feature_mapping[feat] = 'Route Risk'
        elif feat == 'supplier_reliability_score':
            feature_mapping[feat] = 'Supplier Reliability'
        elif feat == 'distance_km':
            feature_mapping[feat] = 'Distance'
        else:
            feature_mapping[feat] = feat
            
    feature_imp['Feature_Name'] = feature_imp['Feature'].map(feature_mapping)
    
    explainer = shap.TreeExplainer(rf)
    
    return model, metrics, feature_imp, explainer, feature_names

try:
    file_mtime = os.path.getmtime(DATA_PATH)
    df_raw = load_data(file_mtime)
    model, metrics, feature_imp, explainer, feature_names = train_model(df_raw, file_mtime)
except Exception as e:
    st.error(f"Error loading data or training model: {e}")
    st.stop()

df = df_raw.copy()

# --- TITLE ---
st.title("Supplier Shipment Delay Predictor")
st.markdown("##### AI-powered logistics analytics dashboard for analyzing supplier shipment delays and route performance.")


tab1, tab2 = st.tabs(["Dashboard Analytics", "AI Prediction Model"])

with tab1:
    # --- CASCADING SIDEBAR FILTERS ---
    st.sidebar.header("Filters")

    if 'reset' not in st.session_state:
        st.session_state.reset = False

    def reset_filters():
        st.session_state.reset = True

    st.sidebar.button("Reset Filters", on_click=reset_filters)

    if st.session_state.reset:
        for key in ['transit_mode', 'origin_city', 'dest_city', 'weather', 'supplier']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.reset = False

    df_filtered = df.copy()

    # Cascading Logic
    transit_modes = ["All"] + df_filtered['transit_mode'].unique().tolist()
    selected_transit = st.sidebar.selectbox("Transit Mode", transit_modes, key='transit_mode')
    if selected_transit != "All":
        df_filtered = df_filtered[df_filtered['transit_mode'] == selected_transit]

    origin_cities = ["All"] + sorted(df_filtered['origin_city'].unique().tolist())
    if 'origin_city' in st.session_state and st.session_state.origin_city not in origin_cities:
        st.session_state.origin_city = "All"
    selected_origin = st.sidebar.selectbox("Origin City", origin_cities, key='origin_city')
    if selected_origin != "All":
        df_filtered = df_filtered[df_filtered['origin_city'] == selected_origin]

    # Destination Options Logic
    dest_source_df = df.copy()
    if selected_transit != "All":
        dest_source_df = dest_source_df[dest_source_df['transit_mode'] == selected_transit]
    if selected_origin != "All":
        dest_source_df = dest_source_df[dest_source_df['origin_city'] == selected_origin]
        
    destination_options = sorted(
        dest_source_df['destination_city'].dropna().astype(str).str.strip().unique().tolist()
    )
    dest_cities = ["All"] + destination_options
    
    if 'dest_city' in st.session_state and st.session_state.dest_city not in dest_cities:
        st.session_state.dest_city = "All"
    selected_dest = st.sidebar.selectbox("Destination City", dest_cities, key='dest_city')
    if selected_dest != "All":
        df_filtered = df_filtered[df_filtered['destination_city'] == selected_dest]

    weather_conditions = ["All"] + sorted(df_filtered['weather_condition'].unique().tolist())
    if 'weather' in st.session_state and st.session_state.weather not in weather_conditions:
        st.session_state.weather = "All"
    selected_weather = st.sidebar.selectbox("Weather Condition", weather_conditions, key='weather')
    if selected_weather != "All":
        df_filtered = df_filtered[df_filtered['weather_condition'] == selected_weather]

    suppliers = ["All"] + sorted(df_filtered['supplier_id'].unique().tolist())
    if 'supplier' in st.session_state and st.session_state.supplier not in suppliers:
        st.session_state.supplier = "All"
    selected_supplier = st.sidebar.selectbox("Supplier ID", suppliers, key='supplier')
    if selected_supplier != "All":
        df_filtered = df_filtered[df_filtered['supplier_id'] == selected_supplier]

    if df_filtered.empty:
        st.warning("No shipment data is available for the selected filters.")
    else:
        # --- SECTION 1 & 2: DATA OVERVIEW & KPIs ---
        st.header("Overview & KPIs")

        col1, col2, col3, col4, col5 = st.columns(5)

        total_shipments = len(df_filtered)
        delayed_pct = (df_filtered['delayed'] == 'Yes').mean() * 100 if total_shipments > 0 else 0
        avg_delay_days = df_filtered['delay_days'].mean() if total_shipments > 0 else 0

        df_filtered['route'] = df_filtered['origin_city'] + " → " + df_filtered['destination_city']
        route_delays = df_filtered.groupby('route')['delay_days'].mean()
        most_delay_prone_route = route_delays.idxmax() if not route_delays.empty else "--"

        supplier_rel = df_filtered.groupby('supplier_id')['supplier_reliability_score'].max()
        most_reliable_supplier = supplier_rel.idxmax() if not supplier_rel.empty else "--"

        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-title">Total Shipments</div>
                <div class="metric-value">{total_shipments:,}</div>
            </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-title">Delayed Rate</div>
                <div class="metric-value">{delayed_pct:.1f}%</div>
            </div>
            ''', unsafe_allow_html=True)

        with col3:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-title">Average Delay</div>
                <div class="metric-value">{avg_delay_days:.2f} <span style="font-size:18px; color:#6c757d; font-weight:normal;">days</span></div>
                <div class="metric-subtext">Negative values indicate early arrival.</div>
            </div>
            ''', unsafe_allow_html=True)

        with col4:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-title">Most Delay-Prone Route</div>
                <div class="metric-value-text">{most_delay_prone_route}</div>
            </div>
            ''', unsafe_allow_html=True)

        with col5:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-title">Most Reliable Supplier</div>
                <div class="metric-value-text">{most_reliable_supplier}</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'''
        <div class="data-overview">
            <div><strong>Data Range:</strong> {df_filtered['departure_date'].min().strftime('%Y-%m-%d')} to {df_filtered['departure_date'].max().strftime('%Y-%m-%d')}</div>
            <div><strong>Suppliers:</strong> {df_filtered['supplier_id'].nunique()}</div>
            <div><strong>Origin Cities:</strong> {df_filtered['origin_city'].nunique()}</div>
            <div><strong>Destination Cities:</strong> {df_filtered['destination_city'].nunique()}</div>
        </div>
        ''', unsafe_allow_html=True)
        

        # --- SECTION 3: SHIPMENT DELAY ANALYSIS ---
        st.header("Shipment Delay Analysis")
        col_3a, col_3b = st.columns(2)

        with col_3a:
            mode_delay = df_filtered.groupby('transit_mode')['delay_days'].mean().reset_index()
            fig_mode = px.bar(mode_delay, x='transit_mode', y='delay_days', 
                              title="Average Delay by Transit Mode",
                              labels={'transit_mode': 'Transit Mode', 'delay_days': 'Avg Delay (Days)'},
                              color_discrete_sequence=['#3B82F6'])
            fig_mode.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_mode, use_container_width=True)

        with col_3b:
            color_map = {'On-Time': '#22C55E', 'Minor Delay': '#EAB308', 'Major Delay': '#EF4444'}
            fig_weather_scatter = px.scatter(df_filtered, x='weather_severity_index', y='delay_days', 
                                             color='delay_category', color_discrete_map=color_map,
                                             title="Weather Severity vs Delay Days",
                                             labels={'weather_severity_index': 'Weather Severity Index', 'delay_days': 'Delay Days', 'delay_category': 'Category'},
                                             opacity=0.6)
            fig_weather_scatter.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_weather_scatter, use_container_width=True)

        col_3c, col_3d = st.columns(2)

        with col_3c:
            df_filtered['month_year'] = df_filtered['departure_date'].dt.to_period('M')
            monthly_trend = df_filtered.groupby('month_year')['delay_days'].mean().reset_index()
            monthly_trend['month_year_str'] = monthly_trend['month_year'].astype(str)
            
            fig_trend = px.line(monthly_trend, x='month_year_str', y='delay_days', markers=True,
                                title="Monthly Average Delay Trend",
                                labels={'month_year_str': 'Month', 'delay_days': 'Avg Delay (Days)'},
                                color_discrete_sequence=['#3B82F6'])
            fig_trend.update_layout(plot_bgcolor='white', xaxis_tickangle=-45)
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_3d:
            delay_dist = df_filtered['delay_category'].value_counts().reset_index()
            delay_dist.columns = ['delay_category', 'count']
            fig_donut = px.pie(delay_dist, values='count', names='delay_category', hole=0.5,
                               title="Delay Category Distribution",
                               color='delay_category', color_discrete_map=color_map)
            st.plotly_chart(fig_donut, use_container_width=True)

        

        # --- SECTION 4: ROUTE ANALYSIS ---
        st.header("Route Analysis")
        
        is_single_route = ('origin_city' in st.session_state and st.session_state.origin_city != "All" and 
                           'dest_city' in st.session_state and st.session_state.dest_city != "All")
        
        if is_single_route:
            st.info("Single route selected. Rendering route performance card.")
            single_stats = df_filtered.groupby('route').agg(
                Shipment_Count=('shipment_id', 'count'),
                Average_Delay=('delay_days', 'mean'),
                Early_Count=('delay_days', lambda x: (x < 0).sum()),
                Delayed_Count=('delayed', lambda x: (x == 'Yes').sum())
            ).reset_index()
            
            if not single_stats.empty:
                r_stat = single_stats.iloc[0]
                total = r_stat['Shipment_Count']
                early_rate = (r_stat['Early_Count'] / total) * 100 if total > 0 else 0
                delay_rate = (r_stat['Delayed_Count'] / total) * 100 if total > 0 else 0
                
                st.subheader(f"Route: {r_stat['route']}")
                col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
                with col_r1:
                    st.metric("Average Delay", f"{r_stat['Average_Delay']:.2f} days")
                with col_r2:
                    st.metric("Early Shipments", f"{r_stat['Early_Count']}")
                with col_r3:
                    st.metric("Delayed Shipments", f"{r_stat['Delayed_Count']}")
                with col_r4:
                    st.metric("Early Arrival Rate", f"{early_rate:.1f}%")
                with col_r5:
                    st.metric("Delayed Rate", f"{delay_rate:.1f}%")
        
        route_heatmap_data = df_filtered.pivot_table(index='origin_city', columns='destination_city', values='delay_days', aggfunc='mean')
        
        fig_heatmap = px.imshow(route_heatmap_data, 
                                title="Origin × Destination Average Delay Heatmap",
                                labels=dict(x="Destination City", y="Origin City", color="Avg Delay (days)"),
                                color_continuous_scale='RdBu_r', color_continuous_midpoint=0, aspect="auto")
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        st.subheader("Route Performance Table")
        route_stats = df_filtered.groupby('route').agg(
            Shipment_Count=('shipment_id', 'count'),
            Average_Delay=('delay_days', 'mean'),
            Early_Count=('delay_days', lambda x: (x < 0).sum()),
            Delayed_Count=('delayed', lambda x: (x == 'Yes').sum())
        ).reset_index()
        
        route_stats = route_stats.sort_values(by='Average_Delay', ascending=False)
        route_stats['Early_Rate'] = (route_stats['Early_Count'] / route_stats['Shipment_Count'] * 100).round(1).astype(str) + '%'
        route_stats['Delay_Rate'] = (route_stats['Delayed_Count'] / route_stats['Shipment_Count'] * 100).round(1).astype(str) + '%'
        route_stats['Average_Delay'] = route_stats['Average_Delay'].round(2).astype(str) + ' days'
        route_stats = route_stats.rename(columns={
            'route': 'Route',
            'Shipment_Count': 'Shipments',
            'Average_Delay': 'Avg Delay',
            'Early_Count': 'Early',
            'Early_Rate': 'Early Rate',
            'Delayed_Count': 'Delayed',
            'Delay_Rate': 'Delayed Rate'
        })
        st.dataframe(route_stats, use_container_width=True, hide_index=True)

        

        # --- SECTION 5: WEATHER ANALYSIS ---
        st.header("Weather Analysis")
        fig_box = px.box(df_filtered, x='weather_condition', y='delay_days', 
                         title="Delay Distribution by Weather Condition",
                         labels={'weather_condition': 'Weather Condition', 'delay_days': 'Delay Days'},
                         color_discrete_sequence=['#3B82F6'])
        fig_box.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig_box, use_container_width=True)

        

        # --- SECTION 6: SUPPLIER ANALYSIS ---
        st.header("Supplier Analysis (Top 10 by Reliability)")
        supplier_stats = df_filtered.groupby('supplier_id').agg(
            supplier_reliability_score=('supplier_reliability_score', 'first'),
            avg_delay_days=('delay_days', 'mean'),
            shipment_count=('shipment_id', 'count')
        ).reset_index()

        top_10_suppliers = supplier_stats.sort_values(by='supplier_reliability_score', ascending=False).head(10)
        top_10_suppliers['supplier_reliability_score'] = top_10_suppliers['supplier_reliability_score'].round(3)
        top_10_suppliers['avg_delay_days'] = top_10_suppliers['avg_delay_days'].round(2)

        plot_df = top_10_suppliers.sort_values(by='supplier_reliability_score', ascending=True)
        custom_data = plot_df[['supplier_id', 'supplier_reliability_score', 'avg_delay_days', 'shipment_count']].values
        hovertemplate = (
            "Supplier: %{customdata[0]}<br>"
            "Reliability Score: %{customdata[1]:.3f}<br>"
            "Average Delay: %{customdata[2]:.2f} days<br>"
            "Total Shipments: %{customdata[3]}<extra></extra>"
        )

        fig_supplier = go.Figure(data=[
            go.Bar(
                name='Reliability Score', 
                y=plot_df['supplier_id'], 
                x=plot_df['supplier_reliability_score'], 
                orientation='h',
                marker_color='#3B82F6',
                customdata=custom_data,
                hovertemplate=hovertemplate
            )
        ])

        min_val = plot_df['supplier_reliability_score'].min()
        max_val = plot_df['supplier_reliability_score'].max()
        x_range = [max(0.0, min_val - 0.05), min(1.0, max_val + 0.02)]

        fig_supplier.update_layout(
            title="Top 10 Suppliers by Reliability",
            yaxis_title="Supplier ID",
            xaxis=dict(
                title="Reliability Score",
                range=x_range
            ),
            plot_bgcolor='white',
            showlegend=False
        )
        st.plotly_chart(fig_supplier, use_container_width=True)

        st.dataframe(top_10_suppliers.rename(columns={
            'supplier_id': 'Supplier ID', 
            'supplier_reliability_score': 'Reliability Score',
            'avg_delay_days': 'Avg Delay Days',
            'shipment_count': 'Total Shipments'
        }), use_container_width=True, hide_index=True)

        

        # --- SECTION 7: DATA TABLE ---
        st.header("Shipment Data")
        with st.expander("View Filtered Shipment Records"):
            st.dataframe(df_filtered.drop(columns=['route', 'month_year', 'month_year_str'], errors='ignore'), use_container_width=True)

with tab2:
    st.header("AI Prediction Model")
    st.markdown("This Random Forest Classifier is trained strictly on the currently loaded dataset to predict whether a shipment will be delayed.")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("Model Performance Summary")
        st.markdown(f"**Model:** Random Forest Classifier (Tuned)")
        st.markdown(f"**Training Records:** {metrics['training_rows']}")
        st.markdown(f"**Testing Records:** {metrics['testing_rows']}")
        st.markdown(f"**Accuracy:** {metrics['accuracy']:.2%}")
        st.markdown(f"**Precision:** {metrics['precision']:.2%}")
        st.markdown(f"**Recall:** {metrics['recall']:.2%}")
        st.markdown(f"**F1 Score:** {metrics['f1']:.2%}")
        st.markdown(f"**ROC-AUC:** {metrics['roc_auc']:.2%}")
        
        st.subheader("Confusion Matrix")
        cm = metrics['confusion_matrix']
        fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale='Blues',
                           labels=dict(x="Predicted", y="Actual"),
                           x=['On-Time', 'Delayed'], y=['On-Time', 'Delayed'],
                           title="Confusion Matrix (Test Set)")
        st.plotly_chart(fig_cm, use_container_width=True)
        
        st.subheader("Global Feature Importance")
        fi_disp = feature_imp[['Feature_Name', 'Importance']].copy()
        fi_disp['Importance'] = (fi_disp['Importance'] * 100).round(2).astype(str) + '%'
        # Group transit mode imports
        fi_disp = fi_disp.groupby('Feature_Name')['Importance'].apply(lambda x: pd.to_numeric(x.str.rstrip('%')).sum()).reset_index()
        fi_disp = fi_disp.sort_values('Importance', ascending=False).reset_index(drop=True)
        fi_disp.index = fi_disp.index + 1
        fi_disp.index.name = 'Rank'
        fi_disp['Importance'] = fi_disp['Importance'].round(2).astype(str) + '%'
        st.dataframe(fi_disp, use_container_width=True)
        
    with col_b:
        st.subheader("Live Prediction Interface")
        
        pred_weather = st.slider("Weather Severity Index", 0.0, 10.0, 2.5)
        pred_traffic = st.slider("Traffic Congestion Level", 0.0, 10.0, 5.0)
        pred_route = st.slider("Route Risk Score", 0.0, 10.0, 4.0)
        pred_rel = st.slider("Supplier Reliability Score", 0.0, 1.0, 0.75)
        pred_dist = st.number_input("Distance (km)", min_value=10, max_value=5000, value=1200)
        pred_mode = st.selectbox("Transit Mode", df_raw['transit_mode'].unique(), key='pred_mode')
        
        if st.button("Predict Delay Risk"):
            input_data = pd.DataFrame([{
                'weather_severity_index': pred_weather,
                'traffic_congestion_level': pred_traffic,
                'route_risk_score': pred_route,
                'supplier_reliability_score': pred_rel,
                'distance_km': pred_dist,
                'transit_mode': pred_mode
            }])
            
            prob = model.predict_proba(input_data)[0][1]
            pred = model.predict(input_data)[0]
            
            st.markdown("### Prediction Result")
            if pred == 1:
                st.error(f"**⚠️ Likely Delayed**\n\n**Predicted probability:** {prob:.1%}")
            else:
                st.success(f"**✅ Likely On-Time**\n\n**Predicted probability:** {prob:.1%}")
                
            st.markdown("### Input Summary")
            st.markdown(f"**Weather Severity:** {pred_weather} / 10 | **Traffic Congestion:** {pred_traffic} / 10 | **Route Risk:** {pred_route} / 10")
            st.markdown(f"**Supplier Reliability:** {pred_rel} | **Distance:** {pred_dist} km | **Transit Mode:** {pred_mode}")
                
            st.markdown("### Prediction Explanation")
            
            # Local Explanation via SHAP
            processed_input = model.named_steps['preprocessor'].transform(input_data)
            shap_values = explainer.shap_values(processed_input)
            
            # shap_values[1] is for the positive class (Delayed)
            shap_contributions = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0, :, 1] if len(shap_values.shape)==3 else shap_values[0]
            
            # Map contributions to original features
            feature_mapping = {}
            for i, feat in enumerate(feature_names):
                if feat.startswith('transit_mode_'):
                    feature_mapping['Transit Mode'] = feature_mapping.get('Transit Mode', 0) + shap_contributions[i]
                elif feat == 'weather_severity_index':
                    feature_mapping['Weather Severity'] = shap_contributions[i]
                elif feat == 'traffic_congestion_level':
                    feature_mapping['Traffic Congestion'] = shap_contributions[i]
                elif feat == 'route_risk_score':
                    feature_mapping['Route Risk'] = shap_contributions[i]
                elif feat == 'supplier_reliability_score':
                    feature_mapping['Supplier Reliability'] = shap_contributions[i]
                elif feat == 'distance_km':
                    feature_mapping['Distance'] = shap_contributions[i]
            
            risk_increasing = []
            risk_reducing = []
            
            for f, contrib in feature_mapping.items():
                if contrib > 0.01:
                    risk_increasing.append((f, contrib))
                elif contrib < -0.01:
                    risk_reducing.append((f, contrib))
                    
            risk_increasing = sorted(risk_increasing, key=lambda x: x[1], reverse=True)
            risk_reducing = sorted(risk_reducing, key=lambda x: x[1])
            
            st.markdown("**Why the model predicts this:**")
            
            col_inc, col_dec = st.columns(2)
            with col_dec:
                st.markdown("**Risk-reducing factors**")
                if risk_reducing:
                    for f, c in risk_reducing:
                        st.markdown(f"<span style='color: #22C55E;'>✓ {f}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("None")
                    
            with col_inc:
                st.markdown("**Risk-increasing factors**")
                if risk_increasing:
                    for f, c in risk_increasing:
                        st.markdown(f"<span style='color: #EF4444;'>⚠ {f}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("None")
                    
            main_factor = ""
            max_abs = 0
            for f, c in feature_mapping.items():
                if abs(c) > max_abs:
                    max_abs = abs(c)
                    main_factor = f
                    
            st.markdown(f"**Main factor:** {main_factor}")
