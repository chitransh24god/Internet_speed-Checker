import time
from datetime import datetime
import sys

import streamlit as st


st.set_page_config(page_title="Internet Speed Checker", page_icon="🚀", layout="centered")

st.title("🚀 Internet Speed Checker")
st.caption("Run a quick test for ping, download speed, and upload speed.")

try:
    import speedtest
except ModuleNotFoundError:
    st.error("Missing dependency: `speedtest-cli` is not installed in this Python environment.")
    st.code("python -m pip install --user speedtest-cli", language="bash")
    st.info("Then restart with: `python -m streamlit run app.py`")
    st.caption(f"Current Python interpreter: `{sys.executable}`")
    st.stop()


def run_speed_test() -> dict:
    """Run network speed checks and return rounded metrics."""
    tester = speedtest.Speedtest(secure=True)

    # Discover nearby servers and select the best candidate.
    tester.get_servers()
    best_server = tester.get_best_server()

    ping_ms = best_server.get("latency", 0.0)

    # speedtest returns bits/second; convert to megabits/second.
    download_mbps = tester.download(threads=4) / 1_000_000
    upload_mbps = tester.upload(threads=4) / 1_000_000

    return {
        "ping": round(ping_ms, 2),
        "download": round(download_mbps, 2),
        "upload": round(upload_mbps, 2),
        "server_name": best_server.get("name", "Unknown"),
        "server_country": best_server.get("country", "Unknown"),
        "sponsor": best_server.get("sponsor", "Unknown"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


if "history" not in st.session_state:
    st.session_state.history = []


if st.button("Start Speed Test", type="primary", use_container_width=True):
    with st.spinner("Testing your internet speed... this can take 15-40 seconds."):
        start_time = time.time()
        try:
            result = run_speed_test()
            result["duration_seconds"] = round(time.time() - start_time, 2)
            st.session_state.history.insert(0, result)
            st.success("Speed test completed.")
        except Exception as exc:
            st.error(f"Speed test failed: {exc}")


if st.session_state.history:
    latest = st.session_state.history[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Ping", f"{latest['ping']} ms")
    col2.metric("Download", f"{latest['download']} Mbps")
    col3.metric("Upload", f"{latest['upload']} Mbps")

    st.markdown("---")
    st.subheader("Latest Test Details")
    st.write(f"**Server:** {latest['server_name']} ({latest['server_country']})")
    st.write(f"**Provider:** {latest['sponsor']}")
    st.write(f"**Completed At:** {latest['timestamp']}")
    st.write(f"**Duration:** {latest['duration_seconds']} seconds")

    if len(st.session_state.history) > 1:
        st.markdown("---")
        st.subheader("Previous Results")
        rows = []
        for item in st.session_state.history[1:]:
            rows.append(
                {
                    "Time": item["timestamp"],
                    "Ping (ms)": item["ping"],
                    "Download (Mbps)": item["download"],
                    "Upload (Mbps)": item["upload"],
                    "Server": f"{item['server_name']} ({item['server_country']})",
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.info("Click **Start Speed Test** to begin.")
