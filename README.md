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
Чтобы отправить сообщение в другую группу сделайте одно из следующего: 
- упомяните бота в сообщении через его никнейм с символом `@` 
- ответьте сообщением на сообщение (`reply`) от бота 
- включите режим прослушки сообщений командой `/on` ; пишите в чат любые сообщения для перессылки в другую группу ; по завершению выключите режим прослушки командой `/off` 
- (`только для админской группы`) начните сообщение с команды `/all` и напишите после нее текст, который хотите разослать во все пользовательские группы


Режим прослушки `/on` (`/off`) для админской группы (а также упоминание бота через его никнейм с символом `@`) после каждого сообщения в чате присылает меню с кнопками выбора пользовательского чата, куда отправить сообщение.


Для получения списка всех доступных для обмена сообщениями админских и пользовательских групп используйте команду:
- `/get_groups_id` \
(Данная команда работает только в админских группах)


Для добавления ID группы в список админских или пользовательских групп (в файлы конфигов `admins.txt` и `users.txt`) используйте соответствующие команды: 
- `/add_admin_group` + "ID_группы" - добавить ID в список admins.txt 
- `/add_user_group` + "ID_группы" - добавить ID в список users.txt \
(Данные команды работают только в админских группах)


Для исключения ID группы в список админских или пользовательских групп (из файлов конфигов `admins.txt` и `users.txt`) используйте соответствующие команды: 
- `/del_admin_group` + "ID_группы" - удалить ID из списка admins.txt 
- `/del_user_group` + "ID_группы" - удалить ID из списка users.txt \
(Данные команды работают только в админских группах)

---

## Deployment

Ниже приведена подробная пошаговая инструкция по развертыванию бота в вашем облаке (на примере сервера на базе Ubuntu). В инструкции описаны команды для установки необходимых пакетов, создания виртуального окружения и настройки systemd-сервиса для автозапуска.

---

## Шаг 1. Подготовка сервера

1. Подключитесь по SSH к вашему серверу.

2. Обновите пакеты системы:

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. (При необходимости) Установите Git для клонирования репозитория:

   ```bash
   sudo apt install git -y
   ```

---

## Шаг 2. Установка Python и создание виртуального окружения

1. Установите Python 3 и необходимые пакеты, если они ещё не установлены:

   ```bash
   sudo apt install python3 python3-venv python3-pip -y
   ```

2. Создайте папку для проекта и перейдите в неё (например, `/home/username/telegram-bot`):

   ```bash
   mkdir -p ~/telegram-bot
   cd ~/telegram-bot
   ```

3. Клонируйте проект из репозитория локально:

   ```bash
   git clone https://github.com/chelaxian/G2G_TG_BOT .
   ```

4. Создайте виртуальное окружение:

   ```bash
   python3 -m venv venv
   ```

5. Активируйте виртуальное окружение:

   ```bash
   source venv/bin/activate
   ```

---

## Шаг 3. Установка зависимостей Python

1. Обновите pip:

   ```bash
   pip install --upgrade pip
   ```

2. Установите пакет [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) (версия 20+ поддерживает асинхронный API):

   ```bash
   pip install python-telegram-bot
   ```

   *Если вы предпочитаете использовать файл зависимостей, создайте файл `requirements.txt` со следующим содержимым:*

   ```txt
   python-telegram-bot
   ```

   *и выполните:*

   ```bash
   pip install -r requirements.txt
   ```

---

## Шаг 4. Настройка файлов проекта

1. В корневой папке проекта разместите файл `bot_token.txt` с токеном вашего бота (одна строка, содержащая токен).

2. Убедитесь, что файлы `users.txt` и `admins.txt` существуют (их можно создать пустыми, если группы будут добавляться позже).

---

## Шаг 5. Запуск бота вручную

Чтобы проверить работу бота, выполните команду:

```bash
python group-bot.py
```

Если бот успешно запустился, он начнет опрашивать сервер Telegram (long polling).

---

## Шаг 6. Автоматический запуск бота через systemd (опционально)

Чтобы бот запускался автоматически и перезапускался при сбоях, создайте systemd-сервис.

1. Создайте файл сервиса:

   ```bash
   sudo nano /etc/systemd/system/telegrambot.service
   ```

2. Вставьте в него следующий конфигурационный текст (не забудьте заменить `username` на ваше имя пользователя и путь к проекту):

   ```ini
   [Unit]
   Description=Telegram Bot Service
   After=network.target

   [Service]
   User=username
   WorkingDirectory=/home/USERNAME/telegram-bot
   ExecStart=/home/USERNAME/telegram-bot/venv/bin/python group-bot.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. Сохраните файл и перезагрузите systemd-демон:

   ```bash
   sudo systemctl daemon-reload
   ```

4. Включите автозапуск сервиса:

   ```bash
   sudo systemctl enable telegrambot.service
   ```

5. Запустите сервис:

   ```bash
   sudo systemctl start telegrambot.service
   ```

6. Проверьте статус сервиса:

   ```bash
   sudo systemctl status telegrambot.service
   ```

7. Для просмотра логов используйте:

   ```bash
   sudo journalctl -u telegrambot.service -f
   ```

---

Теперь ваш бот развернут и запущен в облаке.
