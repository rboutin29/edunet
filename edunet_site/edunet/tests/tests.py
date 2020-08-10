import unittest

from django.test import TestCase, Client, LiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from .. import views

'''
class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        response = self.client.get('/edunet/african-american-studies/african-american-history-from-emancipation-to-the-present/')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['transcript_numbers']), 2)

class MySeleniumTests(LiveServerTestCase):
    fixtures = ['user-data.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        timeout = 2
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name('username')
        username_input.send_keys('rianb')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys('rianboutin')
        self.selenium.find_element_by_xpath('//button[@value="login"]').click()
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_tag_name('body')
        )
'''
        