from flask import Flask, request

app = Flask(__name__)


events = [
    {
        "id": 1,
        "title": "Quizaften",
        "date": "2026-11-13",
        "capacity": 3,
        "participants": ["Anna", "Bo"]
    },
    {
        "id": 2,
        "title": "Brætspilsaften",
        "date": "2026-11-20",
        "capacity": 5,
        "participants": []
    },
    {
        "id": 3,
        "title": "Beerpong-turnering",
        "date": "2026-11-27",
        "capacity": 4,
        "participants": ["Peter"]
    }
]

@app.get("/events")
def get_events():
    return events, 200


@app.get("/events/<int:id>")
def get_event(id):
    for event in events:
        if event["id"] == id:
            return event, 200

    return {"error": "Eventet findes ikke"}, 404

@app.post("/events")
def create_event():
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    date = data.get("date")
    capacity = data.get("capacity")

    if not title or not date or type(capacity) is not int or capacity <= 0:
        return {"error": "Titel, dato og et positivt heltal for antal pladser er påkrævet"}, 400

    new_event = {
        "id": max(event["id"] for event in events) + 1 if events else 1,
        "title": title,
        "date": date,
        "capacity": capacity,
        "participants": []
    }

    events.append(new_event)

    return new_event, 201

@app.post("/events/<int:id>/signups")
def signup_event(id):
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not name:
        return {"error": "Navn er påkrævet"}, 400

    for event in events:
        if event["id"] == id:

            if name in event["participants"]:
                return {"error": "Personen er allerede tilmeldt"}, 409

            if len(event["participants"]) >= event["capacity"]:
                return {"error": "Eventet er fuldt"}, 409

            event["participants"].append(name)
            return event, 201

    return {"error": "Eventet findes ikke"}, 404

@app.delete("/events/<int:id>/signups/<name>")
def delete_signup(id, name):
    for event in events:
        if event["id"] == id:

            if name not in event["participants"]:
                return {"error": "Personen er ikke tilmeldt"}, 404

            event["participants"].remove(name)
            return "", 204

    return {"error": "Eventet findes ikke"}, 404

@app.delete("/events/<int:id>")
def delete_event(id):
    for event in events:
        if event["id"] == id:
            events.remove(event)
            return "", 204

    return {"error": "Eventet findes ikke"}, 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

