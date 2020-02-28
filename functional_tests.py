from selenium import webdriver
import unittest
import sys



# Мы проверяем этим тестом функциональность приложения
# с помощью selenium
# руководство по установке и запуску selenium по ссылке ниже:
# https://selenium-python.com/install-geckodriver

class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.url = 'http://{}/'.format(command_line_param)
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_site_main_page(self):
        # Запустив dev-server командой python manage.py runserver
        # в другой консоли мы запускаем на исполнение функциональное
        # тестирование командой python functional_tests.py
        # прежде всего мы проверяем загузку заголовка главной страницы "Сайта"
        self.browser.get(self.url)
        self.assertIn('Главная страница', self.browser.title)
        self.browser.get(self.url+'contacts/')
        self.assertIn('Контакты', self.browser.title)

        # self.fail('Finish the test!')
    # def test_user_can_go_to_contact_page(self):

    # def test_can_go_to_vacancies_list(self):
    #     #Пользователь переходит на страницу вакансий
    #     # и видит заголовок "Список вакансий"
    #     self.browser.get('http://localhost:8000/vacancies/list')
    #     self.assertIn('Список вакансий', self.browser.title)

    #     # Пользователь видит заголовок h2 "Список вакансий на странице"
    #     header_text = self.browser.find_element_by_tag_name('h2').text
    #     self.assertIn('Список вакансий', header_text)

    #     # Пользователь видит список карточек с классом card-item
    #     cards = self.browser.find_elements_by_class_name('card-item')
    #     self.assertTrue(cards)

    #     # Пользователь видит заголовки вакансий
    #     card_headers = self.browser.find_element_by_class_name('card-vacancy-title')
    #     self.assertTrue(card_headers)

    #     #Пользователь заходит на страницу регистрации
    #     #Регистрируется
    #     #Заходит в ЛК под своим логином и паролем
    #     #Нажимает кнопку "Добавить вакансию"
    #     #Заполняет форму
    #     #Сохраняет форму
    #     #Редактирует форму
    #     #и т.д.

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("command line parameter must be supplied for these tests")
    command_line_param = sys.argv[1]
    del sys.argv[1:]
    unittest.main(warnings='ignore')
