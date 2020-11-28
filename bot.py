import requests
import datetime
import pymongo
import random

 
class DB:
    def __init__(self):
        self.client = pymongo.MongoClient("") # <-- Insert URL here
        self.db = self.client.Hackvelon2020.Users
 
    def add_user(self, telegram_id):
        user = {"name": '',
                "city": '',
                "age": '',
                "sex": '',
                "favourites": [],
                "in_search": False,
                "in_dialog": False,
                "telegram_id": telegram_id,
                "telegram_curr": -1}
        self.db.insert_one(user)
        print(f'Added user with id - {telegram_id}')
        return True
 
    def add_dialog(self, from_id, to_id):
        first = self.db.update({ "telegram_id": from_id }, { "$set": { "telegram_curr": to_id, "in_search": False, "in_dialog": True} })
        second = self.db.update({ "telegram_id": to_id }, { "$set": { "telegram_curr": from_id, "in_search": False, "in_dialog": True} })
        print('Added dialog ({from_id}, {to_id})')
        return True

    def del_dialog(self, from_id, to_id):
        first = self.db.update({ "telegram_id": from_id }, { "$set": {"in_search": False, "in_dialog": False}})
        second = self.db.update({ "telegram_id": to_id }, { "$set": {"in_search": False, "in_dialog": False}})
        print(f'Ended dialog ({from_id}, {to_id})')
        return True
    
    def update_user(self, from_id, text, field):
        self.db.update({ "telegram_id": from_id }, { "$set": { field: text} })

    def get_user(self, telegram_id):
        user = self.db.find_one({"telegram_id": telegram_id})
        if user != None:
            print(f'get_user: {telegram_id}')
            return True, user
        else:
            return False, user
 
    def get_in_search(self):
        users = self.db.find({"in_search": True})
        result = [i['telegram_id'] for i in users]
        print("in_search", result)
        return result
 
    def get_in_dialogs(self):
        users = self.db.find({"in_dialog": True})
        result = {}
        for i in users:
            result[str(i['telegram_id'])] = i['telegram_curr']

        print("dialogs, ", result)
        return result
 

class BotHandler:
    def __init__(self):
        self.query = []
        self.dialogs = {}
        self.api_url = "https://api.telegram.org/bot1405115222:AAHi1V4sxypGDe6Fing1hgsPjOC58ik_IuA/"
 
    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        result = requests.get(self.api_url + method, params)
        result_json = result.json()['result']
        return result_json
 
    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        result = requests.post(self.api_url + method, params)
        return result
 
    def get_last_update(self):
        get_result = self.get_updates()
 
        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]
        return last_update
    
    def start_dialog(self, last_user_id):
        if last_user_id not in self.query:
            self.query.append(last_user_id)

        if len(self.query) > 1:
            from_id = last_user_id
            self.query.pop(self.query.index(from_id))

            random.shuffle(self.query)

            to_id = self.query[0]
            self.query.pop(self.query.index(to_id))

            self.dialogs[str(from_id)] = to_id
            self.dialogs[str(to_id)] = from_id
            
            db.add_dialog(from_id, to_id)
            print('dialogs,', self.dialogs)

            (a, first) = db.get_user(from_id)
            (a, second) = db.get_user(to_id)

            self.send_message(from_id, f'bot: Собеседник найден, (Подсказка: {"Он" if second["sex"] == "М" else "Она"} любит {", ".join(second["favourites"])})')
            self.send_message(to_id, f'bot: Собеседник найден, (Подсказка: {"Он" if first["sex"] == "М" else "Она"} любит {", ".join(first["favourites"])})')

            return True
        else:
            return False

    def start_dialogs(self):
        while len(bot.query) > 1:
            random.shuffle(self.query)

            from_id = self.query[0]
            self.query.pop(self.query.index(from_id))

            to_id = self.query[0]
            self.query.pop(self.query.index(to_id))

            self.dialogs[str(from_id)] = to_id
            self.dialogs[str(to_id)] = from_id
            
            db.add_dialog(from_id, to_id)
            print('dialogs,', self.dialogs)
            self.send_message(from_id, 'bot: Собеседник найден')
            self.send_message(to_id, 'bot: Собеседник найден')
 
    def end_dialog(self, last_user_id):
        from_id = last_user_id
        to_id = self.dialogs[str(from_id)]
 
        del self.dialogs[str(from_id)]
        del self.dialogs[str(to_id)]

        db.del_dialog(from_id, to_id)

        bot.send_message(from_id, 'bot: Разговор окончен. Вы можете начать новый диалог /start')
        bot.send_message(to_id, 'bot: Собеседник завершил разговор. Вы можете начать новый диалог /start')

 
def main():  
    new_offset = None
    stack = {}
    while True:
        bot.get_updates(new_offset)
 
        last_update = bot.get_last_update()
 
        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_user_id = last_update['message']['chat']['id']
        last_user = last_update['message']['chat']['first_name']        

        print(f"New event {last_update_id}: {last_user}({last_user_id}) = {last_chat_text}")

        if last_chat_text[0] == '/':
            if last_chat_text[1:] == 'help':
                pass
            elif last_chat_text[1:] == 'start':
                if last_user_id in bot.query:
                    bot.send_message(last_user_id, 'bot: Пожалуйста подождите, собеседник уже ищется')
                    bot.start_dialog(last_user_id)
                else:
                    if db.get_user(last_user_id)[0]:
                        bot.send_message(last_user_id, 'bot: Начался поиск собеседника')
                        bot.start_dialog(last_user_id)
                        
                    else:
                        bot.send_message(last_user_id, 'bot: Необходимо зарегистрироваться /registration')
            
            elif last_chat_text[1:] == 'stop':
                if last_user_id in bot.query:
                    bot.send_message(last_user_id, 'bot: Поиск остановлен')
                    bot.query.pop(bot.query.index(last_user_id))
                else:
                    if str(last_user_id) in bot.dialogs:
                        bot.end_dialog(last_user_id)

                    elif db.get_user(last_user_id)[1]['in_search'] == False:
                        bot.send_message(last_user_id, 'bot: Вы не начинали поиск собеседника')
                        
                    else:
                        bot.send_message(last_user_id, 'bot: Необходимо зарегистрироваться /registration')

            elif last_chat_text[1:] == 'registration':
                if last_user_id not in bot.query and last_user_id not in bot.dialogs:
                    stack[str(last_user_id)] = 'name'
                    bot.send_message(last_user_id, 'bot: Как мне вас называть?')
                else:
                    bot.send_message(last_user_id, 'bot: Чтобы изменить информацию, необходимо закончить разговор')

            elif last_chat_text[1:] == 'report':
                bot.send_message(last_user_id, 'bot: Благодарим за сотрудничество')

            else:
                bot.send_message(last_user_id, 'bot: Команда не распознана')
        
        else:
            if str(last_user_id) in stack:
                if stack[str(last_user_id)] == 'name':
                    db.add_user(last_user_id)
                    db.update_user(last_user_id, last_chat_text, 'name')
                    bot.send_message(last_user_id, 'bot: Из какого вы города?')
                    stack[str(last_user_id)] = 'city'
                
                elif stack[str(last_user_id)] == 'city':
                    db.update_user(last_user_id, last_chat_text, 'city')
                    bot.send_message(last_user_id, 'bot: Сколько вам лет?')
                    stack[str(last_user_id)] = 'age'

                elif stack[str(last_user_id)] == 'age':
                    db.update_user(last_user_id, last_chat_text, 'age')
                    bot.send_message(last_user_id, 'bot: Выберите свой пол:\nМ / Ж')
                    stack[str(last_user_id)] = 'sex'

                elif stack[str(last_user_id)] == 'sex':
                    db.update_user(last_user_id, last_chat_text, 'sex')
                    bot.send_message(last_user_id, 'bot: Напишите ваши увлечения через запятые')
                    stack[str(last_user_id)] = 'favourites'

                elif stack[str(last_user_id)] == 'favourites':
                    db.update_user(last_user_id, last_chat_text.split(','), 'favourites')
                    bot.send_message(last_user_id, 'bot: Регистрация завершена. Напишите /start чтобы начать поиск')
                    del stack[str(last_user_id)]
                
            else:
                if str(last_user_id) in bot.dialogs:
                    print(f"New message: from - {last_user_id}, to - {bot.dialogs[str(last_user_id)]} = {last_chat_text}")
                    bot.send_message(bot.dialogs[str(last_user_id)], last_chat_text)
                else:
                    bot.send_message(last_user_id, 'bot: Сначала нужно начать диалог /start')
                    

        new_offset = last_update_id + 1

if __name__ == '__main__':
    db = DB()
    bot = BotHandler()

    bot.query = db.get_in_search()
    bot.start_dialogs()

    bot.dialogs = db.get_in_dialogs()
    main()
