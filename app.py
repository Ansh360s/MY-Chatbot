from flask import Flask, render_template, request, jsonify
from ai_chatbot import ai_reply
import wikipedia

app = Flask(__name__)

# Simple memory for one user (while server is running)
user_memory = {
    "name": None,
    "awaiting_mood": False,
    "mood": "friendly",
}

MOOD_OPTIONS = {
    "1": ("friendly", "Friendly 😊"),
    "2": ("cute", "Cute 🐣"),
    "3": ("motivational", "Motivational 💪"),
    "4": ("study", "Study Assistant 📚"),
    "5": ("fitness", "Fitness Coach 🏋️"),
    "6": ("gamer", "Gamer 🎮"),
    "7": ("professional", "Professional 👔"),
}


def mood_menu_text() -> str:
    lines = ["Choose a mood number:", ""]
    for key, (_, label) in MOOD_OPTIONS.items():
        lines.append(f"{key} - {label}")
    lines.append("")
    lines.append("Example: type 2 for Cute, 3 for Motivational.")
    return "\n".join(lines)


def wiki_answer(text: str) -> str | None:
    """Try to answer using Wikipedia. Return None if not a wiki question."""
    wikipedia.set_lang("en")
    q = text.lower()

    if q.startswith("wiki "):
        query = q[5:]
    elif q.startswith("wikipedia "):
        query = q[10:]
    else:
        for prefix in ["who is", "what is", "tell me about"]:
            if prefix in q:
                query = q.split(prefix, 1)[1]
                break
        else:
            return None

    query = query.strip(" ?.!")

    if not query:
        return None

    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return (
            "There are many results for that. "
            f"Try being more specific, for example: {e.options[0]}"
        )
    except wikipedia.exceptions.PageError:
        return "I couldn't find anything on Wikipedia for that topic."
    except Exception:
        return "Something went wrong while talking to Wikipedia."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global user_memory

    data = request.get_json()
    user_message = data.get("message", "").strip()
    text = user_message.lower().strip()

    # 0) Handle mood menu choice (if we are waiting for it)
    if user_memory["awaiting_mood"]:
        choice = text
        # allow both number and labels like "cute"
        if choice in MOOD_OPTIONS:
            mood_key, label = MOOD_OPTIONS[choice]
            user_memory["mood"] = mood_key
            user_memory["awaiting_mood"] = False
            reply = f"Okay! I'll talk in **{label}** mood now 😄"
        else:
            # maybe they typed "cute" etc.
            for key, (mood_key, label) in MOOD_OPTIONS.items():
                if mood_key in choice:
                    user_memory["mood"] = mood_key
                    user_memory["awaiting_mood"] = False
                    reply = f"Okay! I'll talk in **{label}** mood now 😄"
                    break
            else:
                reply = (
                    "I didn't understand that mood choice.\n\n"
                    + mood_menu_text()
                )

    # 1) Commands to open mood menu
    elif text in ["bot mood", "/mood", "change mood", "mood"]:
        user_memory["awaiting_mood"] = True
        reply = mood_menu_text()

    # 2) Basic math handling (very simple)
    elif any(op in text for op in ["+", "-", "*", "/"]):
        try:
            answer = eval(text)
            reply = f"The answer is {answer}"
        except Exception:
            reply = "I can't understand that math question."

    # 3) Remember user name
    elif "my name is" in text:
        name = text.split("my name is", 1)[1].strip().title()
        if name:
            user_memory["name"] = name
            reply = f"Nice to meet you, {name}! I'll remember your name 😊"
        else:
            reply = "I didn't catch your name. Try: 'my name is Ansh'."

    elif text.startswith("i am "):
        name = text[5:].strip().title()
        if name:
            user_memory["name"] = name
            reply = f"Got it, {name}! I'll remember you 👍"
        else:
            reply = "I didn't catch your name. Try: 'I am Ansh'."

    # 4) Ask stored name
    elif "what is my name" in text or "what's my name" in text or "do you remember my name" in text:
        if user_memory["name"]:
            reply = f"Of course! Your name is {user_memory['name']} 😄"
        else:
            reply = "I don't know your name yet. Tell me with: 'my name is ...'."

    # 5) Greetings (use memory)
    elif any(word in text for word in ["hi", "hello", "hey"]):
        if user_memory["name"]:
            reply = f"Hello {user_memory['name']}! 👋 How can I help you today?"
        else:
            reply = "Hello! 👋 What's your name?"

    # 6) Wikipedia questions
    else:
        wiki = wiki_answer(text)
        if wiki is not None:
            reply = wiki
        else:
            # 7) Fallback to AI with chosen mood
            reply = ai_reply(user_message, mood=user_memory["mood"])

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)