
import streamlit as st
import httpx
import os

# Adresse til Flask API'en
API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")

st.title("Fredagsbarens event system")

# Gem brugerens navn mellem klik
if "name" not in st.session_state:
    st.session_state["name"] = ""

name = st.sidebar.text_input("Dit navn", key="name")


# Hent alle events fra API'en
try:
    response = httpx.get(f"{API_URL}/events", timeout=2.0)
    response.raise_for_status()
    events = response.json()

except httpx.TimeoutException:
    st.error("API'en svarer for langsomt.")
    st.stop()

except httpx.ConnectError:
    st.error("Kunne ikke forbinde til Flask API'en.")
    st.stop()

except httpx.RequestError:
    st.error("Der opstod en fejl ved forbindelsen til API'en.")
    st.stop()

except httpx.HTTPStatusError as error:
    st.error(f"API-fejl: {error.response.status_code}")
    st.stop()


# Vis alle events i en tabel
st.subheader("Kommende events")

event_oversigt = []

for event in events:
    event_oversigt.append({
        "Titel": event["title"],
        "Dato": event["date"],
        "Antal tilmeldte": len(event["participants"]),
        "Ledige pladser": event["capacity"] - len(event["participants"])
    })

st.dataframe(event_oversigt, hide_index=True)


# Vælg et event
st.subheader("Tilmelding og afmelding")

if events:
    event_id = st.selectbox(
        "Vælg et event",
        options=[event["id"] for event in events],
        format_func=lambda id: next(
            event["title"] for event in events if event["id"] == id
        )
    )

    # Find det valgte event
    selected_event = None

    for event in events:
        if event["id"] == event_id:
            selected_event = event
            break

    st.write(f"**Dato:** {selected_event['date']}")
    st.write(f"**Deltagere:** {', '.join(str(p) for p in selected_event['participants']) or 'Ingen endnu'}")

    ledige_pladser = selected_event["capacity"] - len(selected_event["participants"])
    st.write(f"**Ledige pladser:** {ledige_pladser}")

    # Tilmeld en deltager
    if st.button("Tilmeld", disabled=ledige_pladser <= 0):

        if not name.strip():
            st.warning("Du skal indtaste dit navn i sidebaren.")

        else:
            try:
                response = httpx.post(
                    f"{API_URL}/events/{event_id}/signups",
                    json={"name": name.strip()},
                    timeout=2.0
                )

                response.raise_for_status()
                st.session_state["message"] = "Du er nu tilmeldt!"
                st.rerun()

            except httpx.HTTPStatusError as error:
                st.error(error.response.json().get("error", "Tilmelding mislykkedes."))

            except httpx.TimeoutException:
                st.error("API'en svarer for langsomt.")

            except httpx.RequestError:
                st.error("Kunne ikke forbinde til API'en.")

    # Afmeld en deltager
    if st.button("Afmeld"):

        if not name.strip():
            st.warning("Du skal indtaste dit navn i sidebaren.")

        else:
            try:
                response = httpx.delete(
                    f"{API_URL}/events/{event_id}/signups/{name.strip()}",
                    timeout=2.0
                )

                response.raise_for_status()
                st.session_state["message"] = "Du er nu afmeldt!"
                st.rerun()

            except httpx.HTTPStatusError as error:
                st.error(error.response.json().get("error", "Afmelding mislykkedes."))

            except httpx.TimeoutException:
                st.error("API'en svarer for langsomt.")

            except httpx.RequestError:
                st.error("Kunne ikke forbinde til API'en.")

else:
    st.info("Der er ingen events endnu.")


# Vis besked efter tilmelding eller afmelding
if "message" in st.session_state:
    st.success(st.session_state.pop("message"))


# Opret et nyt event
st.subheader("Opret nyt event")

with st.form("create_event_form"):
    title = st.text_input("Eventets titel")
    date = st.date_input("Dato")
    capacity = st.number_input("Antal pladser", min_value=1, step=1)

    submitted = st.form_submit_button("Opret event")

    if submitted:
        if not title.strip():
            st.warning("Du skal indtaste en titel.")

        else:
            try:
                response = httpx.post(
                    f"{API_URL}/events",
                    json={
                        "title": title.strip(),
                        "date": date.isoformat(),
                        "capacity": int(capacity)
                    },
                    timeout=2.0
                )

                response.raise_for_status()
                st.session_state["message"] = "Eventet er oprettet!"
                st.rerun()

            except httpx.HTTPStatusError as error:
                st.error(error.response.json().get("error", "Kunne ikke oprette eventet."))

            except httpx.TimeoutException:
                st.error("API'en svarer for langsomt.")

            except httpx.RequestError:
                st.error("Kunne ikke forbinde til API'en.")
