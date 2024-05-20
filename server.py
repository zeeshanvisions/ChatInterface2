import streamlit as st
import requests
import re
import tempfile
    
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
    st.toast('We have sent an email along with your query')

def main():
    st.set_page_config("Ask me any thing")
    
    with st.sidebar:
        st.title('Chatbot Params')
        uploaded_file = st.file_uploader("Upload an article", type=("txt", ".doc", ".docx", ".ppt", ".pptx", ".pdf", ".csv", ".xlxs"))
    
        if st.button("Upload"):
            if uploaded_file is not None:
                
                response = requests.post("http://127.0.0.1:5005/v1/upload",  files={"file": uploaded_file.read()})
                st.toast("File uploaded")
                
        st.subheader('Models and parameters')
        selected_model = st.sidebar.selectbox('Choose a chat model', ['Azure Open AI', 'Azure Chat Open AI', 'Azure Mistral Large'], key='selected_model')
        temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
        top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
        max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    
    st.header("Chat Donna 🤖")
        
    if "conservation" not in st.session_state:
        st.session_state.conservation = list()
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        try:
            response = requests.post('https://f792-154-57-217-98.ngrok-free.app/v1/question', json={'question': str(prompt)}, headers={'Content-Type': 'application/json'})
            json = response.json()
            last_answer = json["answer"]
            # last_answer = get_encoded_url_string(stringWithUrl=last_answer)
            st.session_state.messages.append({"role": "assistant", "content": last_answer})
            st.chat_message("assistant").write(last_answer)
        except:
            last_answer = "Server is offline"
            # last_answer = get_encoded_url_string(stringWithUrl=last_answer)
            st.session_state.messages.append({"role": "assistant", "content": last_answer})
            st.chat_message("assistant").write(last_answer)
                
if __name__ == '__main__':
    main()