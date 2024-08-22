import streamlit as st
import requests
import re
import tempfile

BASE_URL = "https://af91-154-57-217-192.ngrok-free.app/v1"

class Reference:
    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url
    
    def to_string(self):
        return f"[{self.title}]({self.url})"
    
def add_log(log: str):
    print(log)
    if st.session_state.logs is None:
        logs = [log]
        st.session_state.logs = logs
    else:
        st.session_state.logs.append(log)
        
def find(stringWithUrl: str):
  url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',stringWithUrl) 
  return url 

def get_encoded_url_string(stringWithUrl: str):
    newString = stringWithUrl
    newString = newString.replace('\n','<br/>')
    urlsFound = find(stringWithUrl=stringWithUrl)
    referenceUrls = list()
    for url in urlsFound:
        referenceUrls.append(f'<a href="{url}">{url}</a>')
    for index, url in enumerate(urlsFound):
        newString = newString.replace(url, referenceUrls[index])
    return newString

def show_negative_case_toast():
    st.toast('We have sent an email along with your queries')
    
def thumbs_up_pressed():
    messages = st.session_state.messages
    last_answer = ""
    last_question = ""
    type = "like"
    session_id = st.session_state.session_id
    for message in messages:
        if message["role"] == "assistant":
            last_answer = message["content"]
        else:
            last_question = message["content"]
    
    body = {'session_id': session_id, 'question': last_question, 'answer': last_answer, 'type': type}
    response = requests.post(f'{BASE_URL}/feedback', json=body, headers={'Content-Type': 'application/json'})

def thumbs_down_pressed():
    print("Thumbs down pressed")
    messages = st.session_state.messages
    last_answer = ""
    last_question = ""
    type = "dislike"
    session_id = st.session_state.session_id
    for message in messages:
        if message["role"] == "assistant":
            last_answer = message["content"]
        else:
            last_question = message["content"]
    
    body = {'session_id': session_id, 'question': last_question, 'answer': last_answer, 'type': type}
    response = requests.post(f'{BASE_URL}/feedback', json=body, headers={'Content-Type': 'application/json'})
    

def main():
    st.set_page_config("Ask me any thing")
    st.markdown(
            """
        <style>
            .st-emotion-cache-1c7y2kd {
                flex-direction: row-reverse;
                text-align: right;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )
    with st.sidebar:
        st.title('Chatbot Params')
        
        if st.button("Show Session Id"):
            st.write(f'Session ID={st.session_state["session_id"]}')
            
        on = st.toggle("Use Context Understanding", value=True)
        if on:
            st.session_state.use_context = True
        else:
            st.session_state.use_context = False
    
        uploaded_file = st.file_uploader("Upload an article", type=("txt", ".doc", ".docx", ".ppt", ".pptx", ".pdf", ".csv", ".xlxs"))
    
        if st.button("Upload"):
            if uploaded_file is not None:
                response = requests.post(f"{BASE_URL}/upload",  files={"file": uploaded_file.read()})
                st.toast("File uploaded")
                
        st.subheader('Models and parameters')
        selected_model = st.sidebar.selectbox('Choose a chat model', ['Azure Open AI GPT 3.5', 'Azure Mistral Large', 'Azure Open AI GPT 4o'], key='selected_model')
        
        if selected_model == 'Azure Mistral Large':
            st.session_state.model = 'azure_mistral_large_chat'
        elif selected_model == 'Azure Open AI GPT 4o':
            st.session_state.model = "azure_open_ai_chat_gpt4o"
        else:
            st.session_state.model = 'azure_open_ai_chat'
        
        st.session_state.temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.3, step=0.01)
        top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
        max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    
    st.header("Donna 🤖")
        
    if "conservation" not in st.session_state:
        st.session_state.conservation = list()
    
    if "model" not in st.session_state:
            st.session_state.model = "azure_open_ai_chat"
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hi, How can I help you?"}]
        
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = None
    
    if "use_context" not in st.session_state:
        st.session_state.use_context = True
        
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.3
    
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        try:
            body = {'question': str(prompt), 'llm_type': st.session_state.model, 'temperature': st.session_state.temperature, 'use_context': st.session_state.use_context}
            if st.session_state.session_id is not None:
                body["session_id"] = st.session_state.session_id
                
            response = requests.post(f'{BASE_URL}/question', json=body, headers={'Content-Type': 'application/json'})
            json = response.json()
            
            response = json["current_response"]
            last_answer = response["content"]
            show_references = response["show_references"]
            # print(json)
            # print(f"===== > Show references: {show_references}")
            references = list()
            references_string = ""
            # For multiple references
            # if show_references == True:
            #     for reference in response["references"]:
            #         references.append(Reference(reference["title"], reference["url"]))
            #     references_string = "\n".join(f"{ref.to_string()}  " for ref in references)
            #     last_answer = last_answer + "\n\n **Sources:** " + references_string
            
            # if response["references"]:
            #     first_reference = response["references"][0]
            #     references.append(Reference(first_reference["title"], first_reference["url"]))
            #     references_string = references[0].to_string()
            #     last_answer = last_answer + "\n\n **Source:** " + references_string
            
            last_answer = last_answer.replace('$', '\$')
            
            st.session_state["session_id"] = json["session_id"]
            st.session_state.messages.append({"role": "assistant", "content": last_answer})
            with st.chat_message("assistant"):
                st.markdown(last_answer)
                col1,col2,col3,col4 = st.columns([3,3,0.5,0.5])
                with col3:
                        st.button(":thumbsup:", on_click=thumbs_up_pressed)
                with col4:
                        st.button(":thumbsdown:", on_click=thumbs_down_pressed)
        except:
            last_answer = "Server is offline"
            # last_answer = get_encoded_url_string(stringWithUrl=last_answer)
            st.session_state.messages.append({"role": "assistant", "content": last_answer})
            st.chat_message("assistant").write(last_answer)
                
if __name__ == '__main__':
    main()
