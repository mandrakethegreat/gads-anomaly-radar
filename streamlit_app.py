import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json

# Page config
st.set_page_config(
    page_title="Google Ads Anomaly Radar",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📊 Google Ads Anomaly Radar (GAAR)")
st.markdown("Detect and explain performance anomalies in your Google Ads campaigns")

# Sidebar config
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_url = st.text_input(
        "FastAPI Backend URL",
        value="http://localhost:8000",
        help="URL of your FastAPI backend"
    )
    
    selected_date = st.date_input(
        "Select Date",
        value=datetime.now().date(),
        help="Date to analyze (defaults to today)"
    )
    
    min_z_score = st.slider(
        "Min Z-Score Threshold",
        min_value=1.0,
        max_value=5.0,
        value=2.0,
        step=0.5,
        help="Higher = only most significant anomalies"
    )
    
    st.divider()
    st.markdown("### Instructions")
    st.markdown("""
    1. **Configure** your backend URL and date range
    2. **Ingest** Google Ads data
    3. **Detect** anomalies
    4. **Review** and **Explain** anomalies
    """)

# Main tabs
tab1, tab2, tab3 = st.tabs(["🔄 Ingest Data", "📈 Anomalies", "💡 Explain"])

# ===== TAB 1: INGEST =====
with tab1:
    st.header("Ingest Google Ads Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Fetch Data from Google Ads")
        if st.button("📥 Ingest Data", key="ingest_btn", use_container_width=True):
            try:
                with st.spinner("Ingesting data..."):
                    response = requests.post(
                        f"{api_url}/ingest",
                        params={"date": selected_date.isoformat()},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Successfully ingested {result['rows']} rows for {result['date']}")
                        st.json(result)
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.write(response.text)
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to backend at {api_url}")
                st.info("Make sure your FastAPI server is running: `uvicorn app.main:app --reload --port 8000`")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.markdown("### Alternative: Upload Data File")
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=["csv"],
            help="CSV with columns: customer_id, campaign_id, ad_group_id, clicks, impressions, cost, conversions, conv_value"
        )
        
        if uploaded_file:
            st.info("File upload integration can be added to parse and send data to backend.")
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head(10), use_container_width=True)

# ===== TAB 2: ANOMALIES =====
with tab2:
    st.header("Detected Anomalies")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔍 Detect Anomalies", key="detect_btn", use_container_width=True):
            st.session_state.detect_clicked = True
    
    if st.session_state.get("detect_clicked"):
        try:
            with st.spinner("Detecting anomalies..."):
                response = requests.get(
                    f"{api_url}/anomalies",
                    params={
                        "date": selected_date.isoformat(),
                        "min_z": min_z_score
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    anomalies = result.get("anomalies", [])
                    
                    if not anomalies:
                        st.info(f"✅ No anomalies detected for {selected_date} with Z-score >= {min_z_score}")
                    else:
                        st.success(f"Found {len(anomalies)} anomalies")
                        
                        # Convert to dataframe for better display
                        df_anomalies = pd.DataFrame(anomalies)
                        
                        # Reorder and format columns for readability
                        display_cols = [
                            "entity_type", "entity_id", "metric", "direction",
                            "observed", "expected", "zscore"
                        ]
                        available_cols = [col for col in display_cols if col in df_anomalies.columns]
                        df_display = df_anomalies[available_cols].copy()
                        
                        # Format numeric columns
                        for col in ["observed", "expected", "zscore"]:
                            if col in df_display.columns:
                                df_display[col] = df_display[col].round(2)
                        
                        st.dataframe(df_display, use_container_width=True, hide_index=True)
                        
                        # Store anomalies in session state for explain tab
                        st.session_state.anomalies = anomalies
                        
                        # Summary stats
                        st.divider()
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Anomalies", len(anomalies))
                        
                        with col2:
                            entity_types = df_anomalies["entity_type"].nunique()
                            st.metric("Entity Types", entity_types)
                        
                        with col3:
                            metrics = df_anomalies["metric"].nunique()
                            st.metric("Metric Types", metrics)
                        
                        with col4:
                            avg_z = df_anomalies["zscore"].mean()
                            st.metric("Avg Z-Score", f"{avg_z:.2f}")
                
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.write(response.text)
        
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to backend at {api_url}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ===== TAB 3: EXPLAIN =====
with tab3:
    st.header("Explain Anomalies")
    
    if not st.session_state.get("anomalies"):
        st.info("👈 First, detect anomalies in the 'Anomalies' tab")
    else:
        anomalies = st.session_state.anomalies
        
        # Create a selectable list of anomalies
        anomaly_labels = [
            f"{a.get('entity_type')} {a.get('entity_id')} - {a.get('metric')} ({a.get('direction')})"
            for a in anomalies
        ]
        
        selected_idx = st.selectbox(
            "Select an anomaly to explain",
            range(len(anomalies)),
            format_func=lambda i: anomaly_labels[i]
        )
        
        if selected_idx is not None:
            selected_anomaly = anomalies[selected_idx]
            
            # Display anomaly details
            st.markdown("### Anomaly Details")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Entity Type", selected_anomaly.get("entity_type", "N/A"))
            with col2:
                st.metric("Entity ID", selected_anomaly.get("entity_id", "N/A"))
            with col3:
                st.metric("Metric", selected_anomaly.get("metric", "N/A"))
            with col4:
                st.metric("Direction", selected_anomaly.get("direction", "N/A"))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Z-Score", f"{selected_anomaly.get('zscore', 0):.2f}")
            with col2:
                st.metric("Observed", f"{selected_anomaly.get('observed', 0):.2f}")
            with col3:
                st.metric("Expected", f"{selected_anomaly.get('expected', 0):.2f}")
            
            st.divider()
            
            # Get explanation
            if st.button("💡 Get Explanation", use_container_width=True):
                try:
                    # Find anomaly ID from DB (or use index as fallback)
                    anomaly_id = selected_idx + 1  # Assuming sequential IDs
                    
                    with st.spinner("Generating explanation..."):
                        response = requests.post(
                            f"{api_url}/explain",
                            json={"anomaly_id": anomaly_id},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            explanation = response.json()
                            
                            if "error" in explanation:
                                st.warning(f"⚠️ {explanation['error']}")
                            else:
                                st.success("✅ Explanation Generated")
                                
                                # Display explanation
                                if "explanation" in explanation:
                                    st.markdown("### Likely Causes")
                                    st.write(explanation["explanation"])
                                
                                if "suggestions" in explanation:
                                    st.markdown("### Suggested Actions")
                                    suggestions = explanation["suggestions"]
                                    if isinstance(suggestions, list):
                                        for i, suggestion in enumerate(suggestions, 1):
                                            st.write(f"{i}. {suggestion}")
                                    else:
                                        st.write(suggestions)
                                
                                # Show full response for debugging
                                with st.expander("Full Response"):
                                    st.json(explanation)
                        
                        else:
                            st.error(f"❌ Error: {response.status_code}")
                            st.write(response.text)
                
                except requests.exceptions.ConnectionError:
                    st.error(f"❌ Cannot connect to backend at {api_url}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.markdown("""
---
**Google Ads Anomaly Radar** | Powered by FastAPI + Streamlit  
[Documentation](https://github.com/your-repo) | [Report Issues](https://github.com/your-repo/issues)
""")
