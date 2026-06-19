import os
import time
import numpy as np
import pandas as pd
import streamlit as st

# Set page config for a premium wide layout
st.set_page_config(
    page_title="Cherokee Phoenix OCR - Training Metrics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .metric-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #9ca3af;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.875rem;
        color: #f3f4f6;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #10b981;
        margin-top: 4px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Discover Runs
def discover_runs(base_dir="training_data"):
    runs = {}
    if not os.path.exists(base_dir):
        return runs
    
    for root, dirs, files in os.walk(base_dir):
        has_iter = "iteration_metrics.csv" in files
        has_epoch = "epoch_metrics.csv" in files
        if has_iter or has_epoch:
            rel_path = os.path.relpath(root, base_dir)
            if rel_path == ".":
                rel_path = "root_run"
            runs[rel_path] = {
                "dir": root,
                "iteration_metrics": os.path.join(root, "iteration_metrics.csv") if has_iter else None,
                "epoch_metrics": os.path.join(root, "epoch_metrics.csv") if has_epoch else None
            }
    return runs

# Mock / Demo Data Generator
def generate_demo_data():
    np.random.seed(int(time.time()) % 1000) # dynamic seed for realistic ticking changes in demo mode
    
    # 1. Iteration metrics (e.g. 500 iterations)
    iterations = np.arange(10, 510, 10)
    train_loss = 0.5 * np.exp(-iterations / 150) + 0.05 * np.random.randn(len(iterations)) + 0.05
    train_loss = np.clip(train_loss, 0.01, None)
    bcer_train = 0.8 * np.exp(-iterations / 120) + 0.04 * np.random.randn(len(iterations)) + 0.02
    bcer_train = np.clip(bcer_train, 0.0, 1.0)
    bwer_train = 0.9 * np.exp(-iterations / 140) + 0.05 * np.random.randn(len(iterations)) + 0.05
    bwer_train = np.clip(bwer_train, 0.0, 1.0)
    
    iter_df = pd.DataFrame({
        "iteration": iterations,
        "train_loss": train_loss,
        "mean_rms": train_loss,  # alias
        "bcer_train": bcer_train,
        "bwer_train": bwer_train,
        "delta": 0.001 * np.random.randn(len(iterations)),
        "skip_ratio": np.zeros(len(iterations))
    })
    
    # 2. Epoch metrics (e.g. 10 epochs)
    epochs = np.arange(1, 11)
    phoenix_cer = 0.45 * np.exp(-epochs / 3) + 0.02 * np.random.randn(len(epochs)) + 0.01
    phoenix_cer = np.clip(phoenix_cer, 0.005, 1.0)
    cnt_cer = 0.55 * np.exp(-epochs / 2.5) + 0.02 * np.random.randn(len(epochs)) + 0.02
    cnt_cer = np.clip(cnt_cer, 0.01, 1.0)
    weighted_cer = phoenix_cer * 0.7 + cnt_cer * 0.3
    
    epoch_df = pd.DataFrame({
        "epoch": epochs,
        "phoenix_CER": phoenix_cer,
        "cnt_CER": cnt_cer,
        "weighted_CER": weighted_cer
    })
    
    return iter_df, epoch_df

# Title (stays static)
st.title("📊 Cherokee Phoenix OCR Training Monitor")
st.markdown("Real-time telemetry, model convergence charts, and validation benchmarks.")

# Sidebar Configuration (stays static)
st.sidebar.header("🎛️ Control Panel")

runs = discover_runs()
demo_mode = False

if not runs:
    st.sidebar.warning("⚠️ No active or completed runs discovered in `training_data/`.")
    st.sidebar.info("Loading Dashboard in **Demo Mode** with synthetic data.")
    demo_mode = True
    selected_run_name = "Demo Run (Synthetic)"
else:
    run_options = list(runs.keys())
    if st.sidebar.checkbox("Force Demo Mode", value=False):
        demo_mode = True
        selected_run_name = "Demo Run (Synthetic)"
    else:
        selected_run_name = st.sidebar.selectbox("📂 Select Training Run", run_options)

# Auto-Refresh Toggle (stays static)
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Live Refresh")
auto_refresh = st.sidebar.toggle("Enable Live Auto-Refresh", value=not demo_mode)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", min_value=5, max_value=60, value=10, step=5)

# Wrap the rendering in a non-blocking @st.fragment to prevent full page greying!
@st.fragment(run_every=refresh_interval if auto_refresh else None)
def render_dashboard_content(run_name, is_demo):
    # Load Data based on selection
    if is_demo:
        iter_df, epoch_df = generate_demo_data()
        status_text = "🟢 Active (Demo Simulation)"
    else:
        run_info = runs[run_name]
        status_text = f"🟢 Connected to: `{run_name}`"
        
        # Load iteration metrics
        if run_info["iteration_metrics"] and os.path.exists(run_info["iteration_metrics"]):
            try:
                iter_df = pd.read_csv(run_info["iteration_metrics"])
                # Normalize common columns
                if "mean_rms" in iter_df.columns and "train_loss" not in iter_df.columns:
                    iter_df["train_loss"] = iter_df["mean_rms"]
                elif "train_loss" in iter_df.columns and "mean_rms" not in iter_df.columns:
                    iter_df["mean_rms"] = iter_df["train_loss"]
            except Exception as e:
                st.error(f"Error loading iteration metrics: {e}")
                iter_df = pd.DataFrame()
        else:
            iter_df = pd.DataFrame()
            
        # Load epoch metrics
        if run_info["epoch_metrics"] and os.path.exists(run_info["epoch_metrics"]):
            try:
                epoch_df = pd.read_csv(run_info["epoch_metrics"])
                # Normalize common casing
                c_map = {c.lower(): c for c in epoch_df.columns}
                for target in ["phoenix_cer", "cnt_cer", "weighted_cer"]:
                    if target in c_map and target not in epoch_df.columns:
                        epoch_df[target] = epoch_df[c_map[target]]
            except Exception as e:
                st.error(f"Error loading epoch metrics: {e}")
                epoch_df = pd.DataFrame()
        else:
            epoch_df = pd.DataFrame()

    # Quick sanity check/handling of empty files
    if iter_df.empty and epoch_df.empty:
        st.warning("⚠️ Selected run does not contain any valid metrics in `iteration_metrics.csv` or `epoch_metrics.csv` yet.")
        st.info("Check back soon or start training to view statistics.")
        return

    # Compute Key Metrics for Display Cards
    last_epoch = "N/A"
    last_iteration = "N/A"
    best_phoenix_cer = "N/A"
    best_phoenix_epoch = "N/A"
    best_weighted_cer = "N/A"
    best_weighted_epoch = "N/A"
    current_loss = "N/A"

    if not iter_df.empty:
        if "iteration" in iter_df.columns:
            last_iteration = int(iter_df["iteration"].iloc[-1])
        if "train_loss" in iter_df.columns:
            current_loss = f"{iter_df['train_loss'].iloc[-1]:.4f}"

    if not epoch_df.empty:
        if "epoch" in epoch_df.columns:
            last_epoch = int(epoch_df["epoch"].iloc[-1])
        
        p_cer_cols = [c for c in epoch_df.columns if c.lower() == "phoenix_cer"]
        if p_cer_cols and "epoch" in epoch_df.columns:
            col = p_cer_cols[0]
            best_idx = epoch_df[col].idxmin()
            best_p_val = epoch_df[col].loc[best_idx]
            best_phoenix_cer = f"{best_p_val * 100:.2f}%"
            best_phoenix_epoch = int(epoch_df["epoch"].loc[best_idx])
            
        w_cer_cols = [c for c in epoch_df.columns if c.lower() == "weighted_cer"]
        if w_cer_cols and "epoch" in epoch_df.columns:
            col = w_cer_cols[0]
            best_idx = epoch_df[col].idxmin()
            best_w_val = epoch_df[col].loc[best_idx]
            best_weighted_cer = f"{best_w_val * 100:.2f}%"
            best_weighted_epoch = int(epoch_df["epoch"].loc[best_idx])

    # Render Key Metrics Cards in row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Status & Progress</div>
            <div class="metric-value">Epoch {last_epoch}</div>
            <div class="metric-sub">Iteration: {last_iteration} | {status_text}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10b981;">
            <div class="metric-label">Best Phoenix CER</div>
            <div class="metric-value">{best_phoenix_cer}</div>
            <div class="metric-sub">Achieved at Epoch {best_phoenix_epoch}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #8b5cf6;">
            <div class="metric-label">Best Weighted CER</div>
            <div class="metric-value">{best_weighted_cer}</div>
            <div class="metric-sub">Achieved at Epoch {best_weighted_epoch}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #f59e0b;">
            <div class="metric-label">Current Training Loss</div>
            <div class="metric-value">{current_loss}</div>
            <div class="metric-sub">RMS Error (Last Iteration)</div>
        </div>
        """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Convergence Charts", "📊 Tabular Metrics", "🛠️ Environment Info"])

    with tab1:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("1. Iteration-Level Training Stats")
            if not iter_df.empty:
                cols_to_plot = []
                for col in ["train_loss", "bcer_train", "bwer_train"]:
                    if col in iter_df.columns:
                        cols_to_plot.append(col)
                
                if cols_to_plot:
                    chart_df = iter_df.set_index("iteration")[cols_to_plot]
                    st.line_chart(chart_df, height=350)
                else:
                    st.info("Missing train_loss, bcer_train, or bwer_train columns in iteration metrics.")
            else:
                st.info("No iteration metrics to plot.")
                
        with col_chart2:
            st.subheader("2. Epoch-Level Evaluation Stats")
            if not epoch_df.empty:
                cols_to_plot = []
                for target in ["phoenix_cer", "cnt_cer", "weighted_cer"]:
                    found = [c for c in epoch_df.columns if c.lower() == target]
                    if found:
                        cols_to_plot.append(found[0])
                
                if cols_to_plot and "epoch" in epoch_df.columns:
                    chart_df = epoch_df.set_index("epoch")[cols_to_plot]
                    st.line_chart(chart_df, height=350)
                else:
                    st.info("Missing phoenix_CER, cnt_CER, or weighted_CER columns in epoch metrics.")
            else:
                st.info("No epoch metrics to plot.")

    with tab2:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.subheader("Iteration CSV Data")
            if not iter_df.empty:
                st.dataframe(iter_df, use_container_width=True)
            else:
                st.info("No iteration data loaded.")
        with col_t2:
            st.subheader("Epoch CSV Data")
            if not epoch_df.empty:
                st.dataframe(epoch_df, use_container_width=True)
            else:
                st.info("No epoch data loaded.")

    with tab3:
        st.subheader("Configuration & Directories")
        st.markdown(f"""
        - **Dashboard Script Location**: `scripts/metrics_dashboard.py`
        - **Runs Base Directory**: `training_data/`
        - **Auto-Refresh Status**: `{"Enabled" if auto_refresh else "Disabled"}` (Interval: `{refresh_interval}s`)
        - **Last Updated (Wall Time)**: `{time.strftime('%Y-%m-%d %H:%M:%S')}`
        """)

# Render content inside fragment
render_dashboard_content(selected_run_name, demo_mode)
