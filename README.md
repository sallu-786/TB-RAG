### This is a basic chatbot Application that uses Azure OpenAI API to access ChatGPT 3.5 turbo model, Streamlit for Web UI and Langchain to handle the whole process.
If you want to use it first clone the repository to your desktop
1. Run the following command to create a virtual environment--->python -m venv myenv 
2. To activate this environment in windows, go to the command prompt and change directory to folder where you have the code then use this command--->myenv\Scripts\activate
3. Now run the command---> pip install -r requirements.txt
4. Now create .env in your folder file and copy these two line below and then save it
   
      AZURE_OPENAI_ENDPOINT= #your enpoint url from azure portal here
   
      AZURE_OPENAI_API_KEY=  #Azure OpenAI api key 
6. Thats it.! now run the following command to run the code------>streamlit run chat.py

Feel free to use this code but please give due credits..Thanks

email: sulemanmuhammad08@gmail.com
