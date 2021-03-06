# Парсер книг с сайта tululu.org
Собираем базу онлайн библитеки в учебных целях.
Скрипт парсит категорию научной фантастики библиотеки, собирая всю информацию 
о находящихся в категории книгах и скачивая `txt` версии книг и фото обложек.


## Установка:
1. Скопируйте все файлы.  
2. Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки 
зависимостей:  
```
pip install -r requirements.txt
```    
Скрипт готов к использованию!


## Использование:
### 1. Запустите скрипт выполнив в командной строке.  
```
python main.py
```
### 2. Скрипт можно запустить с опциональными парметрами: 
#### ***`--start_page`***

принимает `int` значение - номер страницы с которой начинается парсинг категории. По умолчанию: `= 1`.

*Пример:*    
```
python main.py --start_page 50
```

#### ***`--end_page`***

принимает `int` значение - номер страницы окончания парсинга категории. По умолчанию: `=701`. 
      
*Пример:* 
 
```
python main.py --start_page 50 --end_page 100
```

#### ***`--dest_folder`***

принимает `str` путь к папке для сохранения информации. По умолчанию ниформация будет сохранена в папке выполнения 
программы.

*Пример:*  
    
```
python main.py --start_page 50 --end_page 100 --dest_folder ~/Downloads/
```
#### ***`--skip_images`***

если указано картинки не скачиваются.
    
#### ***`--skip_txt`***

если указано txt файлы не скачиваются.
     
*Пример:*
      
```
python main.py --start_page 50 --end_page 100 --dest_folder ~/Downloads/ --skip_txt
```
   
#### ***`--json_path`***

принимает `str` путь к папке для сохранения json файла содержащего инфомарцию о книгах. По умолчанию информация будет 
сохранена в директории выполнения программы.
