# chatbot.py
# A simple chatbot with fun features + logging

from datetime import datetime
import random

LOG_FILE = "chat_log.txt"


def log(message: str) -> None:
    """Save each message in a file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


print("Bot: Hi! I'm PyChat 🤖")
print("Bot: Type 'bye' to exit. Type '/help' to see commands.\n")

log("=== New chat started at " + datetime.now().isoformat() + " ===")

user_name = None  # will remember your name once you tell it

while True:
    user = input("You: ").strip()
    log("You: " + user)

    if user.lower() in ("bye", "exit", "quit"):
        reply = "Bye! It was nice talking to you 👋"
        print("Bot:", reply)
        log("Bot: " + reply)
        break

    # --- commands start with / ---
    if user.startswith("/"):
        if user == "/help":
            reply = (
                "Commands:\n"
                "  /help  - show this message\n"
                "  /time  - show current time\n"
                "  /joke  - tell a joke\n"
                "  /about - about this bot\n"
                "  /log   - tell where chat is saved"
            )
        elif user == "/time":
            now = datetime.now().strftime("%H:%M")
            reply = f"Current time is {now} ⏰"
        elif user == "/joke":
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
                "There are 10 types of people in the world: those who understand binary and those who don't.",
                "I told my computer I needed a break, and it said 'No problem, I’ll go to sleep.' 😴",
            ]
            reply = random.choice(jokes)
        elif user == "/about":
            reply = "I'm PyChat, a small Python chatbot made by anshul😄"
        elif user == "/log":
            reply = f"I save our chat in the file '{LOG_FILE}' in this folder."
        else:
            reply = "Unknown command. Type /help to see options."

        print("Bot:", reply)
        log("Bot: " + reply)
        continue

    # --- ask & remember user's name ---
    if user_name is None and "name" in user.lower():
        reply = " What should I call you?"
        print("Bot:", reply)
        log("Bot: " + reply)

        user_name = input("You: ").strip()
        log("You: " + user_name)

        reply = f"Nice to meet you, {user_name}! 💫"
        print("Bot:", reply)
        log("Bot: " + reply)
        continue

    # --- simple mood detection ---
    text = user.lower()
    if any(word in text for word in ["sad", "upset", "not good"]):
        reply = "I'm sorry you're feeling that way. Want to talk about it? 🫂"
    elif any(word in text for word in ["happy", "great", "awesome"]):
        reply = "Yay! I'm glad you're feeling good 😄"

    # --- personalized "how are you" ---
    elif "how are you" in text:
        if user_name:
            reply = f"I'm just code, {user_name}, but I'm running perfectly! 😎"
        else:
            reply = "I'm just code, but I'm working perfectly! 😎"

    # --- greetings ---
    elif "hello" in text or "hi" in text:
        if user_name:
            reply = f"Hello {user_name}! How are you today?"
        else:
            reply = "Hello! What's your name?"

    # --- study / college chat ---
    elif "college" in text or "study" in text:
        reply = "Keep learning consistently and you'll be ahead of 90% people 🚀"

    else:
        reply = "I don't fully understand that yet, but I'm learning. Try using /help 🙂"

    print("Bot:", reply)
    log("Bot: " + reply)