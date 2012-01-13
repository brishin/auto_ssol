from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import time
import sys, os
import traceback
import argparse

def get_driver():
	global instance_driver
	if 'instance_driver' not in globals():
		FILE_PATH = os.path.join(os.getcwd(), 'chromedriver')
		instance_driver = webdriver.Chrome(executable_path=FILE_PATH) 
	
	return instance_driver

def login(username, password):
	driver = get_driver()
	driver.get("https://ssol.columbia.edu/")
	username_element = driver.find_element_by_name("u_id")
	username_element.send_keys(username)
	driver.find_element_by_name("u_pw").send_keys(password)
	username_element.submit()

def go_to_registration_page():
	driver = get_driver()
	registration_link = driver.find_element_by_link_text("Registration")
	registration_link.click()

	try: # Visa student agreement page. 
		agree_element1 = driver.find_element_by_name("tran[1]_agree")
		agree_element1.click()
		agree_element2 = driver.find_element_by_name("tran[1]_fj1")
		agree_element2.click()
		agree_element1.submit()
	except NoSuchElementException:
		try: # Check to see if already on registration page.
			driver.find_element_by_class_name("clsDataGridTitle")
		except NoSuchElementException:
			raise NoSuchElementException()

def search_and_register_class(query):
	driver = get_driver()
	search_link_element = driver.find_element_by_link_text("Search Class")
	search_link_element.click()

	search_element = driver.find_element_by_name("tran[1]_ss") # Search Class box
	search_element.send_keys(query)
	search_element.submit()

	register_elements = driver.find_elements_by_class_name("regb")
	if len(register_elements) == 0: # Registration not possible
		print('No available class found for: %s' % query)
		driver.find_element_by_link_text("Back To Registration").click()
		return
	register_elements[0].click()
	add_class_element = driver.find_element_by_name("tran[1]_act")
	add_class_element.click() # Back to registration page.
	messages = driver.find_elements_by_css_selector("div.msgs b") # Success message
	messages.extend(driver.find_elements_by_css_selector("div.msge")) #Fail message
	print "\"%s: %s\"" % (query, messages[0].text)

if __name__ == '__main__':
	try:
		from config import args
	except ImportError:
		# Optional command line arguments in case config.py doesn't exist.
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