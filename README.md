# G2G TG BOT
Group to Group Telegram chat-bot. \
Links multiply chat-groups into single connected network, \
and allow exchange messages between all connected groups 

---
## Config files
- `bot_token.txt` - contains Botfather Token of your bot 
- `users.txt` - contains list of User's Groups ID's 
- `admins.txt` - contains list of Admin's Groups ID's

---

## Bot Commands
- `/start` - вызов бота 
- `/on` - бот слушает сообщения 
- `/off` - бот игнорирует сообщения 
- `/all` + "твое_сообщение" - отправить всем 
- `/get_groups_id` - получить ID групп 
- `/add_user_group` + "ID_группы" - добавить ID в список users.txt 
- `/del_user_group` + "ID_группы" - удалить ID из списка users.txt 
- `/add_admin_group` + "ID_группы" - добавить ID в список admins.txt 
- `/del_admin_group` + "ID_группы" - удалить ID из списка admins.txt 

---

## Manual (Guide)
Чтобы отправить сообщение в другую группу сделайте одно из следующего: \
- упомяните бота в сообщении через его никнейм с символом `@` 
- ответьте сообщением на сообщение (`reply`) от бота 
- включите режим прослушки сообщений командой `/on` ; пишите в чат любые сообщения для перессылки в другую группу ; по завершению выключите режим прослушки командой `/off` 
- (`только для админской группы`) начните сообщение с команды `/all` и напишите после нее текст, который хотите разослать во все пользовательские группы

Режим прослушки `/on` (`/off`) для админской группы (а также упоминание бота через его никнейм с символом `@`) после каждого сообщения в чате присылает меню с кнопками выбора пользовательского чата, куда отправить сообщение.

Для получения списка всех доступных для обмена сообщениями админских и пользовательских групп используйте команду `/get_groups_id` \
(Данная команда работает только в админских группах)

Для добавления ID группы в список админских или пользовательских групп (в файлы конфигов `admins.txt` и `users.txt`) используйте соответствующие команды: \
- `/add_admin_group` + "ID_группы" - добавить ID в список admins.txt 
- `/add_user_group` + "ID_группы" - добавить ID в список users.txt 
(Данные команды работают только в админских группах)

Для исключения ID группы в список админских или пользовательских групп (из файлов конфигов `admins.txt` и `users.txt`) используйте соответствующие команды: \
- `/del_admin_group` + "ID_группы" - удалить ID из списка admins.txt 
- `/del_user_group` + "ID_группы" - удалить ID из списка users.txt 
(Данные команды работают только в админских группах)
