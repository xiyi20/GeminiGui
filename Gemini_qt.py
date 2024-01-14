import google.generativeai as genai
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class Gemini:
    genai.configure(api_key="AIzaSyCYbTJdgdMy5ETlRFPAcpQozMrnYLp5g0w",transport='rest')
    # Set up the model
    generation_config = {
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
    model=genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)
    chat=model.start_chat(history=[])
    def get_content(self,question):
        response=self.chat.send_message(question+'请用简体中文回答')
        return response

class Window:
    def __init__(self):
        self.app=QApplication([])
        windows=self.windows=QMainWindow()
        windows.setWindowIcon(QIcon('git/GeminiGui/gemini.ico'))
        windows.setWindowTitle('Gemini')
        windows.resize(500,400)
        center=QWidget(windows)
        layout=QVBoxLayout(center)

        p1=QFrame()
        p1.setLayout(QVBoxLayout())
        p1.setFixedSize(500,100)
        # p1.setStyleSheet('background-color:gray')
        l1=QLabel(p1,text='Gemini')
        l1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t1=QLineEdit(p1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        t1.resize(500,20)
        p1.layout().addWidget(l1)
        p1.layout().addWidget(t1)
        layout.addWidget(p1)
        layout.addStretch(1)

        windows.setCentralWidget(center)
        
    def run(self):
        self.windows.show()
        self.app.exec()

Window().run()