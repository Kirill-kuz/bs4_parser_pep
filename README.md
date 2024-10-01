# Парсер документации Python и PEP
## Описание
Парсер информации о Python с **https://docs.python.org/3/** и **https://peps.python.org/**
### 1. Перед использованием
Клонируйте репозиторий к себе на компьютер:
```
git clone git@github.com:Kirill-kuz/bs4_parser_pep.git
```
В корневой папке создайте виртуальное окружение и установите зависимости.
```
python -m venv venv
```
```
pip install -r requirements.txt
```
### 2. Запустите файл main.py выбрав парсер и аргументы
```
python src/main.py [парсер] [аргумент]
```
### 3. Виды парсеров
- whats-new (выводит спсок изменений в python)
```
python main.py whats-new [аргумент]
```
- latest_versions (выводит список версий python и ссылки на документацию.)
```
python main.py latest-versions [аргумент]
```
- download (скачивает zip архив с документацией python в pdf формате.)
```
python main.py download [аргумент]
```
- pep (выводит список статусов документов pep и их количество в каждом статусе. )
```
python main.py pep [аргумент]
```
### 4. Аргументы
Есть возможность указывать аргументы для изменения работы программы:   
- -h, --help
Общая информация о командах.
```
python main.py -h
```
- -c, --clear-cache
Очистка кеша перед выполнением парсинга.
```
python main.py [парсер] -c
```
