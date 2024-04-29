import streamlit as st
import requests
import re
    
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
    st.header("KMS 🤖")
        
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
            response = requests.post('https://5419-154-57-217-67.ngrok-free.app/question', json={'question': str(prompt)}, headers={'Content-Type': 'application/json'})
            json = response.json()
            last_answer = json["last_answer"]
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