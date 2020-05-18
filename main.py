import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import design  # Это наш конвертированный файл дизайна
import funcs
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import os


class StartBot(QThread):
    signal_a = pyqtSignal(str)
    signal_b = pyqtSignal()
    signal_c = pyqtSignal(str)

    def __init__(self, logins, passwords, users, comments, commented_users, load_with_gui, load_from_cookies):
        QThread.__init__(self)
        self.driver = None
        self.logins = logins
        self.passwords = passwords
        self.users = users
        self.comments = comments
        self.commented_users = commented_users
        self.load_with_gui = load_with_gui
        self.load_from_cookies = load_from_cookies

    def __del__(self):
        self.wait()

    def run(self):
        self.driver = self.get_driver(self.load_with_gui)
        funcs.pre_start(self.logins, self.passwords, self.users, self.comments, self.commented_users, self.load_from_cookies, self.driver, self.signal_a.emit, self.signal_b.emit, self.signal_c.emit)

    def get_driver(self, gui_bool):
        options = Options()
        options.headless = not gui_bool
        user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        script_dir = os.path.dirname(__file__)
        rel_path = "geckodriver"
        abs_file_path = os.path.join(script_dir, "data", rel_path)
        driver = webdriver.Firefox(options=options, executable_path=abs_file_path, firefox_profile=profile)
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
        self.pre_load_info()

    def closeEvent(self, event):
        try:
            self.bot_thread.get_close()
        except:
            pass
        self.save_config()

    @pyqtSlot(str, name="change_text")
    def handle_signal(self, value):
        self.textBrowser.setPlainText(value)

    @pyqtSlot(name="change_black_list")
    def handle_signal_1(self):
        self.load_commented_users()

    @pyqtSlot(str, name="change_current_user")
    def handle_signal_2(self, value):
        self.textBrowser_3.setPlainText(value)

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
        logins_text = self.textEdit_3.toPlainText()
        if len(logins_text) == 0:
            self.textBrowser.setPlainText("Please enter login(s)")
            return
        else:
            logins = logins_text.split("\n")
        passwords_text = self.textEdit_4.toPlainText()
        if len(passwords_text) == 0:
            self.textBrowser.setPlainText("Please enter password(s)")
            return
        else:
            passwords = passwords_text.split("\n")
        if len(logins) != len(passwords):
            self.textBrowser.setPlainText("Тumber of logins and passwords does not match")
            return
        load_from_cookies = self.checkBox.isChecked()
        load_with_gui = self.checkBox_2.isChecked()
        commented_users_text = self.textBrowser_2.toPlainText()
        if len(commented_users_text) == 0:
            commented_users = []
        else:
            commented_users = commented_users_text.split("\n")
        self.bot_thread = StartBot(logins, passwords, users, comments, commented_users, load_with_gui, load_from_cookies)
        self.bot_thread.signal_a.connect(self.handle_signal)
        self.bot_thread.signal_b.connect(self.handle_signal_1)
        self.bot_thread.signal_c.connect(self.handle_signal_2)
        self.bot_thread.start()


    def load_commented_users(self):
        script_dir = os.path.dirname(__file__)
        rel_path = "commented_users.txt"
        abs_file_path = os.path.join(script_dir, "data", rel_path)
        with open(abs_file_path, "r") as file:
            commented_users = file.read()
        self.textBrowser_2.setPlainText(commented_users)


    def pre_load_info(self):
        script_dir = os.path.dirname(__file__)
        folder = "data"
        file_name = "users.txt"
        abs_file_path = os.path.join(script_dir, folder, file_name)
        with open(abs_file_path, "r") as file:
            text = file.read()
        self.textEdit.setPlainText(text)

        folder = "data"
        file_name = "comments.txt"
        abs_file_path = os.path.join(script_dir, folder, file_name)
        with open(abs_file_path, "r") as file:
            text = file.read()
        self.textEdit_2.setPlainText(text)

        folder = "data"
        file_name = "logins.txt"
        abs_file_path = os.path.join(script_dir, folder, file_name)
        with open(abs_file_path, "r") as file:
            text = file.read()
        self.textEdit_3.setPlainText(text)

        folder = "data"
        file_name = "passwords.txt"
        abs_file_path = os.path.join(script_dir, folder, file_name)
        with open(abs_file_path, "r") as file:
            text = file.read()
        self.textEdit_4.setPlainText(text)

    def save_config(self):
        script_dir = os.path.dirname(__file__)
        folder = "data"
        file_name = "users.txt"
        abs_file_path = os.path.join(script_dir, folder, file_name)
        with open(abs_file_path, "w") as file:
            file.write(self.textEdit.toPlainText())

        folder = "data"
        file_name = "comments.txt"
        abs_file_path = os.path.join(script_dir, folder, file_name)
        with open(abs_file_path, "w") as file:
            file.write(self.textEdit_2.toPlainText())

        folder = "data"
        file_name = "logins.txt"
        abs_file_path = os.path.join(script_dir, folder, file_name)
        with open(abs_file_path, "w") as file:
            file.write(self.textEdit_3.toPlainText())

        folder = "data"
        file_name = "passwords.txt"
        abs_file_path = os.path.join(script_dir, folder, file_name)
        with open(abs_file_path, "w") as file:
            file.write(self.textEdit_4.toPlainText())


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()

