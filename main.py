import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
import design  # Это наш конвертированный файл дизайна
import funcs
from selenium.webdriver.firefox.options import Options
from selenium import webdriver


class StartBot(QThread):

    def __init__(self, login, password, users, comments, commented_users, load_with_gui, load_from_cookies):
        QThread.__init__(self)
        self.driver = None
        self.login = login
        self.password = password
        self.users = users
        self.comments = comments
        self.commented_users = commented_users
        self.load_with_gui = load_with_gui
        self.load_from_cookies = load_from_cookies

    def __del__(self):
        self.wait()

    def run(self):
        self.driver = self.get_driver(self.load_with_gui)
        funcs.start(self.login, self.password, self.users, self.comments, self.commented_users, self.load_from_cookies, self.driver)

    def get_driver(self, gui_bool):
        options = Options()
        options.headless = not gui_bool
        user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(options=options, executable_path="./geckodriver", firefox_profile=profile)
        driver.set_window_size(360, 1100)
        return driver

    def get_close(self):
        try:
            self.driver.close()
        except:
            pass


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.bot_thread = None
        self.setupUi(self)
        self.pushButton.clicked.connect(self.start_bot)
        self.load_commented_users()

    def closeEvent(self, event):
        try:
            self.bot_thread.get_close()
        except:
            pass

    def start_bot(self):
        try:
            self.bot_thread.get_close()
        except:
            pass
        users_text = self.textEdit.toPlainText()
        if len(users_text) == 0:
            self.textBrowser.setPlainText("Please enter usernames")
            return
        else:
            users = users_text.split("\n")
        comments_text = self.textEdit_2.toPlainText()
        if len(comments_text) == 0:
            self.textBrowser.setPlainText("Please enter comments")
            return
        else:
            comments = comments_text.split("\n")
        login = self.lineEdit.text()
        if len(login) == 0:
            self.textBrowser.setPlainText("Please enter login")
            return
        password = self.lineEdit_2.text()
        if len(password) == 0:
            self.textBrowser.setPlainText("Please enter password")
            return
        load_from_cookies = self.checkBox.isEnabled()
        load_with_gui = self.checkBox_2.isEnabled()
        commented_users_text = self.textBrowser_2.toPlainText()
        if len(commented_users_text) == 0:
            commented_users = []
        else:
            commented_users = commented_users_text.split("\n")
        self.textBrowser.setPlainText("Bot started")
        self.bot_thread = StartBot(login, password, users, comments, commented_users, load_with_gui, load_from_cookies)
        self.bot_thread.start()


    def load_commented_users(self):
        with open("commented_users.txt", "r") as file:
            commented_users = file.read()
        self.textBrowser_2.setPlainText(commented_users)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()

