import os
import json
import yagmail
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Optional

# ============================================
# ✅ STEP 1: Load Environment Variables
# ============================================
load_dotenv()

# ============================================
# ✅ STEP 2: Get Email Credentials
# ============================================
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Email client setup
yag_client = None

def setup_email_client():
    """Initialize Yagmail client with proper error handling"""
    global yag_client
    try:
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            st.error("❌ EMAIL_ADDRESS ya EMAIL_PASSWORD .env mein missing hai!")
            return False
        
        yag_client = yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD)
        st.success("✅ Email client ready!")
        return True
    except Exception as e:
        st.error(f"❌ Email setup error: {str(e)}")
        return False

# ============================================
# ✅ STEP 3: Initialize LLM (Google Gemini)
# ============================================
def get_llm():
    """Initialize and return the LLM"""
    if not GOOGLE_API_KEY:
        st.error("❌ GOOGLE_API_KEY .env mein missing hai!")
        return None
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            max_tokens=2000,
        )
        return llm
    except Exception as e:
        st.error(f"❌ LLM error: {str(e)}")
        return None

# ============================================
# ✅ STEP 4: EMAIL FUNCTIONS
# ============================================

def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Send email using Yagmail
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
    
    Returns:
        dict with status and message
    """
    if not yag_client:
        return {
            "status": "error",
            "message": "❌ Email client not initialized. Setup email first!"
        }
    
    try:
        yag_client.send(
            to=to_email,
            subject=subject,
            contents=body
        )
        return {
            "status": "success",
            "message": f"✅ Email sent successfully to {to_email}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Failed to send email: {str(e)}"
        }

# ============================================
# ✅ STEP 5: AI EMAIL REPLY GENERATION
# ============================================

def generate_email_reply(original_email: str, llm) -> str:
    """
    Generate professional email reply using AI
    
    Args:
        original_email: The original email text
        llm: Language model instance
    
    Returns:
        Generated reply text
    """
    if not llm:
        return "❌ LLM not available"
    
    try:
        reply_prompt = PromptTemplate(
            input_variables=["email_content"],
            template="""
Aap ek professional email agent ho. Neeche di gayi email ke liye ek helpful aur polite reply likho.

Original Email:
{email_content}

Reply Requirements:
- Hindi/English mix ke saath professional
- Concise aur clear
- Helpful aur actionable
- 100-150 words mein

Your Reply:
"""
        )
        
        chain = LLMChain(llm=llm, prompt=reply_prompt)
        response = chain.run(email_content=original_email)
        return response.strip()
    except Exception as e:
        return f"❌ Reply generation error: {str(e)}"

# ============================================
# ✅ STEP 6: AI EMAIL COMPOSER
# ============================================

def compose_email(user_request: str, recipient: str, llm) -> str:
    """
    Compose professional email based on user request
    
    Args:
        user_request: What user wants to say
        recipient: Recipient email
        llm: Language model instance
    
    Returns:
        Composed email text
    """
    if not llm:
        return "❌ LLM not available"
    
    try:
        compose_prompt = PromptTemplate(
            input_variables=["request", "recipient"],
            template="""
Aap ek professional email composer ho. User ki request ke base par {recipient} ko ek professional email likho.

User ki Request:
{request}

Email likho jo:
- Professional aur polite ho
- Clear message convey kare
- To: {recipient}
- Subject aur Body dono likho

Format:
Subject: [subject line]
Body: [email body]
"""
        )
        
        chain = LLMChain(llm=llm, prompt=compose_prompt)
        response = chain.run(request=user_request, recipient=recipient)
        return response.strip()
    except Exception as e:
        return f"❌ Compose error: {str(e)}"

# ============================================
# ✅ STEP 7: STREAMLIT UI
# ============================================

def main():
    # Page config
    st.set_page_config(
        page_title="🤖 AI Email Agent",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("🤖 AI Email Agent")
    st.markdown("**AI-powered Email Composer aur Reply Generator**")
    
    # ==================
    # Sidebar Settings
    # ==================
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Email setup
        if st.button("🔧 Setup Email Client", key="setup_btn"):
            setup_email_client()
        
        st.divider()
        
        # Check credentials
        if st.checkbox("Show Credentials Status"):
            st.write("📧 Email Address:", "✅ Set" if EMAIL_ADDRESS else "❌ Missing")
            st.write("🔐 Email Password:", "✅ Set" if EMAIL_PASSWORD else "❌ Missing")
            st.write("🔑 Google API Key:", "✅ Set" if GOOGLE_API_KEY else "❌ Missing")
    
    # ==================
    # Main Content
    # ==================
    llm = get_llm()
    
    # Initialize email client
    if yag_client is None and EMAIL_ADDRESS and EMAIL_PASSWORD:
        setup_email_client()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📝 Compose Email",
        "💬 Reply to Email",
        "📧 Send Email"
    ])
    
    # ==================
    # TAB 1: Compose Email
    # ==================
    with tab1:
        st.subheader("📝 AI se Email Compose Karo")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            email_request = st.text_area(
                "Kya kehna chahte ho? (Apna message likho)",
                placeholder="Ek meeting schedule karna hai, project update dena hai, etc.",
                height=150,
                key="compose_request"
            )
        
        with col2:
            recipient_email = st.text_input(
                "📧 Recipient Email",
                placeholder="recipient@example.com",
                key="compose_recipient"
            )
        
        if st.button("✨ Generate Email", key="generate_compose"):
            if email_request and recipient_email:
                with st.spinner("⏳ Email banaya ja raha hai..."):
                    composed = compose_email(email_request, recipient_email, llm)
                    st.success("✅ Email ready!")
                    st.text_area("Generated Email:", composed, height=250, disabled=True)
                    
                    # Copy button
                    st.code(composed, language="text")
            else:
                st.warning("⚠️ Request aur Recipient dono likho!")
    
    # ==================
    # TAB 2: Reply to Email
    # ==================
    with tab2:
        st.subheader("💬 Email ka Reply Likho")
        
        original_email = st.text_area(
            "Original Email (jinhe reply dena hai)",
            placeholder="Original email yahan paste karo...",
            height=200,
            key="reply_original"
        )
        
        if st.button("✨ Generate Reply", key="generate_reply"):
            if original_email:
                with st.spinner("⏳ Reply banaya ja raha hai..."):
                    reply = generate_email_reply(original_email, llm)
                    st.success("✅ Reply ready!")
                    st.text_area("Generated Reply:", reply, height=250, disabled=True)
                    st.code(reply, language="text")
            else:
                st.warning("⚠️ Original email likho!")
    
    # ==================
    # TAB 3: Send Email
    # ==================
    with tab3:
        st.subheader("📧 Email Bhejo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            send_to = st.text_input(
                "To: Email Address",
                key="send_to"
            )
            send_subject = st.text_input(
                "Subject:",
                key="send_subject"
            )
        
        with col2:
            st.empty()
        
        send_body = st.text_area(
            "Body:",
            height=200,
            key="send_body"
        )
        
        if st.button("🚀 Send Email Now!", key="send_btn"):
            if send_to and send_subject and send_body:
                with st.spinner("📬 Email bheja ja raha hai..."):
                    result = send_email(send_to, send_subject, send_body)
                    
                    if result["status"] == "success":
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
            else:
                st.warning("⚠️ Sab fields fill karo!")
    
    # ==================
    # Footer
    # ==================
    st.divider()
    st.markdown("""
    ### 📋 Features:
    - ✉️ AI se professional emails compose karo
    - 💬 Original emails ka intelligent reply likho
    - 📧 Directly emails bhejo
    - 🤖 Google Gemini AI powered
    - 🔒 Secure credential management
    
    **Made with ❤️ using LangChain, Streamlit, and Google Gemini**
    """)

# ============================================
# ✅ RUN APPLICATION
# ============================================

if __name__ == "__main__":
    main()
