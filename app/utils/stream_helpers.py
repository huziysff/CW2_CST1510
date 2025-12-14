import streamlit as st


def safe_rerun():
    """Safely rerun the Streamlit script.

    Some Streamlit versions may not expose `st.experimental_rerun`. This wrapper
    will attempt to call it, and fall back to nudging the session state and
    stopping the script so the UI can refresh on next interaction.
    """
    try:
        st.experimental_rerun()
    except Exception:
        st.session_state["_refresh"] = st.session_state.get("_refresh", 0) + 1
        st.stop()
