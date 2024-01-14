import tkinter as tk
import tkinter.colorchooser as colorchooser
import google.generativeai as genai

setting_isopen=False

class gemini:
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

class setting:
    def __init__(self, st, st1, st2, st3, sb1, sb2, sb3):
        # 检查设置窗口是否已经打开
        if setting.window_open:
            return
        setting.window_open=True

        t=self.t=tk.Toplevel()
        t.configure(bg='gray')
        t.title('设置')
        t.geometry('400x400+1450+150')
        t1=self.t1=tk.Button(t,text='主窗口颜色',bg=st.cget('bg'),command=lambda:self.setcolor([st,st1,sb1,sb2,sb3],self.t1,0))
        t1.place(x=70,y=30)
        t2=self.t2=tk.Button(t,text='提问框颜色', bg=st2.cget('bg'),command=lambda:self.setcolor(st2,self.t2,None))
        t2.place(x=160,y=30)
        t3=self.t3=tk.Button(t,text='回答框颜色', bg=st3.cget('bg'),command=lambda:self.setcolor(st3,self.t3,None))
        t3.place(x=250,y=30)
        t4=self.t4=tk.Button(t,text='提问字体颜色',bg=st3.tag_cget('me','foreground'),command=lambda:self.setcolor(st3,self.t4,1))
        t4.place(x=40,y=70)
        t5=self.t5=tk.Button(t,text='回答字体颜色',bg=st3.tag_cget('gemini','foreground'),command=lambda:self.setcolor(st3,self.t5,2))
        t5.place(x=150,y=70)
        t6=self.t6=tk.Button(t,text='输入字体颜色',bg=st3.cget('fg'),command=lambda: self.setcolor(st2,self.t6,3))
        t6.place(x=260,y=70)

    def setcolor(self, s, t, mode):
        color = colorchooser.askcolor()
        if color[1]:
            colored=color[1]
            if mode==0:
                for i in s:
                    i.config(bg=colored)
            elif mode==1:
                s.tag_config('me', foreground=colored)
            elif mode==2:
                s.tag_config('gemini', foreground=colored)
            elif mode==3:
                s.config(fg=colored)
            else:
                s.config(bg=colored)
            t.config(bg=colored)

    def begin(self):
        self.t.mainloop()

    # 添加类属性 window_open 来控制设置窗口只能打开一个
    window_open=False


class window:
    def __init__(self):
        t=self.t=tk.Tk()
        t.attributes('-topmost', True)
        t.title('Gemini AI')
        t.geometry("800x600+600+150")

        t1=self.t1=tk.Label(t,text="Hello",font=('幼园', 25))
        t1.pack()

        t2=self.t2=tk.Text(t)
        t2.place(x=50,y=50,width=700,height=100)

        t3=self.t3=tk.Text(t,state='disabled')
        t3.tag_config('me',foreground='blue')
        t3.tag_config('gemini',foreground='red')
        t3.place(x=50,y=150,width=700,height=400)

        b1=self.b1=tk.Button(t,command=self.answer,text="确认")
        b1.place(x=500,y=0)
        b2=self.b2=tk.Button(t,command=self.clear,text="清空回答")
        b2.place(x=550,y=0)
        b3=self.b3=tk.Button(t,command=self.setting,text="设置")
        b3.place(x=620,y=0)

    def answer(self):
        my_gemini=gemini()
        self.t3.configure(state='normal')
        self.t3.insert('end','\n我: \n'+self.t2.get('1.0', 'end'), 'me')
        self.t3.tag_config('red')
        self.t3.insert('end','\nGemini: \n'+my_gemini.get_content(
        self.t2.get('1.0','end')).text+'\n','gemini')
        self.t3.configure(state='disable')

    def clear(self):
        self.t3.configure(state='normal')
        self.t3.delete('1.0','end')
        self.t3.configure(state='disable')

    def setting(self):
        # 在打开设置窗口之前，检查是否已经打开
        if setting.window_open:
            return
        self.setting_window=setting(self.t, self.t1, self.t2, self.t3, self.b1, self.b2, self.b3).begin()

    def begin(self):
        self.t.mainloop()

window=window().begin()