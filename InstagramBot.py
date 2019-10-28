from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from random import Random
import bs4 as bs
import time
import re


class InstagramBot:
    def __init__(self, username, password, driver_path=r"..\chromedriver\chromedriver.exe"):
        self.__username = username
        self.__password = password
        self.__driver = webdriver.Chrome(executable_path=driver_path)
        self.DEFAULT_TIMEOUT = 3  # seconds
        self.__rand = Random()

    def login(self):
        """
        Logs the bot in to the default page of Instagram
        :returns True if Log in was successful, else Raise error
        """
        driver = self.__driver
        driver.get("https://www.instagram.com/accounts/login/")
        try:
            login_button = WebDriverWait(driver, self.DEFAULT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH,
                                                                                                             "//button[@type='submit']")))
            username_field = driver.find_element_by_name(name="username")
            password_field = driver.find_element_by_name(name="password")

            username_field.send_keys(self.__username)
            password_field.send_keys(self.__password)
            login_button.click()
            self.__check_notification_popup()
        except TimeoutException:
            print("ERROR: Could not log in")
            raise

    def __check_notification_popup(self):
        """
        Sometimes a pop-up appears, when you log in to Instagram, asking about notifications.
        This function gets rid of it by clicking "Not Now"
        :returns True if Click was successful, else False
        """
        driver = self.__driver
        try:
            notification_button = WebDriverWait(driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//button[text()='Not Now']")))
            notification_button.click()
            return True
        except TimeoutException:
            print("There is no notification pop-up")
            return False

    #
    def get_followers_id(self, account_username: str) -> list:
        """
        Returns a list of follower ids(user names) for specified account
        :param: account_username: Instagram account user name
        :return: list with user ids
        """

        driver = self.__driver
        driver.get(f"https://www.instagram.com/{account_username}")
        try:
            followers_button = WebDriverWait(driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, f"//a[@href='/{account_username}/followers/']")))
            follower_count = int(followers_button.find_element_by_tag_name("span").text)
            followers_button.click()
            follower_list = WebDriverWait(driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//ul/div")))

            actions = ActionChains(self.__driver)

            start_count = len(driver.find_elements_by_xpath("//div[@role='dialog']//ul/div/li"))
            clicked = False
            count = start_count
            follower_list_elements = []
            while count < follower_count-5:
                follower_list_elements = driver.find_elements_by_xpath("//div[@role='dialog']//ul/div/li")
                count = len(follower_list_elements)
                if count == start_count:
                    follower_list.click()
                if count != start_count and not clicked:
                    follower_list.click()
                    clicked = True

                actions.send_keys(Keys.ARROW_DOWN)
                actions.perform()
                time.sleep(self.__rand.uniform(0.5, 1.5))

            followers = []
            xml = "<div>"
            for el in follower_list_elements:
                xml += el.get_attribute('outerHTML')
            xml += "</div>"
            soup = bs.BeautifulSoup(xml, "html.parser")
            for el in soup.find_all('a', {"title": re.compile(r".*")}):
                followers.append(el['title'])
            return followers
        except TimeoutException:
            print("ERROR: Something unexpected happened while extracting followers")
            raise
