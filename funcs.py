from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import time
import pickle
import random
from selenium.webdriver.common.action_chains import ActionChains


# def get_users():
#     with open("users.txt", "r") as file:
#         users = file.readlines()
#     users = [user.rstrip() for user in users]
#     return users
#
#
# def get_comments():
#     with open("comments.txt", "r") as file:
#         comments = file.readlines()
#     comments = [comment.rstrip() for comment in comments]
#     return comments
#
#
# def get_commented_users():
#     with open("commented_users.txt", "r") as file:
#         commented_users = file.readlines()
#     commented_users = [commented_user.rstrip() for commented_user in commented_users]
#     return commented_users


def save_commented_users(users):
    with open("commented_users.txt", "w") as file:
        for user in users:
            file.write(user + "\n")


def get_driver(gui_bool):
    options = Options()
    options.headless = not gui_bool
    user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(options=options, executable_path="geckodriver123", firefox_profile=profile)
    driver.set_window_size(360, 1100)
    return driver


def log_in(driver, username, password):
    elems = driver.find_elements_by_tag_name("button")
    for elem in elems:
        if elem.text == "Log In":
            elem.click()
            break
    delay()
    elems = driver.find_elements_by_tag_name("input")
    elems[0].send_keys(username)
    elems[1].send_keys(password)
    elems = driver.find_elements_by_tag_name("button")
    for elem in elems:
        if elem.get_attribute("type") == "submit":
            elem.click()
            break
    else:
        raise Exception("Button not found")


def notification_off(driver):
    elems = driver.find_elements_by_tag_name("button")
    for elem in elems:
        if elem.text == "Not Now":
            elem.click()
            break


def save_cookies(driver):
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))


def load_cookies(driver):
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)


def search_user(driver, username):
    elems = driver.find_elements_by_tag_name("svg")
    for elem in elems:
        if elem.get_attribute("aria-label") == "Search & Explore":
            elem.click()
            break
    delay()
    elem = driver.find_element_by_tag_name("input")
    elem.send_keys(username)
    delay()
    elem = driver.find_element_by_tag_name("a").find_element_by_tag_name("div")
    elem.click()


def open_img(driver):
    elems = driver.find_elements_by_tag_name("div")
    for elem in elems:
        if elem.get_attribute("style") == "flex-direction: column; padding-bottom: 0px; padding-top: 0px;":
            img = elem.find_element_by_tag_name("div").find_element_by_tag_name("div")
            img.click()
            break


def open_likes(driver):
    elems = driver.find_elements_by_tag_name("a")
    for elem in elems:
        if "likes" in elem.text:
            elem.click()
            break


def parsing_user_list(driver):
    usernames = []
    elems = driver.find_elements_by_tag_name("a")
    for elem in elems[:-12]:
        try:
            href = elem.get_attribute("href")
            href = href.split("/")
            usernames.append(href[3])
        except:
            pass
    return usernames


def get_user_list(driver):
    user_list = []
    previous = ""
    previous_count = 0
    while True:
        delay(0.5)
        user_list += parsing_user_list(driver)
        if previous == user_list[-1]:
            previous_count += 1
        else:
            previous_count = 0
        elems = driver.find_elements_by_tag_name("a")
        elems[len(elems)-12].location_once_scrolled_into_view
        previous = user_list[-1]
        if previous_count == 2:
            break
    return list(set(user_list))


def get_usernames_of_post(driver, users):
    user_list = []
    for user in users:
        delay()
        search_user(driver, user)
        delay()
        open_img(driver)
        delay()
        open_likes(driver)
        delay()
        try:
            user_list += get_user_list(driver)
        except:
            pass
    return user_list


def make_comment(driver, comments):
    elems = driver.find_elements_by_tag_name("svg")
    for elem in elems:
        if elem.get_attribute("aria-label") == "Comment":
            elem.click()
            break
    delay(2)
    elem = driver.find_element_by_tag_name("textarea")
    elem.send_keys(random.choice(comments))
    elem = driver.find_element_by_tag_name("button")
    elem.click()
    delay(5)


def commenting(driver, user, comments):
    delay()
    search_user(driver, user)
    delay()
    open_img(driver)
    delay()
    make_comment(driver, comments)


def delay(time_sleep=3):
    time.sleep(time_sleep)


def start(username, password, users, comments, commented_users, load_from_cookies, driver):
    # output.setPlainText("Init driver")
    # driver = get_driver(load_with_gui)
    driver.get("https://www.instagram.com/")

    if load_from_cookies:
        try:
            load_cookies(driver)
            driver.get("https://www.instagram.com/")
        except:
            pass

    delay()
    try:
        log_in(driver, username, password)
    except:
        pass

    delay()
    notification_off(driver)

    user_list = get_usernames_of_post(driver, users)
    for user in user_list:
        if user in commented_users:
            pass
            # print("User in black list")
        else:
            commented_users.append(user)
            try:
                commenting(driver, user, comments)
            except:
                pass
    save_commented_users(commented_users)
    save_cookies(driver)
    driver.close()
    # print("end")


# users = get_users()
# comments = get_comments()
# commented_users = get_commented_users()
# start(username="miml.cat", password="Test1234", users=users, comments=comments, commented_users=commented_users, new_acc=False)
