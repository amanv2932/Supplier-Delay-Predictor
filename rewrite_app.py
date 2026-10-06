import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
imports_to_add = """
import shap
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import roc_auc_score
"""
content = content.replace('from sklearn.pipeline import Pipeline', 'from sklearn.pipeline import Pipeline' + imports_to_add)

# Replace train_model function
old_train_model = """@st.cache_resource
def train_model(df, mtime):
    features = ['weather_severity_index', 'traffic_congestion_level', 'route_risk_score', 'supplier_reliability_score', 'distance_km', 'transit_mode']
    X = df[features].copy()
    y = (df['delayed'] == 'Yes').astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['transit_mode'])
        ],
        remainder='passthrough'
    )
    
    model = Pipeline(steps=[('preprocessor', preprocessor),
                            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))])
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
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
    
    return model, metrics, feature_imp"""

new_train_model = """@st.cache_resource
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
    
    return model, metrics, feature_imp, explainer, feature_names"""

content = content.replace(old_train_model, new_train_model)
content = content.replace("model, metrics, feature_imp = train_model(df_raw, file_mtime)", "model, metrics, feature_imp, explainer, feature_names = train_model(df_raw, file_mtime)")

# Rewrite Tab 2
old_tab2 = """with tab2:
    st.header("AI Prediction Model")
    st.markdown("This Random Forest Classifier is trained strictly on the currently loaded dataset to predict whether a shipment will be delayed.")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("Model Evaluation Metrics")
        st.markdown(f"**Accuracy:** {metrics['accuracy']:.2%}")
        st.markdown(f"**Precision:** {metrics['precision']:.2%}")
        st.markdown(f"**Recall:** {metrics['recall']:.2%}")
        st.markdown(f"**F1 Score:** {metrics['f1']:.2%}")
        
        st.subheader("Feature Importance")
        st.dataframe(feature_imp, hide_index=True)
        
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
            
            if pred == 1:
                st.error(f"⚠️ Likely Delayed (Probability: {prob:.1%})")
            else:
                st.success(f"✅ Likely On-Time (Probability: {1-prob:.1%})")
                
            st.info("Prediction Insight: The prediction is derived using local deterministic logic based heavily on the feature importances (e.g., high traffic or route risk significantly increases probability of delay, while a strong supplier reliability mitigates it).")"""

new_tab2 = """with tab2:
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
                st.error(f"**⚠️ Likely Delayed**\\n\\n**Predicted probability:** {prob:.1%}")
            else:
                st.success(f"**✅ Likely On-Time**\\n\\n**Predicted probability:** {prob:.1%}")
                
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
                        st.markdown(f"✓ {f}")
                else:
                    st.markdown("None")
                    
            with col_inc:
                st.markdown("**Risk-increasing factors**")
                if risk_increasing:
                    for f, c in risk_increasing:
                        st.markdown(f"⚠ {f}")
                else:
                    st.markdown("None")
                    
            main_factor = ""
            max_abs = 0
            for f, c in feature_mapping.items():
                if abs(c) > max_abs:
                    max_abs = abs(c)
                    main_factor = f
                    
            st.markdown(f"**Main factor:** {main_factor}")"""

content = content.replace(old_tab2, new_tab2)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
