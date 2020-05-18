from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import time
import pickle
import random
import os
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
    script_dir = os.path.dirname(__file__)
    rel_path = "commented_users.txt"
    abs_file_path = os.path.join(script_dir, "data", rel_path)
    with open(abs_file_path, "w") as file:
        for user in users:
            file.write(user + "\n")


def get_driver(gui_bool):
    options = Options()
    options.headless = not gui_bool
    user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(options=options, executable_path="./geckodriver123", firefox_profile=profile)
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


def save_cookies(driver, username):
    script_dir = os.path.dirname(__file__)
    rel_path = f"{username}.pkl"
    rel_path_1 = "cookies"
    abs_file_path = os.path.join(script_dir, rel_path_1, rel_path)
    pickle.dump(driver.get_cookies(), open(abs_file_path, "wb"))


def load_cookies(driver, username):
    script_dir = os.path.dirname(__file__)
    rel_path = f"{username}.pkl"
    rel_path_1 = "cookies"
    abs_file_path = os.path.join(script_dir, rel_path_1, rel_path)
    cookies = pickle.load(open(abs_file_path, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)


def search_user(driver, username):
    elems = driver.find_elements_by_tag_name("svg")
    for elem in elems:
        if elem.get_attribute("aria-label") == "Search & Explore":
            elem.click()
            break
    # delay()
    elem = driver.find_element_by_tag_name("input")
    elem.send_keys(username)
    wait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "li")))
    elem = driver.find_element_by_tag_name("a").find_element_by_tag_name("div")
    elem.click()


def open_img(driver):
    delay(0.5)
    wait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div[style='flex-direction: column; padding-bottom: 0px; padding-top: 0px;']")))
    # delay(0.5)
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
        # delay(0.5)
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


def get_usernames_of_post(driver, user):
    user_list = []
    delay()
    search_user(driver, user)
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
    delay(0.5)
    wait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "svg[aria-label='Comment']")))
    elems = driver.find_elements_by_tag_name("svg")
    for elem in elems:
        if elem.get_attribute("aria-label") == "Comment":
            elem.click()
            break
    delay(0.5)
    wait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "textarea[aria-label='Add a comment…']")))
    elem = driver.find_element_by_tag_name("textarea")
    elem.send_keys(random.choice(comments))
    elem = driver.find_element_by_tag_name("button")
    elem.click()
    delay(2)


def is_private_or_no_posts(driver):
    html = driver.page_source
    if "This Account is Private" in html or "No Posts Yet" in html:
        return True
    else:
        return False


def commenting(driver, user, comments):
    search_user(driver, user)
    delay(0.5)
    if is_private_or_no_posts(driver):
        raise Exception("Acc is private or no posts")
    open_img(driver)
    # delay()
    make_comment(driver, comments)


def delay(time_sleep=3.0):
    time.sleep(time_sleep)


def prepare_to_comment(driver, user_list, commented_users, comments, output, refresh_black_list):
    for user in user_list:
        if user in commented_users:
            pass
            output(f"User {user} in black list. Skip it")
        else:
            try:
                commenting(driver, user, comments)
                output(f"Account {user} successfully commented")
                commented_users.append(user)
                save_commented_users(commented_users)
                refresh_black_list()
            except:
                output(f"Account {user} is private or error has occurred")
                is_banned(driver)


def is_banned(driver):
    html = driver.page_source
    if "Your Account Was Compromised" in html:
        raise Exception("Account compromised")


def start(username, password, users, comments, commented_users, load_from_cookies, driver, output, refresh_black_list):
    # output("Bot started")
    driver.delete_all_cookies()
    driver.get("https://www.instagram.com/")

    if load_from_cookies:
        try:
            output("Load cookies")
            load_cookies(driver, username)
            driver.get("https://www.instagram.com/")
        except:
            output("Failed to load cookies")
    is_banned(driver)
    delay()
    try:
        output("Try to log in")
        log_in(driver, username, password)
        output("Successful logged in")
    except:
        output("Failed to log in or you are already logged in")
    is_banned(driver)
    delay()
    output("Turn off notification")
    notification_off(driver)
    save_cookies(driver, username)
    for user in users:
        output(f"Collecting users of {user}")
        user_list = get_usernames_of_post(driver, user)
        is_banned(driver)
        prepare_to_comment(driver, user_list, commented_users, comments, output, refresh_black_list)
    save_cookies(driver, username)
    driver.close()
    # output("Bot finished work")


def pre_start(usernames, passwords, users, comments, commented_users, load_from_cookies, driver, output, refresh_black_list, current_user):
    output("Bot started")
    accs = [(usernames[i], passwords[i]) for i in range(len(usernames))]
    for username, password in accs:
        current_user(username)
        try:
            start(username, password, users, comments, commented_users, load_from_cookies, driver, output, refresh_black_list)
        except:
            output("Smth go wrong or acc is blocked. Changing account")
            continue
        break
    output("Bot finished work")


# driver = get_driver(True)
# driver.get("https://www.instagram.com/")
# users = get_users()
# comments = get_comments()
# commented_users = get_commented_users()
# start(username="miml.cat", password="Test1234", users=users, comments=comments, commented_users=commented_users, new_acc=False)
