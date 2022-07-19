import sqlite3
import json


#--------------------functions-----------------------#
def reply_key(names: list, types,  row=1):
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	keyboards = [types.KeyboardButton(text=name) for name in names]
	f = lambda A, n=row: [A[i:i+n] for i in range(0, len(A), n)]
	names = f(keyboards)
	for name in names:
		keyboard.add(*name)
	return keyboard



def get_inline(data, types, row=1):
	buttons = []
	keyboard = types.InlineKeyboardMarkup(row_width=row)
	for lan, call_data in data.items():
		buttons.append(types.InlineKeyboardButton(text=lan, callback_data=call_data))
	keyboard.add(*buttons)
	return keyboard


def add_user(u_id: int, name: str, username: str = None):
	conn = sqlite3.connect("data/users.db")
	c = conn.cursor()
	c.execute("SELECT * FROM users WHERE u_id=:u_id", {"u_id": u_id})
	data = len(c.fetchall())
	if data != 0:
		c.execute("UPDATE users SET username=:username, name=:name WHERE u_id=:u_id",
			{"u_id": u_id, "username": username, "name": name})
		conn.commit()
		conn.close()
		return None
	try:
		c.execute("INSERT INTO users VALUES(?, ?, ?, ?)", (u_id, name, username, None))
	except Exception as e:
		return e
	conn.commit()
	conn.close()
	return None



def add_user_language(u_id: int, language: str):
	conn = sqlite3.connect("data/users.db")
	c = conn.cursor()
	c.execute("UPDATE users SET language=:language WHERE u_id=:u_id",
			{"u_id": u_id, "language": language})
	conn.commit()
	conn.close()


def get_greeting_text(lan_code:str):
	conn = sqlite3.connect("data/game_data.db")
	c = conn.cursor()
	c.execute("SELECT * FROM start WHERE lan_code=:language", {"language": lan_code})
	text = c.fetchone()
	conn.close()
	return text

def get_play_text():
	conn = sqlite3.connect("data/game_data.db")
	c = conn.cursor()
	c.execute("SELECT * FROM start")
	# print(c.fetchall())
	text = [i[-1] for i in c.fetchall()]
	conn.close()
	return text

def get_answer_text():
	with open("data/answer_btn.json") as file:
		data = json.load(file)
		result = list()
		for i in data:
			for a in data[i]:
				result.append(a)
		return result


def get_users():
	conn = sqlite3.connect("data/users.db")
	c = conn.cursor()
	c.execute("SELECT * FROM users")
	users = c.fetchall()
	conn.close()
	return users


def get_limit_words(text):
	text = [text]
	while len(text[-1]) >= 4096:
		before = text[-1][:4096]
		index = before.rfind("\n")
		before = text[-1][:index]
		after = text[-1][index:]
		text.remove(text[-1])
		text.append(before)
		text.append(after)
	return text


def msg_entities(data):
	result_data = []
	for user in data:
		name = user[1]
		username = user[2]
		if username != None:
			result_data.append(f"{name}:  @{username}")
		else:
			result_data.append(f"{name}   ------")
	result_data = "\n".join(result_data)
	return result_data

