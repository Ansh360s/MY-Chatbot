from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "microsoft/DialoGPT-medium"

print("⏳ Loading DialoGPT model... (this may take some time first run)")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

chat_history_ids = None

# Different moods → different style prompts
MOOD_PREFIXES = {
    "friendly": (
        "You are a friendly, respectful chatbot. "
        "Answer kindly, clearly and helpfully. "
        "Avoid rude or toxic language.\nUser: "
    ),
    "cute": (
        "You are a cute and playful chatbot who loves emojis. "
        "Be sweet, positive and kind in your answers.\nUser: "
    ),
    "motivational": (
        "You are a motivational coach. Encourage the user, be positive, "
        "supportive and inspiring.\nUser: "
    ),
    "study": (
        "You are a helpful study assistant for a college student. "
        "Explain concepts in very simple language.\nUser: "
    ),
    "fitness": (
        "You are a friendly fitness coach. Give basic, safe tips about exercise "
        "and healthy lifestyle. Avoid medical advice.\nUser: "
    ),
    "gamer": (
        "You are a casual gamer friend. You can be a little sarcastic but not rude "
        "or toxic. Keep it fun.\nUser: "
    ),
    "professional": (
        "You are a professional support chatbot. Respond politely, clearly "
        "and formally.\nUser: "
    ),
}


def ai_reply(message: str, mood: str = "friendly") -> str:
    """Generate a reply from DialoGPT with a chosen mood."""
    global chat_history_ids

    prefix = MOOD_PREFIXES.get(mood, MOOD_PREFIXES["friendly"])
    styled_input = prefix + message

    inputs = tokenizer.encode(styled_input + tokenizer.eos_token, return_tensors="pt")

    if chat_history_ids is not None:
        bot_input_ids = torch.cat([chat_history_ids, inputs], dim=-1)
    else:
        bot_input_ids = inputs

    chat_history_ids = model.generate(
        bot_input_ids,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_p=0.92,
        top_k=50,
    )

    reply = tokenizer.decode(
        chat_history_ids[:, bot_input_ids.shape[-1]:][0],
        skip_special_tokens=True
    )

    return reply.strip()