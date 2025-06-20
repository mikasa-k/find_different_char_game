#!/usr/bin/env python3
import os
import tkinter as tk
import wave
import threading
import random
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, 2)
os.close(devnull)
import pyaudio #これだけ外部ライブラリ

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
window_size = {'width':600, 'height':450}
default_style = {'anchor':'w', 'justify':'left'}
ff = 'Corbel'
is_key_enable = True
def abcrand(n):
	r = []
	for i in range(n):
		r.append(ABC[random.randint(0, len(ABC)-1)])
	return "".join(r)
def play_audio(file_path, mlen):
	if os.path.exists(file_path):
		try:
			wf = wave.open(file_path, 'rb')
			p = pyaudio.PyAudio()
			stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=wf.getnchannels(),rate=wf.getframerate(),output=True)
			chunk = 1024
			data = wf.readframes(chunk)
			while data and mlen >= 0:
				stream.write(data)
				data = wf.readframes(chunk)
				mlen -= 0.1
			stream.stop_stream()
			stream.close()
			p.terminate()
			wf.close()
		except:
			pass
class BGMplay:
	def __init__(self):
		self.stop_flag = threading.Event()
		self.bgm_thread = None
	def play_bgm(self, filename, loop=True):
		if os.path.exists(filename):
			try:
				p = pyaudio.PyAudio()
				while not self.stop_flag.is_set():
					wf = wave.open(filename, 'rb')
					stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=wf.getnchannels(),rate=wf.getframerate(),output=True)
					chunk = 1024
					while not self.stop_flag.is_set():
						data = wf.readframes(chunk)
						if not data:
							break
						stream.write(data)
					stream.stop_stream()
					stream.close()
					wf.close()
					if loop == False:
						break
				p.terminate()
			except:
				pass
	def start_bgm(self, filename, loop=True):
		if os.path.exists(filename):
			try:
				if self.bgm_thread and self.bgm_thread.is_alive():
					return
				self.bgm_thread = threading.Thread(target=self.play_bgm, args=(filename, loop), daemon=True)
				self.bgm_thread.start()
			except:
				pass
	def stop_bgm(self):
		try:
			if self.bgm_thread and self.bgm_thread.is_alive():
				self.stop_flag.set()
				self.bgm_thread.join()
		except:
			pass
class Speak:
	def __init__(self, label_name, wrap_len=False, next_btn=False, next_place=False):
		self.label = label_name
		self.next_btn = next_btn
		self.saying = False
		self.next_place = next_place
		self.text = ""
		self.count = 0
		self.speed = 50
		if wrap_len == False:
			self.width = int(window_size["width"] *0.95)
		else:
			self.width = wrap_len
	def say(self, text=False):
		global is_key_enable
		self.saying = True
		is_key_enable = False
		if text != False:
			self.text = text
			if text == "":
				self.label.config(text="")
			elif self.next_btn != False and self.next_place != False:
				self.next_btn.place_forget()
		if self.count < len(self.text):
			self.count += 1
			self.label.config(text=self.text[0:self.count], wraplength=self.width)
			tim = self.speed
			if self.text[self.count -1] == "。":
				tim *= 10
			elif self.text[self.count -1] == "、":
				tim *= 5
			self.label.after(tim, self.say)
		else:
			self.stop_saying()
	def say_all(self):
		self.label.config(text=self.text, wraplength=self.width)
		self.stop_saying()
	def stop_saying(self):
		global is_key_enable
		if self.next_btn != False and self.next_place != False:
			self.next_btn.place(**self.next_place)
		self.saying = False
		is_key_enable = True
		self.count = 0
		self.text = ''
class Stage:
	def __init__(self, root):
		#画面遷移
		self.SID_TITLE = 1
		self.SID_MAIN = 2
		self.SID_END = 3
		self.SID_BACK = 4
		self.bgm = BGMplay()
		self.reset()
		self.id = self.SID_TITLE #タイトル画面で初期化
		self.bg = "#043" #デフォルト背景色
		self.memframe = tk.Frame(root, bg=self.bg)
		self.description_list = (
		"この度ハ、閲覧くださいまシて有難うござイます。\n製作者は、深夜テンションでプログラムしテいて表示がおかしいかモしれませんがご了承下さイッ。",
		"あああああはははははハハハハハハハあｈHAHAHAHAHAHAHAHAHA\nฅ( ̳• ·̫ • ̳ฅ)و 。。。。\nウフフフフフフフっ",
		"手が勝手に！？、、、はぁーはぁー。。。\n注意: シラフです。ネタが思いつかなくて適当にキーボードを打ちました。\n一部の文字化けシているとおもはれる箇所は、全て仕様通りでス。",
		"キーボード操作について:\nEnterキー = 決定\nEscキー = 戻る\nスペースキー = 別の決定\nCtrl+QまたはALT+F4 = 終了",
		"指が疲れてきたから、この辺で勘弁してネ。",
		False)
		self.main_point = 0
		self.save_file = "save.dat"
	def reset(self):
		self.bgm.start_bgm("wav/spring.wav")
		self.page = 0 #ページ移動(小さな画面遷移)
		self.time = {"t":0, "label":tk.Label(root), "limit":60}
	def save(self, point):
		r = []
		rank = 1
		if os.path.exists(self.save_file):
			isadd = False
			with open(self.save_file, "r") as f:
				t = f.readlines()
			for i in range(len(t)):
				t[i] = t[i].strip()
				if t[i].isdecimal():
					if isadd == False and int(t[i]) < point:
						r.append(str(point))
						isadd = True
					r.append(t[i])
					if isadd == False:
						rank += 1
			if isadd == False:
				r.append(str(point))
				rank = len(r)
		else:
			r.append(str(point))
		with open(self.save_file, "w") as f:
			f.write("\n".join(r)+"\n")
		self.rank = rank
	def moveStage(self, sid):
		self.id = sid
		self.reset()
		self.showWindow()
	def main_countup(self):
		if self.id == self.SID_MAIN:
			self.time["t"] += 1
			if self.time["t"] >= self.time["limit"]:
				self.save(self.main_point)
				self.moveStage(self.SID_END)
			else:
				self.showWindow(True)
				self.time["label"].after(1000, self.main_countup)
	def input_action(self, key):
		if is_key_enable:
			k = key.lower()
			if k == "quit":
				root.quit()
			elif self.id == self.SID_TITLE:
				if k == "return":
					self.moveStage(self.SID_MAIN)
				elif k == "space":
					self.moveStage(self.SID_BACK)
			elif self.id == self.SID_MAIN:
				if k == "escape":
					self.moveStage(self.SID_TITLE)
				elif self.page == 0 and k == "return":
					self.page += 1
					self.showWindow()
					self.main_countup()
				elif self.page != 0 and (k.upper() in ABC or k == "0"):
					p = False
					if self.p_list[0] == self.p_list[1]:
						if k == "0":
							self.main_point += 1
							p = True
					elif k.upper() == self.p_list[1]:
						p = True
					if p:
						play_audio("wav/true.wav", 3)
						self.main_point += 1
					else:
						play_audio("wav/false.wav", 100)
					#連打長押し対策
					self.time["t"] += 1
					if self.time["t"] > self.time["limit"]:
						self.main_point = 0
						self.rank = 0
						self.moveStage(self.SID_TITLE)
					else:
						self.showWindow()
			elif self.id == self.SID_END:
				if k == "return":
					self.main_point = 0
					self.rank = 0
					self.moveStage(self.SID_TITLE)
			elif self.id == self.SID_BACK:
				if k == "return":
					self.page += 1
					if self.description_list[self.page] == False:
						self.moveStage(self.SID_TITLE)
					else:
						self.showWindow()
				elif k == "escape":
					self.moveStage(self.SID_TITLE)
	def showWindow(self, same=False):
		if not same:
			self.memframe.destroy()
		if self.id == self.SID_TITLE:
			self.memframe = tk.Frame(root, bg=self.bg)
			h1 = tk.Label(self.memframe, text="繧ｲ繧ｷ繝･繧ｿ繝ｫ繝亥ｴｩ螢?", **default_style, bg=self.bg, fg="#fff", font=("Arial", 35))
			description = tk.Label(self.memframe, **default_style, bg=self.bg, fg="#fff", font=(ff, 20))
			copy_right = tk.Label(self.memframe, text="© mikasa 2025", **default_style, bg=self.bg, fg="#fff", font=("Arial", 20))
			links = []
			link_opt = ["スタート", "せつめい", "おしまい"]
			link_key = ["Return", "Space", "quit"]
			for i in range(3):
				links.append(tk.Label(self.memframe, text=link_opt[i], **default_style, bg=self.bg, fg="#15b", font=("Arial", 30)))
			h1.place(relx=0, rely=0)
			copy_right.place(relx=0.3, rely=0.8)
			description.place(relx=0.1, rely=0.2)
			speak = Speak(description)
			speak.say("△#○♪〜　うふふふふぁ ...zzz")
			for i in range(len(links)):
				links[i].bind("<Enter>", lambda e, j=i:links[j].config(font=("Arial", 30, "bold")))
				links[i].bind("<Leave>", lambda e, j=i:links[j].config(font=("Arial", 30)))
				links[i].bind("<Button-1>", lambda e, j=link_key[i]:self.input_action(j))
				links[i].place(relx=0.35, rely=0.4+0.1*i)
		elif self.id == self.SID_MAIN:
			if not same:
				self.memframe = tk.Frame(root, bg=self.bg)
				self.pvar = tk.Canvas(self.memframe, highlightthickness=0, width=0, height=10, background="#0ff")
				self.p_list = [abcrand(1), abcrand(1), random.randint(0, 200)]
				t = self.p_list[0]*(self.p_list[2] -1)+self.p_list[1]+self.p_list[0]*(199 -self.p_list[2])
				self.chars = tk.Label(self.memframe, text=t, **default_style, bg=self.bg, fg="#fff", font=("Arial", 20), wraplength=window_size["width"])
			else:
				self.pvar.config(width=window_size["width"]*(self.time["t"]/self.time["limit"]))
			if self.page == 0:
				head = tk.Label(self.memframe, **default_style, bg=self.bg, fg="#fff", font=("Arial", 20))
				next_link = tk.Label(self.memframe, text="開始", **default_style, bg=self.bg, fg="#15b", font=("Arial", 30))
				next_link.bind("<Enter>", lambda e, l=next_link:l.config(font=("Arial", 30, "bold")))
				next_link.bind("<Leave>", lambda e, l=next_link:l.config(font=("Arial", 30)))
				next_link.bind("<Button-1>", lambda e:self.input_action("Return"))
				speak = Speak(head, False, next_link, {"relx":0.5,"rely":0.6})
				head.place(relx=0, rely=0)
				speak.say("１文字だけ違うのがあります。ｷｰﾎﾞｰﾄﾞで回答して下さい。全部同じ場合は数字の0を入力します。大文字小文字は区別しません。シフトキーは不要です。Enterキーで開始します。\n注意: キーを連打したり長押してはいけません。記録が無効になります。")
				self.head = head
				self.next_link = next_link
			else:
				if self.head != None:
					self.next_link.destroy()
					self.head.destroy()
					self.next_link = None
					self.head = None
				self.chars.place(relx=0, rely=0.21)
				self.pvar.place(relx=0, rely=0.95)
		elif self.id == self.SID_END:
			self.memframe = tk.Frame(root, bg=self.bg)
			h1 = tk.Label(self.memframe, text="しゅーりょー ", **default_style, bg=self.bg, fg="#fff", font=("Arial", 30))
			rank = tk.Label(self.memframe, **default_style, bg=self.bg, fg="#fff", font=("Arial", 20))
			rtext = f"得点: {self.main_point} 順位: {self.rank}位\n"
			with open(self.save_file, "r") as f:
				t = f.readlines()
			for i in range(min(len(t), 10)):
				t[i] = str(i+1)+"位 "+t[i]
			rtext += "".join(t[0:10])
			speak = Speak(rank)
			h1.place(relx=0, rely=0)
			rank.place(relx=0, rely=0.1)
			speak.say(rtext)
		elif self.id == self.SID_BACK:
			lbg = "#b30"
			self.memframe = tk.Frame(root, bg=lbg)
			h1 = tk.Label(self.memframe, text="くわしい説明", **default_style, bg=lbg, fg="#fff", font=("Arial", 40))
			description = tk.Label(self.memframe, **default_style, bg=lbg, fg="#fff", font=(ff, 20))
			next_link = tk.Label(self.memframe, text="次へ", **default_style, bg=lbg, fg="#ff0", font=("Arial", 30))
			speak = Speak(description, False, next_link, {"relx":0.5,"rely":0.8})
			h1.place(relx=0, rely=0)
			description.place(relx=0, rely=0.2)
			speak.say(self.description_list[self.page])
			next_link.bind("<Enter>", lambda e, l=next_link:l.config(font=("Arial", 30, "bold")))
			next_link.bind("<Leave>", lambda e, l=next_link:l.config(font=("Arial", 30)))
			next_link.bind("<Button-1>", lambda e:self.input_action("Return"))
			if self.description_list[self.page +1] == False:
				next_link.config(text="タイトルへ戻る")
		self.memframe.place(relx=0, rely=0, **window_size)

# canvasはhighlightthickness=0 で線を消す
def window_head(tk_window, window_size, title, bg_color, resize=False):
	tk_window.title(title)
	try:
		if os.path.exists("favicon.ico"):
			tk_window.iconbitmap(default="favicon.ico")
	except:
		pass
	tk_window.geometry(window_size)
	if resize == False:
		tk_window.resizable(width=False, height=False)
	tk_window.configure(background=bg_color)
if not("REQUEST_METHOD" in os.environ and os.environ["REQUEST_METHOD"]):
	root = tk.Tk()
	window_head(root, f"{window_size['width']}x{window_size['height']}", "蟆?擂縺ｮ鬲疲ｳ穂縺?〒縺?", "#000")
	mainWindow = Stage(root)
	mainWindow.showWindow()
	root.bind('<Control-Key-q>', lambda x:mainWindow.input_action("quit"))
	root.bind("<KeyPress>", lambda event:mainWindow.input_action(event.keysym))
	root.mainloop()
