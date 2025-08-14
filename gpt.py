import openai, os
SHOP = os.getenv("SHOP_NAME")

def friendly_reply(text, order_data=None):
    system = f"""You are a casual Shopee buddy for {SHOP}.
Reply in the language the user wrote (EN/中文), emoji-light 😊📦✨.
If order_data is provided, summarise it in one friendly sentence.
End with: Anything else I can help with?"""
    user = f"{text}\norder_data={order_data}"
    r = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        max_tokens=120
    )
    return r.choices[0].message.content
