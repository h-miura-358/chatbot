import streamlit as st
from google import genai
from google.genai import types

# ページのタイトルと説明
st.title("💬 Gemini Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini model to generate responses. "
    "To use this app, you need to provide a Gemini API key, which you can get [Google AI Studio](https://aistudio.google.com/). "
    "You can also store the API key in `./.streamlit/secrets.toml` as `GEMINI_API_KEY`."
)

# APIキーの取得優先順位: 
# 1. st.secrets (Streamlit Cloud等の場合)
# 2. 画面上のテキスト入力
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.text_input("Gemini API Key", type="password")

if not api_key:
    st.info("Please add your Gemini API key to continue (or set it in secrets.toml).", icon="🗝️")
else:
    # 1. Gemini クライアントの初期化
    client = genai.Client(api_key=api_key)

    # 2. セッションステートでチャットメッセージを保持
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 3. 過去のチャットメッセージを表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 4. チャット入力欄
    if prompt := st.chat_input("What is up?"):
        # ユーザーの入力を保存して表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 5. これまでの履歴を Gemini の形式（Contents）に変換してチャットセッションを構築
        # systemロールや過去の履歴を正しく渡すための準備
        chat_history = []
        for m in st.session_state.messages[:-1]: # 最新のpromptを除く履歴
            # Gemini SDKのロール名は 'user' または 'model'
            role = "user" if m["role"] == "user" else "model"
            chat_history.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=m["content"])]
                )
            )

        # チャットセッションを開始
        chat = client.chats.create(
            model="gemini-2.5-flash",
            history=chat_history
        )

        # 6. ストリーミング出力を処理するジェネレータ
        def generate_response():
            response_stream = chat.send_message(prompt, stream=True)
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        # 7. アシスタントの返答をストリーミング表示し、履歴に保存
        with st.chat_message("assistant"):
            response = st.write_stream(generate_response())
            
        st.session_state.messages.append({"role": "assistant", "content": response})
