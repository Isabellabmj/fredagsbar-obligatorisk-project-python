import streamlit as st
import httpx

API_URL = "http://127.0.0.1:5000"

st.title("🍻 Fredagsbarens event-system")
st.subheader("Kommende events")

try:
    # Hent alle events fra Flask API'en
    response = httpx.get(f"{API_URL}/events", timeout=5.0)
    response.raise_for_status()

    events = response.json()

    # Gennemgå alle events
    for event in events:
        st.write(f"**{event['title']}**")
        st.write(f"Dato: {event['date']}")

        # Beregn antal ledige pladser
        ledige_pladser = event["capacity"] - len(event["participants"])
        st.write(f"Ledige pladser: {ledige_pladser}")

        # Felt til deltagerens navn
        name = st.text_input(
            "Dit navn",
            key=f"name_{event['id']}"
        )

        # Tilmeldingsknap
        if st.button("Tilmeld", key=f"signup_{event['id']}"):

            if not name.strip():
                st.warning("Du skal indtaste dit navn.")

            else:
                try:
                    # Send tilmelding til Flask API'en
                    response = httpx.post(
                        f"{API_URL}/events/{event['id']}/signups",
                        json={"name": name.strip()},
                        timeout=5.0
                    )

                    response.raise_for_status()

                    st.success("Du er nu tilmeldt!")
                    st.rerun()

                except httpx.HTTPStatusError:
                    st.error(
                        response.json().get(
                            "error",
                            "Tilmelding mislykkedes."
                        )
                    )

                except httpx.RequestError:
                    st.error("Kunne ikke forbinde til Flask API'en.")

        st.divider()

except httpx.RequestError:
    st.error("Kunne ikke forbinde til Flask API'en.")

except httpx.HTTPStatusError:
    st.error("Flask API'en returnerede en fejl.")