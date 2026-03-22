"""
Wersja testowa app_1.py z przykładowymi danymi wbudowanymi w kod.
Uruchom: streamlit run app_test.py
"""
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Panel obozu tenisowego",
    page_icon="🎾",
    layout="wide",
)

st.title("🎾 Marcowa Turcja 2026")
st.caption("Wersja TESTOWA — dane przykładowe (bez Google Sheets)")

# ---------- PRZYKŁADOWE DANE ----------
participants = pd.DataFrame([
    {"name": "Anna Kowalska",  "active": "TRUE"},
    {"name": "Bartek Nowak",   "active": "TRUE"},
    {"name": "Celina Wiśniewska", "active": "TRUE"},
    {"name": "Dawid Zając",    "active": "FALSE"},  # nieaktywny – nie pojawi się
])

days = pd.DataFrame([
    {"id": "1", "title": "Niedziela 22.03", "subtitle": "Dzień przyjazdu i pierwsze zajęcia"},
    {"id": "2", "title": "Poniedziałek 23.03", "subtitle": "Pełny dzień treningów"},
    {"id": "3", "title": "Wtorek 24.03", "subtitle": "Turniej wewnętrzny"},
])

schedule = pd.DataFrame([
    {"day_id": "1", "order": 1, "text": "09:00 – Przyjazd i zakwaterowanie"},
    {"day_id": "1", "order": 2, "text": "11:00 – Rozgrzewka na korcie"},
    {"day_id": "1", "order": 3, "text": "19:00 – Kolacja powitalna"},
    {"day_id": "2", "order": 1, "text": "08:00 – Poranna rozgrzewka"},
    {"day_id": "2", "order": 2, "text": "09:00 – Trening z trenerem (2h)"},
    {"day_id": "2", "order": 3, "text": "17:00 – Sparingi"},
    {"day_id": "3", "order": 1, "text": "09:00 – Losowanie par turniejowych"},
    {"day_id": "3", "order": 2, "text": "10:00 – Turniej (faza grupowa)"},
    {"day_id": "3", "order": 3, "text": "16:00 – Finały i dekoracja"},
])

events = pd.DataFrame([
    {"day_id": "3", "label": "🏆 Turniej wewnętrzny – wszyscy uczestnicy"},
    {"day_id": "1", "label": "🍽️ Kolacja powitalna o 19:00"},
])

personal_plans = pd.DataFrame([
    {"participant_name": "Anna Kowalska",     "day_id": "1", "time": "11:00", "court": "Kort 1", "with_players": "Bartek Nowak",      "event_labels": ""},
    {"participant_name": "Anna Kowalska",     "day_id": "2", "time": "09:00", "court": "Kort 2", "with_players": "Celina Wiśniewska", "event_labels": "Trening z trenerem"},
    {"participant_name": "Anna Kowalska",     "day_id": "3", "time": "10:00", "court": "Kort 3", "with_players": "Bartek Nowak",      "event_labels": "Turniej – Grupa A"},
    {"participant_name": "Bartek Nowak",      "day_id": "1", "time": "11:00", "court": "Kort 1", "with_players": "Anna Kowalska",     "event_labels": ""},
    {"participant_name": "Bartek Nowak",      "day_id": "2", "time": "09:00", "court": "Kort 4", "with_players": "",                  "event_labels": "Trening z trenerem"},
    {"participant_name": "Celina Wiśniewska", "day_id": "2", "time": "09:00", "court": "Kort 2", "with_players": "Anna Kowalska",     "event_labels": "Trening z trenerem"},
])

# ---------- PRZETWARZANIE (identyczne jak w app_1.py) ----------
def safe_str(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()

participants = participants[participants["active"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
participants = participants.sort_values("name")
days["id"] = days["id"].astype(str)
schedule["day_id"] = schedule["day_id"].astype(str)
schedule["order"] = pd.to_numeric(schedule["order"], errors="coerce").fillna(9999)
events["day_id"] = events["day_id"].astype(str)
personal_plans["day_id"] = personal_plans["day_id"].astype(str)

# ---------- SIDEBAR ----------
st.sidebar.header("Ustawienia")
participant_names = participants["name"].tolist()
selected_participant = st.sidebar.selectbox("Wybierz uczestnika", participant_names)
view_mode = st.sidebar.radio("Widok", ["Cały obóz", "Na dziś"])
today_day_id = "1"  # na potrzeby testu: dzień 1 = "dzisiaj"

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
            event_labels = safe_str(row["event_labels"])

            st.success(f"{time_val} | {court_val}")
            if with_players:
                st.write(f"**Z kim:** {with_players}")
            if event_labels:
                st.write(f"**Zapisany na:** {event_labels}")

    st.divider()
