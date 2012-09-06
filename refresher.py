from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import time
import sys, os
import traceback
import argparse
import gntp.notifier

def get_driver():
    global _driver
    if '_driver' not in globals():
        if sys.platform.startswith('darwin'):
            FILE_PATH = os.path.join(os.getcwd(), 'chromedriver')
        elif sys.platform.startswith('win32'):
            FILE_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')
        _driver = webdriver.Chrome(executable_path=FILE_PATH)
    return _driver

def login(username, password):
    driver = get_driver()
    START_URL = "https://ssol.columbia.edu/"
    USERNAME_NAME = "u_id"
    PASSWORD_NAME = "u_pw"

    driver.get(START_URL)
    username_element = driver.find_element_by_name(USERNAME_NAME)
    username_element.send_keys(username)
    driver.find_element_by_name(PASSWORD_NAME).send_keys(password)
    username_element.submit()

def go_to_registration_page():
    driver = get_driver()
    VISA_AGREEMENT_NAME1 = "tran[1]_agree"
    VISA_AGREEMENT_NAME2 = "tran[1]_fj1"
    REGISTRATION_PAGE_CLASS = "clsDataGridTitle"

    registration_link = driver.find_element_by_link_text("Registration")
    registration_link.click()

    try:
        agree_element1 = driver.find_element_by_name(VISA_AGREEMENT_NAME1)
        agree_element1.click()
        agree_element2 = driver.find_element_by_name(VISA_AGREEMENT_NAME2)
        agree_element2.click()
        agree_element1.submit()
    except NoSuchElementException:
        try: # Check to see if already on registration page.
            driver.find_element_by_class_name(REGISTRATION_PAGE_CLASS)
        except NoSuchElementException:
            raise NoSuchElementException()

def search_and_register_class(query):
    driver = get_driver()
    REGISTRATION_ACCEPT_CLASS = "regb"
    SEARCH_BOX_NAME = "tran[1]_ss"
    ADD_CLASS_NAME = "tran[1]_act"
    SUCCESS_CSS = "div.msgs b"
    FAIL_CSS = "div.msge"

    search_link_element = driver.find_element_by_link_text("Search Class")
    search_link_element.click()

    search_element = driver.find_element_by_name(SEARCH_BOX_NAME) # Search Class box
    search_element.send_keys(query)
    search_element.submit()

    while True:
        if try_register_class(query):
            success_elements = driver.find_elements_by_css_selector(SUCCESS_CSS)
            if len(success_elements) > 0:
                print('%s has been registered.' % query)
                growl.notifier.mini('%s has been registered.' % query)
                return
        time.sleep(10)
        driver.refresh()

def try_register_class(query):
    driver = get_driver()
    REGISTRATION_ACCEPT_CLASS = "regb"
    ADD_CLASS_NAME = "tran[1]_act"
    SEARCH_BOX_NAME = "tran[1]_ss"

    search_element = driver.find_element_by_name(SEARCH_BOX_NAME) # Search Class box
    search_element.submit()
    register_elements = driver.find_elements_by_class_name(REGISTRATION_ACCEPT_CLASS)
    if len(register_elements) == 0: # Registration not possible
        print('No available class found for: %s' % query)
        return False
    register_elements[0].click()
    add_class_element = driver.find_element_by_name(ADD_CLASS_NAME)
    add_class_element.click() # Back to registration page.
    return True

if __name__ == '__main__':
    try:
        from config import args
    except ImportError:
        parser = argparse.ArgumentParser(description='Automatically access SSOL')
        parser.add_argument('username')
        parser.add_argument('password')
        args = parser.parse_args()
    try:
        login(args['username'], args['password'])
        go_to_registration_page()
        for class_name in args['classes']:
            search_and_register_class(class_name)
    except NoSuchElementException:
        # TODO: Detect and handle any sequence in webpage.
        traceback.print_exc(file=sys.stdout)
    finally:
        get_driver().quit()
        growl.notifier.mini("Script finished.")