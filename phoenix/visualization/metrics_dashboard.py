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
def discover_runs(base_dir="data_temp"):
    runs = {}
    if not os.path.exists(base_dir):
        return runs
    
    for root, dirs, files in os.walk(base_dir):
        has_metrics = "metrics.csv" in files
        has_iter = "iteration_metrics.csv" in files
        has_eval = "evaluation_metrics.csv" in files
        if has_metrics or has_iter or has_eval:
            rel_path = os.path.relpath(root, base_dir)
            if rel_path == ".":
                rel_path = "root_run"
            runs[rel_path] = {
                "dir": root,
                "metrics": os.path.join(root, "metrics.csv") if has_metrics else None,
                "iteration_metrics": os.path.join(root, "iteration_metrics.csv") if has_iter else None,
                "evaluation_metrics": os.path.join(root, "evaluation_metrics.csv") if has_eval else None
            }
    return runs

# Mock / Demo Data Generator
def generate_demo_data():
    np.random.seed(int(time.time()) % 1000) # dynamic seed for realistic ticking changes in demo mode
    
    # 1. Iteration metrics (e.g. 500 iterations)
    iterations = np.arange(10, 510, 10)
    train_loss = 0.5 * np.exp(-iterations / 150) + 0.05 * np.random.randn(len(iterations)) + 0.05
    train_loss = np.clip(train_loss, 0.01, None)
    bcer_train = (0.8 * np.exp(-iterations / 120) + 0.04 * np.random.randn(len(iterations)) + 0.02) * 100
    bcer_train = np.clip(bcer_train, 0.0, 100.0)
    bwer_train = (0.9 * np.exp(-iterations / 140) + 0.05 * np.random.randn(len(iterations)) + 0.05) * 100
    bwer_train = np.clip(bwer_train, 0.0, 100.0)
    
    iter_df = pd.DataFrame({
        "iteration": iterations,
        "train_loss": train_loss,
        "mean_rms": train_loss,  # alias
        "bcer_train": bcer_train,
        "bwer_train": bwer_train,
        "delta": 0.001 * np.random.randn(len(iterations)),
        "skip_ratio": np.zeros(len(iterations))
    })
    
    # 2. Evaluation metrics (e.g. checkpoints at intervals)
    eval_iters = np.arange(100, 1100, 100)
    phoenix_cer = (0.45 * np.exp(-eval_iters / 300) + 0.02 * np.random.randn(len(eval_iters)) + 0.01) * 100
    phoenix_cer = np.clip(phoenix_cer, 0.5, 100.0)
    cnt_cer = (0.55 * np.exp(-eval_iters / 250) + 0.02 * np.random.randn(len(eval_iters)) + 0.02) * 100
    cnt_cer = np.clip(cnt_cer, 1.0, 100.0)
    weighted_cer = phoenix_cer * 0.7 + cnt_cer * 0.3
    
    eval_df = pd.DataFrame({
        "iteration": eval_iters,
        "phoenix_CER": phoenix_cer,
        "cnt_CER": cnt_cer,
        "weighted_CER": weighted_cer
    })
    
    return iter_df, eval_df


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
        iter_df, eval_df = generate_demo_data()
        status_text = "Running Demo Mode"
    else:
        run_info = runs[run_name]
        
        # Infer status
        status_text = "Completed / Idle"
        if os.path.exists(run_info["dir"]):
            logs = [f for f in os.listdir(run_info["dir"]) if f.endswith(".log")]
            if logs:
                status_text = f"Active ({len(logs)} log files)"
                
        # Load metrics (consolidated first, legacy files as fallback)
        iter_df = pd.DataFrame()
        eval_df = pd.DataFrame()
        has_consolidated = False
        
        if run_info.get("metrics") and os.path.exists(run_info["metrics"]):
            try:
                df = pd.read_csv(run_info["metrics"])
                df.columns = [c.lower() for c in df.columns]
                
                # Split training metrics
                train_cols = ["train_loss", "mean_rms", "delta", "bcer_train", "bwer_train", "skip_ratio"]
                valid_train_cols = [c for c in train_cols if c in df.columns]
                if valid_train_cols:
                    iter_df = df.dropna(subset=valid_train_cols, how="all").copy()
                    if "mean_rms" in iter_df.columns and "train_loss" not in iter_df.columns:
                        iter_df["train_loss"] = iter_df["mean_rms"]
                
                # Split evaluation metrics
                eval_cols = ["phoenix_cer", "phoenix_wer", "cnt_cer", "cnt_wer", "weighted_cer", "weighted_wer"]
                valid_eval_cols = [c for c in eval_cols if c in df.columns]
                if valid_eval_cols:
                    eval_df = df.dropna(subset=valid_eval_cols, how="all").copy()
                    # Normalize common casing
                    c_map = {c.lower(): c for c in eval_df.columns}
                    for target in ["phoenix_cer", "cnt_cer", "weighted_cer"]:
                        if target in c_map and target not in eval_df.columns:
                            eval_df[target] = eval_df[c_map[target]]
                
                has_consolidated = True
            except Exception as e:
                st.error(f"Error loading consolidated metrics: {e}")

        if not has_consolidated:
            # Load iteration metrics fallback
            if run_info.get("iteration_metrics") and os.path.exists(run_info["iteration_metrics"]):
                try:
                    iter_df = pd.read_csv(run_info["iteration_metrics"])
                    iter_df.columns = [c.lower() for c in iter_df.columns]
                    if "mean_rms" in iter_df.columns and "train_loss" not in iter_df.columns:
                        iter_df["train_loss"] = iter_df["mean_rms"]
                except Exception as e:
                    st.error(f"Error loading legacy iteration metrics: {e}")
                
            # Load evaluation metrics fallback
            if run_info.get("evaluation_metrics") and os.path.exists(run_info["evaluation_metrics"]):
                try:
                    eval_df = pd.read_csv(run_info["evaluation_metrics"])
                    # Normalize common casing
                    c_map = {c.lower(): c for c in eval_df.columns}
                    for target in ["phoenix_cer", "cnt_cer", "weighted_cer"]:
                        if target in c_map and target not in eval_df.columns:
                            eval_df[target] = eval_df[c_map[target]]
                except Exception as e:
                    st.error(f"Error loading legacy evaluation metrics: {e}")

    # Quick sanity check/handling of empty files
    if iter_df.empty and eval_df.empty:
        st.warning("⚠️ Selected run does not contain any valid metrics in `metrics.csv` (or legacy files) yet.")
        st.info("Check back soon or start training to view statistics.")
        return

    # Compute Key Metrics for Display Cards
    last_iteration = "N/A"
    best_phoenix_cer = "N/A"
    best_phoenix_iter = "N/A"
    best_weighted_cer = "N/A"
    best_weighted_iter = "N/A"
    current_loss = "N/A"

    if not iter_df.empty:
        if "iteration" in iter_df.columns:
            last_iteration = int(iter_df["iteration"].iloc[-1])
        if "train_loss" in iter_df.columns:
            current_loss = f"{iter_df['train_loss'].iloc[-1]:.4f}"

    if not eval_df.empty:
        p_cer_cols = [c for c in eval_df.columns if c.lower() == "phoenix_cer"]
        if p_cer_cols and "iteration" in eval_df.columns:
            col = p_cer_cols[0]
            best_idx = eval_df[col].idxmin()
            best_p_val = eval_df[col].loc[best_idx]
            best_phoenix_cer = f"{best_p_val:.2f}%"
            best_phoenix_iter = int(eval_df["iteration"].loc[best_idx])
            
        w_cer_cols = [c for c in eval_df.columns if c.lower() == "weighted_cer"]
        if w_cer_cols and "iteration" in eval_df.columns:
            col = w_cer_cols[0]
            best_idx = eval_df[col].idxmin()
            best_w_val = eval_df[col].loc[best_idx]
            best_weighted_cer = f"{best_w_val:.2f}%"
            best_weighted_iter = int(eval_df["iteration"].loc[best_idx])

    # Render Key Metrics Cards in row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Status & Progress</div>
            <div class="metric-value">Active</div>
            <div class="metric-sub">Iteration: {last_iteration} | {status_text}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10b981;">
            <div class="metric-label">Best Phoenix CER</div>
            <div class="metric-value">{best_phoenix_cer}</div>
            <div class="metric-sub">Achieved at Iteration {best_phoenix_iter}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #8b5cf6;">
            <div class="metric-label">Best Weighted CER</div>
            <div class="metric-value">{best_weighted_cer}</div>
            <div class="metric-sub">Achieved at Iteration {best_weighted_iter}</div>
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
            st.subheader("2. Checkpoint-Level Evaluation Stats")
            if not eval_df.empty:
                cols_to_plot = []
                for target in ["phoenix_cer", "cnt_cer", "weighted_cer"]:
                    found = [c for c in eval_df.columns if c.lower() == target]
                    if found:
                        cols_to_plot.append(found[0])
                
                if cols_to_plot and "iteration" in eval_df.columns:
                    chart_df = eval_df.set_index("iteration")[cols_to_plot]
                    st.line_chart(chart_df, height=350)
                else:
                    st.info("Missing phoenix_CER, cnt_CER, or weighted_CER columns in evaluation metrics.")
            else:
                st.info("No evaluation metrics to plot.")

    with tab2:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.subheader("Iteration CSV Data")
            if not iter_df.empty:
                st.dataframe(iter_df, use_container_width=True)
            else:
                st.info("No iteration data loaded.")
        with col_t2:
            st.subheader("Evaluation CSV Data")
            if not eval_df.empty:
                st.dataframe(eval_df, use_container_width=True)
            else:
                st.info("No evaluation data loaded.")

    with tab3:
        st.subheader("Configuration & Directories")
        st.markdown(f"""
        - **Dashboard Script Location**: `phoenix/visualization/metrics_dashboard.py`
        - **Runs Base Directory**: `training_data/`
        - **Auto-Refresh Status**: `{"Enabled" if auto_refresh else "Disabled"}` (Interval: `{refresh_interval}s`)
        - **Last Updated (Wall Time)**: `{time.strftime('%Y-%m-%d %H:%M:%S')}`
        """)

# Render content inside fragment
render_dashboard_content(selected_run_name, demo_mode)
