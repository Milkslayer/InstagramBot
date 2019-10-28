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
import json
from pathlib import Path


class InstagramBot:
    def __init__(self, username=None, password=None, driver_path=r"..\chromedriver\chromedriver.exe"):
        """
        Constructor of the InstagramBot class.
        If no credentials are passed to the constructor it is expected to
        have a 'credentials.json' file in the same directory as the app.
        :param username: Instagram account name
        :param password: Instagram account password
        :param driver_path: Path to the compatible chrome driver
        """
        if username or password is None:
            with open('credentials.json', 'r') as file:
                obj = json.loads(file.read())
                self.__username = obj['login']
                self.__password = obj['password']
        else:
            self.__username = username
            self.__password = password
        self.__driver = webdriver.Chrome(executable_path=driver_path)
        self.DEFAULT_TIMEOUT = 3  # seconds
        self.__rand = Random()

    def login(self) -> None:
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

    def __check_notification_popup(self) -> bool:
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

    @staticmethod
    def export_list(_list: list, file_path: str = './output', exported_file_extension: str = ".json") -> bool:
        """
        Exports provided list to a file
        :param _list: list of variables, preferably list of follower/following ids
        :param file_path: name of exported file
        :param exported_file_extension: file format
        :returns: True if successful export, else False
        """
        try:
            path = Path(file_path + exported_file_extension)
            if path.is_file():
                raise FileExistsError
            with open(file_path + exported_file_extension, 'w') as file:
                if exported_file_extension == ".json":
                    json.dump(_list, file)
                    return True
                elif exported_file_extension == '.txt':
                    file.write("\n".join(str(item) for item in _list))
                    return True

        except FileExistsError:
            print("File Already exists")
            return False
