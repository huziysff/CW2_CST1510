import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.getcwd())

from app.data.db import connect_database
from app.data.datasets import load_datasets_metadata_csv
from app.utils.stream_helpers import safe_rerun

st.markdown(
    """
    <div style="background:linear-gradient(90deg,#1e3a8a,#6366f1);padding:12px;border-radius:8px;color:white;">
        <h2 style="margin:0">📚 Data Science — Governance & Discovery</h2>
        <div style="opacity:0.9">Dataset catalog resource usage, source dependency and archive recommendations</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filters & Actions")
    if st.button("Refresh"):
        safe_rerun()
    st.divider()
    if st.button("Download catalog"):
        conn_dl = connect_database()
        df_dl = pd.read_sql_query("SELECT * FROM datasets_metadata", conn_dl)
        conn_dl.close()
        st.download_button("Download CSV", df_dl.to_csv(index=False), file_name="datasets_metadata.csv")

conn = connect_database()
try:
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", conn)
except Exception:
    df = pd.DataFrame()
conn.close()

st.write(f"Rows in `datasets_metadata` table: **{len(df)}**")
if len(df) == 0:
    st.warning("No datasets found. You can load sample data from CSV below.")

if st.button("Load datasets from CSV (force)"):
    conn2 = connect_database()
    loaded = load_datasets_metadata_csv(conn2, force=True)
    conn2.close()
    st.success(f"Loaded {loaded} dataset rows from CSV")
    safe_rerun()

if df.empty:
    st.stop()

# normalize types
if "file_size_mb" in df.columns:
    df["file_size_mb"] = pd.to_numeric(df["file_size_mb"], errors="coerce").fillna(0.0)
if "record_count" in df.columns:
    df["record_count"] = pd.to_numeric(df["record_count"], errors="coerce").fillna(0)
if "last_updated" in df.columns:
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")

with st.sidebar:
    cats = df["category"].dropna().unique().tolist() if "category" in df.columns else []
    sources = df["source"].dropna().unique().tolist() if "source" in df.columns else []
    cat_sel = st.multiselect("Category", options=cats, default=cats if cats else None, key="ds_cat")
    src_sel = st.multiselect("Source", options=sources, default=sources if sources else None, key="ds_src")

if cat_sel:
    df = df[df["category"].isin(cat_sel)]
if src_sel:
    df = df[df["source"].isin(src_sel)]

# KPIs
total_ds = df.shape[0]
total_rows = int(df["record_count"].sum()) if "record_count" in df.columns else 0
total_size = float(df["file_size_mb"].sum()) if "file_size_mb" in df.columns else 0.0
c1, c2, c3 = st.columns(3)
c1.metric("Total Datasets", total_ds)
c2.metric("Total Rows", f"{total_rows:,}")
c3.metric("Total Size (MB)", f"{total_size:,.1f}")

st.markdown("---")
left, right = st.columns([2, 1])
with left:
    st.subheader("Top datasets by size")
    if "file_size_mb" in df.columns:
        st.bar_chart(df.sort_values("file_size_mb", ascending=False).head(20).set_index("dataset_name")["file_size_mb"])

    st.subheader("Top datasets by row count")
    if "record_count" in df.columns:
        st.bar_chart(df.sort_values("record_count", ascending=False).head(20).set_index("dataset_name")["record_count"])

    st.subheader("Source dependency")
    if "file_size_mb" in df.columns and "source" in df.columns:
        src_group = df.groupby("source")["file_size_mb"].sum().sort_values(ascending=False)
        st.bar_chart(src_group)
        st.write("Top sources by total data size (MB)")
        st.dataframe(src_group.reset_index().rename(columns={"file_size_mb": "total_size_mb"}).head(20), width='stretch')

with right:
    st.subheader("Category distribution")
    if "category" in df.columns:
        st.bar_chart(df["category"].value_counts())
    st.subheader("Sample datasets")
    st.dataframe(df.head(20), width='stretch')

st.markdown("---")
st.subheader("Archive Recommendation Engine")

age_days = st.number_input("Archive if not updated in X days", min_value=30, max_value=3650, value=365)
size_threshold = st.number_input("Size threshold (MB) for archiving candidates", min_value=1, max_value=100000, value=1024)
row_threshold = st.number_input("Row count below which to consider archiving", min_value=0, max_value=100000000, value=1000)

candidates = df.copy()
now = pd.Timestamp.now()
if "last_updated" in candidates.columns:
    candidates["age_days"] = (now - candidates["last_updated"]).dt.days
else:
    candidates["age_days"] = 9999

candidates["size_mb"] = candidates.get("file_size_mb", 0.0)
candidates["rows"] = candidates.get("record_count", 0)

archive_cond = (candidates["age_days"] > age_days) | ((candidates["size_mb"] > size_threshold) & (candidates["rows"] < row_threshold))
arch_candidates = candidates[archive_cond].sort_values(["size_mb", "age_days"], ascending=[False, False])

st.write(f"Found {len(arch_candidates)} archiving candidate(s)")
if not arch_candidates.empty:
    st.dataframe(arch_candidates[["dataset_name", "source", "category", "size_mb", "rows", "age_days"]].head(200), width='stretch')
    st.download_button("Download archive candidates (CSV)", arch_candidates.to_csv(index=False).encode("utf-8"), file_name="archive_candidates.csv")
else:
    st.success("No immediate archive candidates with current thresholds.")

st.markdown("---")
st.subheader("Governance Recommendations")
total_size_mb = df.get("file_size_mb", pd.Series([0.0])).sum()
top_sources = df.groupby("source")["file_size_mb"].sum().sort_values(ascending=False) if "source" in df.columns else pd.Series()
if not top_sources.empty:
    top_source = top_sources.index[0]
    pct = (top_sources.iloc[0] / total_size_mb) * 100 if total_size_mb > 0 else 0
    st.write(f"- Focus governance on source **{top_source}** which accounts for **{pct:.1f}%** of total data size.")

st.write("- Consider archiving datasets not updated within the threshold or large-but-sparse datasets.")
st.write("- Add automated size and usage quotas per source; enforce lifecycle policies for old datasets.")