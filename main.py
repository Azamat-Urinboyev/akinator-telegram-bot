from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from akinator_brain import MyAkinator
import functions as fun
import json

from config import TOKEN, ADMIN, PASSWORD

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

with open("data/answer_btn.json") as file:
	answer_btns = json.load(file)


class Game(StatesGroup):
	game = State()
	lan_code = State()

class Admin(StatesGroup):
	rassilka = State()

play_button = fun.get_play_text()

answer_texts = fun.get_answer_text()

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	await message.answer("The bot attempts to determine what fictional or real-life character the you are thinking of by asking a series of questions (like the game Twenty Questions). It uses an artificial intelligence program that learns the best questions to ask through its experience with players.")
	u_id = message.chat.id
	name = message.from_user.first_name
	username = message.from_user.username
	fun.add_user(u_id, name, username)

	btn_data = {
	"English": "language_en",
	"Arabic": "language_ar",
	"Chinese": "language_cn",
	"German": "language_de",
	"Spanish": "language_es",
	"French": "language_fr",
	"Italian": "language_it",
	"Japanese": "language_jp",
	"Korean": "language_kr",
	# "Russian": "language_ru",
	"Turkish": "language_tr",
	"Indonesian": "language_id" 
	}
	btn = fun.get_inline(btn_data, types, 3)
	msg = "Please choose one of the languages below."
	await message.answer(msg, reply_markup=btn)





@dp.callback_query_handler(Text(startswith="language_"), state="*")
async def select_user_language(call: types.CallbackQuery, state: FSMContext):
	await call.answer(cache_time=60)
	lan_code = call.data.split("_")[1]
	if lan_code in ["en", "de", "es", "fr", "it", "jp"]:
		if lan_code == "en":
			msg = "Select the next game thematic"
			btn_data = {
			"Characters": "chooselan/en",
			"Animals": "chooselan/en_animals",
			"Objects": "chooselan/en_objects"
			}
		elif lan_code == "de":
			msg = "Wähle die nächste Spiele-Thematik"
			btn_data = {
			"Figur": "chooselan/de",
			"Tieren": "chooselan/de_animals"
			}
		elif lan_code == "es":
			msg = "Selecciona el siguiente tema del juego"
			btn_data = {
			"Personaje": "chooselan/es",
			"Animales": "chooselan/es_animals"
			}
		elif lan_code == "fr":
			msg = "Sélectionner le thème du jeu"
			btn_data = {
			"Personnages": "chooselan/fr",
			"Animaux": "chooselan/fr_animals",
			"Objets": "chooselan/fr_objects"
			}
		elif lan_code == "it":
			msg = "Seleziona il tema della prossima partita"
			btn_data = {
			"Personaggio": "chooselan/it",
			"Animali": "chooselan/it_animals"
			}
		elif lan_code == "jp":
			msg = "次のゲームテーマを選択する"
			btn_data = {
			"キャラクタ-": "chooselan/jp",
			"動物": "chooselan/jp_animals"
			}
		btn = fun.get_inline(btn_data, types, 2)
		await call.message.edit_text(msg, reply_markup=btn)
		return
	btn_data = fun.get_greeting_text(lan_code)[-1]
	btn = fun.reply_key([btn_data], types)
	msg = fun.get_greeting_text(lan_code)[1]
	await bot.send_message(chat_id=call.message.chat.id, text="OK", reply_markup=btn)
	await call.message.edit_text(msg)
	fun.add_user_language(call.message.chat.id, lan_code)
	async with state.proxy() as data:
		data["lan_code"] = lan_code



@dp.callback_query_handler(Text(startswith="chooselan/"), state="*")
async def select_game_type(call: types.CallbackQuery, state: FSMContext):
	await call.answer(cache_time=60)
	game_type = call.data.split("/")[1]
	lan_code = game_type.split("_")[0]
	try:
		obj_animal = game_type.split("_")[1]
		if obj_animal == "objects":
			msg = fun.get_greeting_text(lan_code)[2]
		else:
			msg = fun.get_greeting_text(lan_code)[3]
	except:
		msg = fun.get_greeting_text(lan_code)[1]
	game = MyAkinator(game_type)
	question = game.question
	btn_data = answer_btns[lan_code]
	await call.message.edit_text(msg)
	await call.message.answer(question, reply_markup=fun.reply_key(btn_data, types, 2))
	async with state.proxy() as data:
		data["game"] = game
		data["lan_code"] = lan_code



#-------------------------------admin side----------------------------#
@dp.callback_query_handler(Text("len_users"), state="*")
async def send_len_users(call: types.CallbackQuery, state: FSMContext):
	users = fun.get_users()
	await call.message.answer(f"The number of users:  {len(users)}👥")



@dp.callback_query_handler(Text("users_data"), state="*")
async def send_users_data(call: types.CallbackQuery, state: FSMContext):
	users = fun.get_users()
	text = fun.msg_entities(users)
	for users_data in fun.get_limit_words(text):
		await bot.send_message(call.message.chat.id, users_data)


@dp.callback_query_handler(Text("rassilka"), state="*")
async def send_message_users(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer("Send you message.")
	await Admin.rassilka.set()



@dp.message_handler(lambda message: message.text in play_button , content_types=["text"], state="*")
async def start_the_game(message: types.Message, state: FSMContext):
	await message.reply("🕐🕒🕓🕔", reply_markup=types.ReplyKeyboardRemove())
	try:
		async with state.proxy() as data:
			lan_code = data["lan_code"]
		game = MyAkinator(lan_code)
		question = game.question
		btn_data = answer_btns[lan_code]
		await message.answer(question, reply_markup=fun.reply_key(btn_data, types, 2))
		async with state.proxy() as data:
			data["game"] = game
	except:
		await message.answer("Please press👇 /start")



@dp.message_handler(lambda message: message.text in answer_texts, content_types=["text"], state="*")
async def start_the_game(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		game = data["game"]
		lan_code = data["lan_code"]
	play_button = fun.get_greeting_text(lan_code)[-1]
	answer = answer_btns[lan_code].index(message.text)
	game.answer_question(answer)
	if game.progression >= 80:
		data = game.win()
		name = data["name"]
		description = data["description"]
		photo = data["absolute_picture_path"]
		caption = f"{name}\n{description}"
		try:
			await bot.send_photo(message.chat.id, photo, caption=caption, reply_markup=fun.reply_key([play_button], types))
		except Exception as e:
			await bot.send_message(message.chat.id, caption, reply_markup=fun.reply_key([play_button], types))
		game.progression = game.progression - 50
		return
	async with state.proxy() as data:
		data["game"] = game
	question = f"{round(game.progression)}% ✅\n\n{game.question}"
	await message.answer(question)


@dp.message_handler(lambda message: message.text == PASSWORD and message.chat.id == ADMIN, content_types=["text"], state="*")
async def password_check(message: types.Message, state: FSMContext):
	msg = "What do you want to do?"
	btn_data = {
	"Users#": "len_users",
	"Users data": "users_data",
	"Send message": "rassilka"
	}
	btn = fun.get_inline(btn_data, types, 2)
	await message.answer(msg, reply_markup=btn)



@dp.message_handler(state=Admin.rassilka, content_types=["text", "photo", "video", "audio", "voice", "animation", "document", "video_note"])
async def send_message_to_users(message: types.Message, state: FSMContext):
	if message.text in ["cancel", "Cancel"]:
		await state.finish()
		await message.reply("Canceled❎")
		return


	async def send_rassilka(message, i):
		try:
			if message.content_type == "text":
			#text
				tex = message.text
				await bot.send_message(i, tex)
			elif message.content_type == "photo":
			#photo
				capt = message.caption
				photo = message.photo[-1].file_id
				await bot.send_photo(i, photo, caption=capt)
			elif message.content_type == "video":
			#video
				capt = message.caption
				photo = message.video.file_id
				await bot.send_video(i, photo, caption=capt)
			elif message.content_type == "audio":
			#audio
				capt = message.caption
				photo = message.audio.file_id
				await bot.send_audio(i, photo, caption=capt)
			elif message.content_type == "voice":
			#voice
				capt = message.caption
				photo = message.voice.file_id
				await bot.send_voice(i, photo, caption=capt)
			elif message.content_type == "animation":
			#animation
				capt = message.caption
				photo = message.animation.file_id
				await bot.send_animation(i, photo, caption=capt)
			elif message.content_type == "document":
			#document
				capt = message.caption
				photo = message.document.file_id
				await bot.send_document(i, photo, caption=capt)
			elif message.content_type == "video_note":
				#rounded video
				video = message.video_note.file_id
				await bot.send_video_note(i, video)
			return
		except Exception as e:
			return e

	for user in fun.get_users():
		user_id = user[0]
		exeption_data = dict()
		exeption = await send_rassilka(message, user_id)
		if exeption:
			if str(exeption) not in exeption_data:
				exeption_data[str(exeption)] = 1
			else:
				exeption_data[str(exeption)] += 1
		msg = []
		for exeption_text, number in exeption_data.items():
			msg.append(f"{exeption_text}:  {number}")
		if len(msg) > 0:
			await bot.send_message(ADMIN, "\n".join(msg))


if __name__ == '__main__':
    executor.start_polling(dp)