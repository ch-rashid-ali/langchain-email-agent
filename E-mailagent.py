import os
from dotenv import load_dotenv
import yagmail
import streamlit as st  # <-- YEH LINE ADD KAREIN

# Sabse pehle .env file ko load karein
load_dotenv()

# .env file se password ko khufiya tarike se uthaein
my_password = os.environ.get("EMAIL_PASSWORD")

# Ab yahan asli password ki jagah humne 'my_password' variable use kiya hai
yag = yagmail.SMTP("rashidalim514@gmail.com", my_password)

yag.send(
    to="khan.rashidali4343@gmail.com",
    subject="Test Email",
    contents="Hello, this is sent using Yagmail!"
)

print("Email sent!")

# %%
from langchain.agents import create_agent

from langchain_google_genai import ChatGoogleGenerativeAI

# Pehle environment se key variable mein load karein
gemini_key = os.environ.get("GOOGLE_API_KEY")

# Ab llm ko create karte waqt wo key pass karein
llm = ChatGoogleGenerativeAI(
    api_key=gemini_key,           # Yeh ab automatic .env se key utha lega
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

# %%
def send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Sends email to recipeint, with subject , body."""
    yag.send(
        to="khan.rashidali4343@gmail.com",
        subject="Hello, how are you? test email from langchain",
        contents="hello, this is the body of the email sent using langchain and yagmail!"
    )
    return "Email sent successfully."

# %%
graph = create_agent(
    model=llm,
    tools=[send_email_tool],
    system_prompt="You are a helpful assistant, and you can send emails on behalf of me Rashid Ali as real email.",
)
st.title("AI Email Agent 🤖")

# Browser par user se command lene ke liye text box
user_prompt = st.text_input("Apna Hukam Likhein:", placeholder="e.g., Send mail to khan...")

# Ek button banayein jise dabane par agent chalega
run_button = st.button("Execute Agent")

if run_button:
    if user_prompt:
        st.info("Agent process kar raha hai...")
        
        # Ab input manually dene ki jagah user_prompt variable se jayega
        inputs = {"messages": [{"role": "user", "content": user_prompt}]}
        
        # Loop ke andar st.write lagayein taake output terminal ke bajaye browser par dikhe
        for chunk in graph.stream(inputs, stream_mode="updates"):
            st.write(chunk)
            
        st.success("Kaam Mukammal Ho Gaya!")
    else:
        st.warning("Pehle text box mein koi instruction likhein!")


