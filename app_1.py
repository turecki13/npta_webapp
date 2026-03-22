import streamlit as st
import pandas as pd
from datetime import date
from urllib.parse import quote_plus


st.set_page_config(
    page_title="Panel obozu tenisowego",
    page_icon="🎾",
    layout="wide",
)

st.title("🎾 Marcowa Turcja 2026")
st.caption("Panel uczestnika — trening grupowy i aktywnosci dodatkowe")


# ---------- KONFIGURACJA ----------
# Tryb 1 (klasyczny): zwykly arkusz po SHEET_ID
SHEET_ID = ""

# Tryb 2 (opublikowany arkusz): URL w formacie .../d/e/<PUB_ID>/pubhtml
PUBLISHED_SHEET_PUB_ID = "2PACX-1vSFbtvf5TVj7B5fbHg26WDo9wjg_6eg4rolROWiZWdFlgb_uLuoYg5JVW_WpouIfw"
PUBLISHED_GID_BY_SHEET = {
    "participants": "657101072",
    "days": "425051877",
    "schedule": "303053933",
    "events": "1300205265",
    "personal_plans": "218479741",
    "Grupa": "1469054443",
    "Americano": "1472473550",
    "Turniej tie breakowy": "638787706",
    "Turniej singlowy": "1136501516",
    "Wycieczki": "245379286",
    "Grupa_wyjatki": "764845859",
}

BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="


# ---------- POMOCNICZE ----------
@st.cache_data(ttl=60)
def load_sheet(sheet_name: str, required: bool = True) -> pd.DataFrame:
    if PUBLISHED_SHEET_PUB_ID:
        gid = PUBLISHED_GID_BY_SHEET.get(sheet_name)
        if not gid:
            if required:
                raise ValueError(f"Brak gid dla arkusza: {sheet_name}")
            return pd.DataFrame()
        url = f"https://docs.google.com/spreadsheets/d/e/{PUBLISHED_SHEET_PUB_ID}/pub?output=csv&gid={gid}"
    else:
        if not SHEET_ID:
            raise ValueError("Ustaw SHEET_ID albo PUBLISHED_SHEET_PUB_ID w sekcji konfiguracji.")
        url = BASE_URL + quote_plus(sheet_name)

    try:
        return pd.read_csv(url)
    except Exception:
        if required:
            raise
        return pd.DataFrame()


def safe_str(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_event_entries(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizuje arkusze wydarzen (Americano/turnieje) do kolumn day_id + participant_name."""
    if df.empty:
        return pd.DataFrame(columns=["day_id", "participant_name"])

    cols = {c.lower().strip(): c for c in df.columns}
    participant_col = cols.get("participant_name") or cols.get("name")
    day_col = cols.get("day_id") or cols.get("id")

    if not participant_col:
        return pd.DataFrame(columns=["day_id", "participant_name"])

    out = pd.DataFrame()
    out["participant_name"] = df[participant_col].astype(str).str.strip()
    if day_col:
        out["day_id"] = df[day_col].astype(str).str.strip()
    else:
        out["day_id"] = ""

    out = out[out["participant_name"] != ""]
    return out


def normalize_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizuje arkusz Grupa do participant_name + group (+ trener i kort)."""
    if df.empty:
        return pd.DataFrame(columns=["participant_name", "group", "trainer", "court", "training_time", "day_id"])

    cols = {c.lower().strip(): c for c in df.columns}
    participant_col = cols.get("participant_name") or cols.get("name")
    group_col = cols.get("group") or cols.get("grupa")
    trainer_col = cols.get("trainer") or cols.get("with_coach") or cols.get("coach") or cols.get("trener")
    court_col = cols.get("court") or cols.get("kort")
    training_time_col = cols.get("training_time") or cols.get("time") or cols.get("godzina")
    day_col = cols.get("day_id") or cols.get("id")

    if not participant_col or not group_col:
        return pd.DataFrame(columns=["participant_name", "group", "trainer", "court", "training_time", "day_id"])

    out = pd.DataFrame()
    out["participant_name"] = df[participant_col].astype(str).str.strip()
    out["group"] = df[group_col].astype(str).str.strip()
    if trainer_col:
        out["trainer"] = df[trainer_col].astype(str).str.strip()
    else:
        out["trainer"] = ""
    if court_col:
        out["court"] = df[court_col].astype(str).str.strip()
    else:
        out["court"] = ""
    if training_time_col:
        out["training_time"] = df[training_time_col].astype(str).str.strip()
    else:
        out["training_time"] = ""
    if day_col:
        out["day_id"] = df[day_col].astype(str).str.strip()
    else:
        out["day_id"] = ""

    out = out[(out["participant_name"] != "") & (out["group"] != "")]
    return out


def normalize_group_overrides(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizuje arkusz Grupa_wyjatki do dziennych wyjatkow grupy."""
    if df.empty:
        return pd.DataFrame(columns=["day_id", "group", "participants", "trainer", "court", "training_time"])

    cols = {c.lower().strip(): c for c in df.columns}
    day_col = cols.get("day_id") or cols.get("id")
    group_col = cols.get("group") or cols.get("grupa")
    participants_col = cols.get("participants") or cols.get("participant_names") or cols.get("members") or cols.get("uczestnicy")
    trainer_col = cols.get("trainer") or cols.get("coach") or cols.get("trener")
    court_col = cols.get("court") or cols.get("kort")
    training_time_col = cols.get("training_time") or cols.get("time") or cols.get("godzina")

    if not day_col:
        return pd.DataFrame(columns=["day_id", "group", "participants", "trainer", "court", "training_time"])

    out = pd.DataFrame()
    out["day_id"] = df[day_col].astype(str).str.strip()
    out["group"] = df[group_col].astype(str).str.strip() if group_col else ""
    out["participants"] = df[participants_col].astype(str).str.strip() if participants_col else ""
    out["trainer"] = df[trainer_col].astype(str).str.strip() if trainer_col else ""
    out["court"] = df[court_col].astype(str).str.strip() if court_col else ""
    out["training_time"] = df[training_time_col].astype(str).str.strip() if training_time_col else ""

    out = out[out["day_id"] != ""]
    return out


def parse_participants(raw: str):
    if not raw:
        return []
    normalized = raw.replace("\n", ",").replace(";", ",").replace("|", ",")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def get_group_context(groups_df: pd.DataFrame, participant_name: str, day_id: str, group_overrides_df: pd.DataFrame):
    """Zwraca kontekst grupy uczestnika z opcjonalnymi wyjatkami dziennymi."""
    if groups_df.empty:
        return "", [], "", "", ""

    my_group_rows = groups_df[groups_df["participant_name"] == participant_name]
    if my_group_rows.empty:
        return "", [], "", "", ""

    group_name = safe_str(my_group_rows.iloc[0]["group"])
    if not group_name:
        return "", [], "", "", ""

    group_trainer = safe_str(my_group_rows.iloc[0]["trainer"]) if "trainer" in my_group_rows.columns else ""
    group_court = safe_str(my_group_rows.iloc[0]["court"]) if "court" in my_group_rows.columns else ""
    group_training_time = safe_str(my_group_rows.iloc[0]["training_time"]) if "training_time" in my_group_rows.columns else ""

    members = groups_df[groups_df["group"] == group_name]
    members_list = sorted(members["participant_name"].dropna().astype(str).str.strip().unique().tolist())

    # Wyjatki dzienne: mozna nadpisac sklad, trenera, kort i godzine.
    if not group_overrides_df.empty:
        day_overrides = group_overrides_df[group_overrides_df["day_id"] == day_id]
        if not day_overrides.empty:
            selected_override = None

            # Priorytet 1: wyjatek, ktory jawnie zawiera uczestnika na ten dzien.
            for _, ov in day_overrides.iterrows():
                ov_members = parse_participants(safe_str(ov["participants"]))
                if ov_members and participant_name in ov_members:
                    selected_override = ov
                    break

            # Priorytet 2: wyjatek dla domyslnej grupy uczestnika.
            if selected_override is None:
                group_match = day_overrides[day_overrides["group"] == group_name]
                if not group_match.empty:
                    selected_override = group_match.iloc[0]

            if selected_override is not None:
                override_group = safe_str(selected_override["group"])
                effective_group = override_group or group_name

                # Domyslne dane dla grupy efektywnej.
                effective_rows = groups_df[groups_df["group"] == effective_group]
                if not effective_rows.empty:
                    default_trainer = safe_str(effective_rows.iloc[0]["trainer"]) if "trainer" in effective_rows.columns else ""
                    default_court = safe_str(effective_rows.iloc[0]["court"]) if "court" in effective_rows.columns else ""
                    default_time = safe_str(effective_rows.iloc[0]["training_time"]) if "training_time" in effective_rows.columns else ""
                    default_members = sorted(effective_rows["participant_name"].dropna().astype(str).str.strip().unique().tolist())
                else:
                    default_trainer, default_court, default_time = group_trainer, group_court, group_training_time
                    default_members = members_list

                override_members = parse_participants(safe_str(selected_override["participants"]))
                members_list = override_members if override_members else default_members

                # Jesli uczestnik nie jest w skladzie na ten dzien, nie pokazujemy treningu grupowego.
                if participant_name not in members_list:
                    return "", [], "", "", ""

                group_name = effective_group
                group_trainer = safe_str(selected_override["trainer"]) or default_trainer
                group_court = safe_str(selected_override["court"]) or default_court
                group_training_time = safe_str(selected_override["training_time"]) or default_time

    return group_name, members_list, group_trainer, group_court, group_training_time


# ---------- DANE ----------
participants = load_sheet("participants")
days = load_sheet("days")
schedule = load_sheet("schedule")
events = load_sheet("events")
personal_plans = load_sheet("personal_plans")
groups_raw = load_sheet("Grupa", required=False)
americano_raw = load_sheet("Americano", required=False)
tiebreak_raw = load_sheet("Turniej tie breakowy", required=False)
singles_raw = load_sheet("Turniej singlowy", required=False)
trips_raw = load_sheet("Wycieczki", required=False)
group_overrides_raw = load_sheet("Grupa_wyjatki", required=False)

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

groups = normalize_groups(groups_raw)
if not groups.empty:
    groups["day_id"] = groups["day_id"].astype(str)

americano = normalize_event_entries(americano_raw)
tiebreak = normalize_event_entries(tiebreak_raw)
singles = normalize_event_entries(singles_raw)
trips = normalize_event_entries(trips_raw)
group_overrides = normalize_group_overrides(group_overrides_raw)

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

    # Dynamiczne wydarzenia z dodatkowych arkuszy (ze statusem zapisu).
    dynamic_statuses = []
    dynamic_sources = [
        ("Americano", americano),
        ("Turniej tie breakowy", tiebreak),
        ("Turniej singlowy", singles),
        ("Wycieczki", trips),
    ]
    for event_name, event_df in dynamic_sources:
        if event_df.empty:
            continue

        # Status pokazujemy tylko w dniu, w ktorym event faktycznie wystepuje.
        specific_day_rows = event_df[event_df["day_id"] != ""]
        if not specific_day_rows.empty:
            event_rows_for_day = specific_day_rows[specific_day_rows["day_id"] == day_id]
            if event_rows_for_day.empty:
                continue
        else:
            # Fallback: gdy arkusz nie ma day_id, traktujemy event jako ogolny.
            event_rows_for_day = event_df

        scoped = event_rows_for_day[event_rows_for_day["participant_name"] == selected_participant]
        is_registered = not scoped.empty
        dynamic_statuses.append((event_name, is_registered))

    if not day_events.empty:
        st.markdown("### Wydarzenia specjalne")
        for _, ev in day_events.iterrows():
            st.info(f"🏆 {safe_str(ev['label'])}")

    if dynamic_statuses:
        st.markdown("### Zapisy na wydarzenia")
        for event_name, is_registered in dynamic_statuses:
            if is_registered:
                st.info(f"🏆 {event_name} - jestes zapisany")
            else:
                st.error(f"❌ {event_name} - nie jestes zapisany")

    # Informacja o grupie i skladzie grupy dla wybranego uczestnika.
    group_name, group_members_list, group_trainer, group_court, group_training_time = get_group_context(
        groups,
        selected_participant,
        day_id,
        group_overrides,
    )
    if group_name:
        members_txt = ", ".join(group_members_list)

        st.markdown("### Grupa treningowa")
        st.success(f"Twoja grupa: {group_name}")
        if group_trainer:
            st.write(f"Trener grupy: {group_trainer}")
        if group_court:
            st.write(f"Kort grupy: {group_court}")
        if group_training_time:
            st.write(f"Godzina treningu grupy: {group_training_time}")
        if members_txt:
            st.write(f"Skład grupy: {members_txt}")

    st.markdown("### Trening grupowy")
    if group_name:
        teammates = [p for p in group_members_list if p != selected_participant]
        st.success(f"{group_training_time or 'Godzina do ustalenia'} | {group_court or 'Kort do ustalenia'}")
        if teammates:
            st.write(f"**Z kim:** {', '.join(teammates)}")
        if group_trainer:
            st.write(f"**Trener:** {group_trainer}")
    else:
        st.write("Brak przypisanej grupy treningowej.")

    day_schedule = schedule[schedule["day_id"] == day_id].sort_values("order")
    if not day_schedule.empty:
        st.markdown("### Plan dnia")
        for _, row in day_schedule.iterrows():
            st.write(f"• {safe_str(row['text'])}")

    st.markdown("### Dodatkowe aktywności")
    personal_for_day = personal_plans[
        (personal_plans["participant_name"] == selected_participant)
        & (personal_plans["day_id"] == day_id)
    ]

    if personal_for_day.empty:
        st.write("Brak dodatkowych aktywności.")
    else:
        for _, row in personal_for_day.iterrows():
            cols = {c.lower().strip(): c for c in personal_for_day.columns}
            label_col = cols.get("event_labels") or cols.get("label") or cols.get("activity") or cols.get("name")
            time_col = cols.get("time")
            note_col = cols.get("note") or cols.get("notes")

            activity_label = safe_str(row[label_col]) if label_col else "Aktywność"
            activity_time = safe_str(row[time_col]) if time_col else ""
            activity_note = safe_str(row[note_col]) if note_col else ""

            if activity_time:
                st.success(f"{activity_time} | {activity_label}")
            else:
                st.success(activity_label)
            if activity_note:
                st.write(f"**Notatka:** {activity_note}")

    st.divider()