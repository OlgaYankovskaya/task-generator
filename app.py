# coding: utf-8
from flask import Flask, request, render_template, send_file
import random
import json
from os import listdir
from os.path import isfile, join
from fpdf import FPDF

# Запуск приложения Flask
app = Flask(__name__)
JSONPATH = "./json/" # Путь к папке json
LANGUAGES = None # Все языки, которые есть в приложении
LANG = None # Язык, который используется на момент работы приложения
UI = None # Перевод пользовательского интерфейса
TASKS = None # Задания, которые будут отображаться на веб-странице

# Функция, которая загружает все языки, доступные в приложении
def getLanguages():
    global LANGUAGES
    global LANG

    files = [f for f in listdir(JSONPATH) if isfile(join(JSONPATH, f))]
    LANGUAGES = [f.split("tasks")[1].split(".")[0] for f in files]
    LANG = LANGUAGES[0]

# Функция, которая загружает перевод пользовательского интерфейса на выбранном языке
def getUI(lang: str = "FR"):
    global UI

    path = JSONPATH + 'tasks' + lang + '.json'
    f = json.load(open(path, 'r', encoding='utf-8'))
    UI = f["UI"]

# Функция, который загружает выбранный язык
def setLang(lang : str):
    global LANG
    global UI
    global TASKS

    LANG = lang
    getUI(LANG)
    TASKS = None
    return render_template('home.html', isLoaded=False, ui=UI, languages=LANGUAGES)

# Функция, которая выбирает задания в случайном порядке на выбранном языке
def getRandomTasks(lang: str = "FR"):
    path = JSONPATH + 'tasks' + lang + '.json'
    f = json.load(open(path, 'r', encoding='utf-8'))

    correctVerbTasks = f["tasks"]["correctVerb"]
    correctLetterTasks = f["tasks"]["correctLetter"]
    verbConjugationTasks = f["tasks"]["verbConjugation"]
    otherTasks = f["tasks"]["other"]
    wordTransformationTasks = f["tasks"]["wordTransformation"]
    correctNounTasks = f["tasks"]["correctNoun"]

    tasks = {
        "correctVerb": random.choice(correctVerbTasks),
        "correctLetter": random.choice(correctLetterTasks),
        "verbConjugation": random.choice(verbConjugationTasks),
        "other": random.choice(otherTasks),
        "wordTransformation": random.choice(wordTransformationTasks),
        "correctNoun": random.choice(correctNounTasks)
    }
    return tasks

# Функция, генерирующая и загружающая PDF-файл
def downloadPDF(tasks: dict):
    myPdf = FPDF()
    myPdf.add_page()
    myPdf.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
    myPdf.set_font("DejaVu", size=12)

    myPdf.multi_cell(180, 10, txt=UI["tasks"], align="C")
    myPdf.multi_cell(160, 10, txt="", align="L")
    myPdf.multi_cell(160, 10, txt=tasks["correctVerb"]["task"], align="L")
    myPdf.multi_cell(160, 10, txt=tasks["correctVerb"]["question"], align="L")
    myPdf.multi_cell(160, 10, txt=tasks["correctVerb"]["answer"], align="L")

    myPdf.multi_cell(160, 10, txt="", align="L")
    myPdf.multi_cell(160, 10, txt=tasks["correctLetter"]["task"], align="L")
    myPdf.multi_cell(160, 10, txt=tasks["correctLetter"]["question"], align="L")

    myPdf.multi_cell(160, 10, txt="", align="L")
    myPdf.multi_cell(160, 10, txt=tasks["verbConjugation"]["task"], align="L")
    myPdf.multi_cell(160, 10, txt=tasks["verbConjugation"]["question"], align="L")

    myPdf.multi_cell(160, 10, txt="", align="L")
    myPdf.multi_cell(160, 10, txt=tasks["other"]["task"], align="L")
    myPdf.multi_cell(160, 10, txt=tasks["other"]["question"], align="L")

    myPdf.multi_cell(160, 10, txt="", align="L")
    myPdf.multi_cell(160, 10, txt=tasks["wordTransformation"]["task"], align="L")
    myPdf.multi_cell(160, 10, txt=tasks["wordTransformation"]["question"], align="L")

    myPdf.multi_cell(160, 10, txt="", align="L")
    myPdf.multi_cell(160, 10, txt=tasks["correctNoun"]["task"], align="L")
    myPdf.multi_cell(160, 10, txt=tasks["correctNoun"]["question"], align="L")
    myPdf.multi_cell(160, 10, txt=tasks["correctNoun"]["answer"], align="L")

    myPdf.output("tasks.pdf")
    myPdf.close()

    return send_file("tasks.pdf", as_attachment=True)

@app.route('/', methods = ['GET', 'POST']) # Домашняя страница приложения
# Функция, отвечающая за алгоритм работы домашней страницы приложения
def home():
    global UI
    global LANG
    global TASKS
    action = None

    if not LANGUAGES or not LANG or not UI:
        getLanguages()
        getUI(LANG)

    if request.method == 'POST':
        action = request.form.get("action")

        if action in LANGUAGES:
            return setLang(action)

        if UI["generate"] == action:
            TASKS = getRandomTasks(LANG)
            return render_template('home.html', isLoaded=True, tasks=TASKS, ui=UI, languages=LANGUAGES)

    return render_template('home.html', isLoaded=False, ui=UI, languages=LANGUAGES)

@app.route('/download', methods = ['GET']) # Путь, который отвечает за загрузку файла
def downloadFile():
    return downloadPDF(TASKS)

if __name__ == "main":
    app.run(debug=True)
