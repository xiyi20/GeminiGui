import markdown
import google.generativeai as genai

class Gemini:
    def __init__(self,model="gemini-pro"):
        from Rwconfig import rwconfig
        genai.configure(api_key=rwconfig.apikey,transport='rest')
        # Set up the model
        generation_config={
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        self.model=genai.GenerativeModel(model_name=model,
                                           generation_config=generation_config,
                                           safety_settings=safety_settings)
        self.chat=self.model.start_chat(history=[])

    def get_content(self,code,question,img=None):
        try:
            if img is None:
                response=self.chat.send_message(question).text
                if code==0:
                    response=markdown.markdown(response)
            else:
                response=self.model.generate_content([question,img]).text
            return response
        except Exception as e:
            return f'{type(e).__name__}:{e}'
            # messagebox.messageSignal.connect(messagebox.showmsg)
            # messagebox.messageSignal.emit(f'{type(e).__name__}:{e}')
