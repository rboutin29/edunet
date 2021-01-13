'''
Script used for live server testing with selenium.
'''
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.edge.webdriver import WebDriver

class MySeleniumTests(StaticLiveServerTestCase):
    '''Class for live server tests with selenium.'''
    fixtures = ['edunet_testdata.json']

    @classmethod
    def setUpClass(cls):
        '''Set up function for live server testing.'''
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        '''Tear down function for live server testing.'''
        yield cls.selenium
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        '''Test log in with live server testing... yields winerror 10054.'''
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('rianl')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('rianl')
        self.selenium.find_element_by_xpath('//button[@value="login"]').click()
