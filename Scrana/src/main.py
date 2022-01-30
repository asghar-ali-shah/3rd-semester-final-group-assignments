import csv
import math
import operator
import string
import sys

import requests
from PyQt5 import QtWidgets as qw, QtGui as qg, QtCore as qc
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from bs4 import BeautifulSoup

msg = "Data Structures Assignment # 2 \nGroup Members: Yahya Malik --- Abdul Basit --- Asghar Ali Shah"
purifier_data = list(string.punctuation) + ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e',
                                            'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                                            'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                                            'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                                            'Y', 'Z']
main_url = "https://www.bbc.com"
topic_urls = ["/urdu/topics/cjgn7n9zzq7t", "/urdu/topics/cl8l9mveql2t", "/urdu/topics/cw57v2pmll9t",
              "/urdu/topics/c340q0p2585t", "/urdu/topics/ckdxnx900n5t", "/urdu/topics/c40379e2ymxt"]

# Data Vars
words_freq: dict = {}
topic_story_count: dict = {}
min_story_len: int = 99999999999
max_story_len: int = 0
unique_words: list = []
freq_word: str = ""
freq_count: int = 0
top_ten_words: dict = {}


class Worker(qc.QObject):
    finished_analysis = qc.pyqtSignal()
    finished_scrapping = qc.pyqtSignal()
    log_sig = qc.pyqtSignal(str)

    @qc.pyqtSlot()
    def scrape_site(self):
        data = {}
        self.log_sig.emit("starting Scrapping...")
        for topic in topic_urls:
            topic_title = ""
            url = main_url + topic

            storyCount = 0
            page = 1
            story_list = []
            self.log_sig.emit(f'started: {topic}')
            while storyCount < 100:
                res = requests.get(url).text
                doc = BeautifulSoup(res, "html.parser")
                main_content = doc.find("div", class_="gel-wrap no-touch")
                if page == 1:
                    topic_title = main_content.find("h1", class_="topic-title").string
                    self.log_sig.emit("Scrapping section '" + topic_title + "'.....")
                stories = main_content.find("ol").contents
                stories = [tag for tag in stories if tag.name == "li"]

                for story in stories:
                    story_title = ""
                    story_link = ""
                    try:
                        story_title = story.h3.a.string
                        story_link = story.h3.a["href"]
                        self.log_sig.emit(
                            "Scrapping story#" + str(storyCount + 1) + " from section '" + topic_title + "'......")
                    except AttributeError:
                        continue
                    if story_link.split("/")[2] != "live":
                        storyCount += 1
                        story__data = self.get_story_data(main_url + story_link)
                        story_list.append({"story_title": story_title, "story_data": story__data})
                page += 1
                url = self.update_url(page, url)
            data[topic_title] = story_list
        self.log_sig.emit("Scrapping Completed...")
        self.log_sig.emit("Writing Scrapped data to 'extracted_news_data.csv'...")
        # write data to csv file
        header = ["topic", "story_title", "story_data"]
        with open("extracted_news_data.csv", "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for key in data.keys():
                row = [key]
                for singleStory in data[key]:
                    row.append(singleStory["story_title"])
                    row.append(singleStory["story_data"])
                    # print(row)
                    writer.writerow(row)
                    row = [key]
        self.finished_scrapping.emit()

    @qc.pyqtSlot()
    def analyze_data(self):
        global max_story_len, min_story_len, unique_words, words_freq, freq_word, top_ten_words, freq_count
        self.log_sig.emit("started analyzing Data.....")
        with open("extracted_news_data.csv", "r", encoding='utf-8') as f:
            reader = csv.reader(f)
            self.log_sig.emit("reading rows from csv file.....")
            for row in list(reader)[1:]:
                self.count_story(row)
                story_len = len(str(row[2]))
                # self.log_sig.emit("finding min and max length story")
                if story_len > max_story_len:
                    max_story_len = story_len
                if story_len < min_story_len and story_len != 0:
                    min_story_len = story_len

                data_str = self.purify(row[1] + row[2])
                for word in data_str.split(" "):
                    if word in words_freq.keys():
                        words_freq[word] += 1
                    else:
                        words_freq[word] = 1
        freq_word = list(words_freq)[0]
        freq_count = int(words_freq[list(words_freq)[0]])
        for key in words_freq.keys():
            if words_freq[key] > freq_count:
                freq_count = int(words_freq[key])
                freq_word = key
        words_freq.pop("")
        self.log_sig.emit("Finding Top 10 Most Frequent Words")
        top_ten_words = dict(sorted(words_freq.items(), key=operator.itemgetter(1), reverse=True)[:10])
        # unique words
        self.log_sig.emit("Searching for unique words in the data")
        for key in words_freq.keys():
            if int(words_freq[key]) == 1:
                unique_words.append(key)

        self.log_sig.emit("Finished Analysis..")
        self.finished_analysis.emit()

    def purify(self, text: str):
        data_list = list(text)
        data_list = [char for char in data_list if char not in purifier_data]
        data_list = [x for x in data_list if x is not None]
        return "".join(data_list)

    def count_story(self, row):
        global topic_story_count
        topic_name = row[0].strip()
        if topic_name in topic_story_count.keys():
            topic_story_count[topic_name] += 1
        else:
            topic_story_count[topic_name] = 1

    def update_url(self, pageNo, link) -> str:
        if pageNo == 2:
            link = link + f'/page/{pageNo}'
        else:
            lst = link.split("/")
            lst[len(lst) - 1] = str(pageNo)
            link = "/".join(lst)
        return link

    def get_story_data(self, url_string: str):
        self.log_sig.emit(f'scrapping-->: {url_string}')
        story_data = requests.get(url_string).text
        doct = BeautifulSoup(story_data, "html.parser")
        news = doct.find("main")
        news = news.find_all("p")
        lst = [x.string for x in news[1:5]]
        for new in news[5:]:
            if new.find(["b", "a"]) is None and new.string is not None:
                lst.append(new.string)
        lst = [a for a in lst if a is not None]
        rtrn = " ".join(lst)
        if rtrn is None:
            return ""
        return rtrn


class MainWindow(QMainWindow):
    start_sc = qc.pyqtSignal()
    start_an = qc.pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Scrana")
        self.setWindowIcon(qg.QIcon("icon.svg"))
        screen = app.primaryScreen()
        size = screen.size()
        h = (size.height() / 2) - 300
        w = (size.width() / 2) - 400
        if h < 0:
            h = 0
        if w < 0:
            w * -1
        self.setGeometry(math.floor(w), math.floor(h), 800, 600)
        # Grid Layout
        self.grid = qw.QGridLayout()
        # widgets
        self.console = qw.QTextEdit()
        self.urlEdit = qw.QLineEdit()
        self.scrapeButton = qw.QPushButton("Scrape")
        self.analyzeEdit = qw.QLineEdit()
        self.analyzeButton = qw.QPushButton("Analyze")
        # toolbar
        self.tb = self.addToolBar("Toolbar")
        self.tb.addAction("Stop Process", self.stop_thr).setToolTip("Force Stop Analyzing/Scrapping Process")
        self.tb.hide()
        # thread
        self.create_worker_thread()
        # GUI init
        self.init_gui()

    def init_gui(self):
        # menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        fileMenu.addAction("Exit", self.exit_act, shortcut=qg.QKeySequence.Quit)
        # setting widgets
        self.scrapeButton.clicked.connect(self.scrape_act)
        self.analyzeButton.clicked.connect(self.start_analysis)
        self.console.setFont(qg.QFont("Droid Sans Mono", 10, qg.QFont.Weight.Normal))
        self.console.setReadOnly(True)
        self.console.setText(msg)
        self.analyzeEdit.setText("extracted_news_data.csv")
        self.analyzeEdit.setToolTip("Paste your csv file location along with name. scrapping "
                                    "usually takes up to 5 minutes on an average internet connection, "
                                    "If you have already scraped the data paste path to the file here.")
        self.analyzeEdit.setToolTipDuration(10000)
        self.urlEdit.setText(main_url)
        self.grid.addWidget(qw.QLabel("Enter URL to Scrap From: "), 0, 0)
        self.grid.addWidget(self.urlEdit, 0, 1)
        self.grid.addWidget(self.scrapeButton, 0, 2)
        self.grid.addWidget(qw.QLabel("CSV file location: "), 1, 0)
        self.grid.addWidget(self.analyzeEdit, 1, 1)
        self.grid.addWidget(self.analyzeButton, 1, 2)
        self.grid.addWidget(self.console, 2, 0, 2, 0)
        qwidget = qw.QWidget()
        qwidget.setLayout(self.grid)
        self.setCentralWidget(qwidget)

    def create_worker_thread(self):
        # worker Thread
        self.worker = Worker()
        self.w_thread = qc.QThread()
        self.worker.finished_analysis.connect(self.done_analysis)
        self.worker.finished_scrapping.connect(self.done_scrapping)
        self.worker.log_sig.connect(self.console_log)
        self.worker.moveToThread(self.w_thread)
        self.w_thread.start()
        self.start_sc.connect(self.worker.scrape_site)
        self.start_an.connect(self.worker.analyze_data)

    def console_log(self, text):
        console_text = self.console.toPlainText() + "\n" + text
        self.console.clear()
        self.console.setText(console_text)
        self.console.moveCursor(qg.QTextCursor.End)

    def exit_act(self):
        self.close()

    def stop_thr(self):
        self.tb.hide()
        if self.w_thread.isRunning():
            self.w_thread.terminate()
            self.w_thread.wait()
            self.create_worker_thread()

    def start_analysis(self):
        filename = self.analyzeEdit.text()
        try:
            with open(filename, "r", encoding='utf-8') as f:
                pass
            self.console.clear()
            self.tb.show()
            self.start_an.emit()
        except FileNotFoundError:
            QMessageBox(QMessageBox.Critical, "Specified File Not Found", "File Not Found Error!").exec_()

    def done_analysis(self):
        self.tb.hide()
        global freq_count, max_story_len, min_story_len, freq_word, topic_story_count, top_ten_words
        self.console_log("\n\n\n\n\n::::::::::::: Analysis Results For Data Scrapped :::::::::::::")
        self.console_log("Max Story Length:" + str(max_story_len))
        self.console_log("Min Story Length:" + str(min_story_len))
        self.console_log("Most Frequent Word: " + str(freq_word) + "  occurred " + str(freq_count) + " times")
        self.console_log("{:<5}\t{:<15}".format("Story Count", "Topic"))
        for key in topic_story_count.keys():
            self.console_log("{:<5}\t{:<15}".format(topic_story_count[key], key))
        self.console_log("\n\n:::Top 10 Most Frequent Words:::")
        self.console_log("{:<5}\t{:<15}".format("Frequency", "Word"))
        for key in top_ten_words.keys():
            self.console_log("{:<5}\t{:<15}".format(top_ten_words[key], key))
        self.console_log("\n\n::::::::::::::Unique Words::::::::::::::")
        self.console_log(f'Found {len(unique_words)} in tht data. Saved in file \'unique_words.txt\'')
        f = open("unique_words.txt", "w", encoding='utf-8')
        for key in unique_words:
            f.write(f'{key},\n')
        f.close()

    def done_scrapping(self):
        self.tb.hide()
        self.console_log("Scrapping Finished! Scrapped Data is Saved to 'extracted_news_data.csv.")
        self.scrape_act()

    def scrape_act(self):
        url_text = self.urlEdit.text()
        if url_text != main_url:
            msg = qw.QMessageBox()
            msg.setWindowTitle("Wrong URL Input")
            msg.setText("Currently the software can only scrape BBC website")
            msg.setIcon(qw.QMessageBox.Critical)
            msg.exec_()
        else:
            QMessageBox(QMessageBox.Information, "Starting Scrapping",
                        "Staring Scrapping.. It may take up to 5 minutes.").exec_()
            self.console.clear()
            self.tb.show()
            self.start_sc.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
