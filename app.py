from dotenv import load_dotenv
import os
from openai import OpenAI
import streamlit as st
import time
import asyncio

load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=API_KEY)

# thread id를 하나로 관리하기 위함
if 'thread_id' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

thread_id = st.session_state.thread_id
assistant_id = "asst_RxzT6x7PnlMn4i4NfY4O5SfL"

thread_messages = client.beta.threads.messages.list(thread_id, order="asc")

st.header("진우스님 AI")

for msg in thread_messages.data:
    with st.chat_message(msg.role):
        st.write(msg.content[0].text.value)

prompt = st.chat_input("물어보고 싶은 것을 입력하세요")
if prompt:
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )
    with st.chat_message(message.role):
        st.write(message.content[0].text.value)
    
    async def check_run_status(run_id, thread_id):
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        while run.status not in ["completed", "failed"]:
            await asyncio.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
        return run
    
    with st.spinner('응답을 기다리는 중...'):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        run = loop.run_until_complete(check_run_status(run.id, thread_id))
        
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    with st.chat_message(messages.data[0].role):
        st.write(messages.data[0].content[0].text.value)

