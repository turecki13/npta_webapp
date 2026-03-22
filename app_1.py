import streamlit as st
import pandas as pd
from datetime import date


st.set_page_config(
    page_title="Panel obozu tenisowego",
    page_icon="🎾",
    layout="wide",
)

st.title("🎾 Marcowa Turcja 2026")
st.caption("MVP panelu uczestnika — dane z Google Sheets")


# ---------- KONFIGURACJA ----------
SHEET_ID = "TU_WKLEJ_ID_ARKUSZA"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="


# ---------- POMOCNICZE ----------
@st.cache_data(ttl=60)
def load_sheet(sheet_name: str) -> pd.DataFrame:
    url = BASE_URL + sheet_name
    return pd.read_csv(url)


def safe_str(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


# ---------- DANE ----------
participants = load_sheet("participants")
days = load_sheet("days")
schedule = load_sheet("schedule")
events = load_sheet("events")
personal_plans = load_sheet("personal_plans")

participants = participants[participants["active"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
participants = participants.sort_values("name")

days = days.copy()
days["id"] = days["id"].astype(str)

schedule = schedule.copy()
schedule["day_id"] = schedule["day_id"].astype(str)
schedule["order"] = pd.to_numeric(schedule["order"], errors="coerce").fillna(9999)

events = events.copy()
events["day_id"] = events["day_id"].astype(str)

personal_plans = personal_plans.copy()
personal_plans["day_id"] = personal_plans["day_id"].astype(str)

# ---------- SIDEBAR ----------
st.sidebar.header("Ustawienia")

participant_names = participants["name"].tolist()
selected_participant = st.sidebar.selectbox("Wybierz uczestnika", participant_names)

view_mode = st.sidebar.radio("Widok", ["Cały obóz", "Na dziś"])

# MVP: "Na dziś" = pierwszy dzień z arkusza.
# Potem możemy to zmienić na automatyczne mapowanie po bieżącej dacie.
today_day_id = days.iloc[0]["id"] if not days.empty else None

# ---------- GŁÓWNY WIDOK ----------
for _, day in days.iterrows():
    day_id = safe_str(day["id"])
    day_title = safe_str(day["title"])
    day_subtitle = safe_str(day["subtitle"])

    if view_mode == "Na dziś" and day_id != today_day_id:
        continue

    st.markdown(f"## {day_title}")
    if day_subtitle:
        st.write(day_subtitle)

    day_events = events[events["day_id"] == day_id]
    if not day_events.empty:
        st.markdown("### Wydarzenia specjalne")
        for _, ev in day_events.iterrows():
            st.info(f"🏆 {safe_str(ev['label'])}")

    day_schedule = schedule[schedule["day_id"] == day_id].sort_values("order")
    if not day_schedule.empty:
        st.markdown("### Plan dnia")
        for _, row in day_schedule.iterrows():
            st.write(f"• {safe_str(row['text'])}")

    st.markdown("### Twój plan")
    personal_for_day = personal_plans[
        (personal_plans["participant_name"] == selected_participant)
        & (personal_plans["day_id"] == day_id)
    ]

    if personal_for_day.empty:
        st.write("Brak zaplanowanych zajęć.")
    else:
        for _, row in personal_for_day.iterrows():
            time_val = safe_str(row["time"])
            court_val = safe_str(row["court"])
            with_players = safe_str(row["with_players"])
            with_coach = safe_str(row["with_coach"])
            event_labels = safe_str(row["event_labels"])

            st.success(f"{time_val} | {court_val}")
            if with_players:
                st.write(f"**Z kim:** {with_players}")
            if with_coach:
                st.write(f"**Trener:** {with_coach}")
            if event_labels:
                st.write(f"**Zapisany na:** {event_labels}")

    st.divider()