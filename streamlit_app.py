import streamlit as st
from google import genai
from google.genai import types

# ページのタイトルと説明
st.title("💬 Gemini Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini model to generate responses. "
    "To use this app, you need to provide a Gemini API key."
)

# APIキーの取得（st.secrets または 画面入力）
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.text_input("Gemini API Key", type="password")

if not api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
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

        # 5. これまでの履歴を Gemini の形式に変換
        chat_history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            chat_history.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=m["content"])]
                )
            )

        # 6. チャットセッションの作成とメッセージ送信（モデルを gemini-3.8-flash に指定）
        try:
            chat = client.chats.create(
                model="gemini-3.8-flash",
                history=chat_history
            )

            with st.chat_message("assistant"):
                with st.spinner("考えています..."):
                    response = chat.send_message(prompt)
                    answer = response.text
                    st.markdown(answer)

            # アシスタントの返答を履歴に追加
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
