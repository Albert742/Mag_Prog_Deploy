import streamlit as st
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

def get_remote_ip() -> str:
    """Get remote ip."""
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None

    return session_info.request.remote_ip

st.title("Test ip getter")
client_ip = get_remote_ip()
if client_ip:
    st.markdown(f"The remote IP is {client_ip}")
else:
    st.markdown("Unable to retrieve the remote IP.")