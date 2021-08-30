from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver, common
import time
import telegram_channel

browser = webdriver.Chrome()
browser.implicitly_wait(5)

# Pages to parse range
start_page = 150
end_page = 158

# Все car-dictionary элементы на запарсенных страницах (1 страница - 20 машин)
all_cars_lst_dic = []
# Только отсортированыные по просмотрам
sorted_by_views_dic = []
# список car-dictionary элементов, уже отправленнх в телеграм канал
already_send_to_channel = []


def go_to_page(page_number):
    """Переход в браузере на страницу page_number г. Алматы (Казахстан)"""

    current_link = "https://kolesa.kz/cars/almaty/?page=" + str(page_number)
    browser.get(current_link)
    print(f"----------------------------------- PAGE # {page_number} -----------------------------------")


def console_print_car_data(car_data_dictionary, order=0):
    """Принт-форма для печати данных об авто в консоли, берет значения из словаля car_data_dictionary"""

    car_mark = car_data_dictionary['car_mark']
    car_id = car_data_dictionary['car_id']
    link_to_car = car_data_dictionary['link_to_car']
    car_views = car_data_dictionary['car_views']
    # price = car_data_dictionary['car_price']
    # year = car_data_dictionary['car_year']

    cute_string = f'{order}) Kolesa car ID is: {car_id} -> {link_to_car}  Views: {car_views}  Car-mark: {car_mark}'
    print(cute_string)

    return cute_string


def channel_print_car_data(car_data_dictionary, order=0):
    """Текст для телеграмм канала, берет значения из словаля car_data_dictionary"""

    car_mark = car_data_dictionary['car_mark']
    car_id = car_data_dictionary['car_id']
    link_to_car = car_data_dictionary['link_to_car']
    car_views = car_data_dictionary['car_views']
    price = car_data_dictionary['car_price']
    year = car_data_dictionary['car_year']

    cute_string = f'🔔 *Новый автомобиль г. Алматы*\n\n' \
                  f'{order}) Kolesa car ID is: {car_id} ' \
                  f'\nМарка машины: *{car_mark} {year} * ' \
                  f'\nЦена: *{price}* ' \
                  f'\nПросмотров: {car_views}' \
                  f'\n{link_to_car}'

    console_print_car_data(car_data_dictionary, order)
    return cute_string


def get_car_views(car_data_text):
    """
    Функция форматирует текст от car-web-element-text и возращает только кол-во просмотров
    У некоторых машин на колеса, есть комментарии, если они есть, это дополнительное поле в спике
    """
    return car_data_text[-2] if car_data_text[-2].isdigit() and car_data_text[-1].isdigit() else car_data_text[-1]


def write_cars_on_page():
    """
    Берет все веб-элементы машины (car-web-element) на странице (20 карточек),
    Создает словарь car_data_dictionary [keys: car_id, link_to_car, car_views, car_mark]
    """
    try:
        counter = 0
        # Получить карточки машин
        cars_on_current_page = browser.find_elements_by_css_selector("div#results > div.row.vw-item.list-item")

        for car in cars_on_current_page:
            # Словарь хранит ID, ссылку на машину, количество просмотров и Марку автомобиля
            car_data_dictionary = {}
            counter += 1

            # ID машины на колёса
            car_id = car.get_attribute('data-id')
            car_data_dictionary['car_id'] = car_id

            # Ссылка на машину
            link_to_car = f'https://kolesa.kz/a/show/{car_id}'
            car_data_dictionary['link_to_car'] = link_to_car

            # Весь текст из карточки автомобиля, на общей странице авто
            car_data = car.text.split('\n')

            # Цена и год выпуска
            car_data_dictionary['car_price'] = car_data[1] if car_data[0] != 'Новая' else car_data[2]
            car_data_dictionary['car_year'] = car_data[2][:7] if car_data[0] != 'Новая' else car_data[3][:7]

            # Количество просмотров
            car_data_dictionary['car_views'] = get_car_views(car_data)
            car_data_dictionary['car_mark'] = car_data[0] if car_data[0] != 'Новая' else car_data[1]

            # общий список - словарь автомобилей
            if car_data_dictionary not in all_cars_lst_dic:
                all_cars_lst_dic.append(car_data_dictionary)

            # ВСЕ ЛОГИ
            console_print_car_data(car_data_dictionary, counter)

    except common.exceptions.NoSuchElementException:
        print("ERROR: NoSuchElementException")


def submit_new_cars(views=5):
    """
        Функция фильтрует по просмотрам views
        Добавляет car-dictionary в список sorted_by_views_dic
        Постит в Телеграмм новые автомобили, которых нет в списке already_send_to_channel
    """
    print("\n--------------------FILTER BY VIEWS-----------------\n")
    counter = len(already_send_to_channel) + 1

    for car in all_cars_lst_dic:
        if int(car['car_views']) < views and car not in sorted_by_views_dic:
            sorted_by_views_dic.append(car)
            if car not in already_send_to_channel:
                # здесь отправка в телеграмм канал
                send_car_to_telegram(car, counter)
                counter += 1
    print("\n--------------------END FILTER BY VIEWS-----------------\n")


def send_car_to_telegram(car, counter):
    """
        Отправляет сообщения в телеграм канал
        Добавляет в список уже отправленные в канал автомобили
    """
    result_text = channel_print_car_data(car, counter)
    telegram_channel.telegram_bot_send_text(result_text)
    already_send_to_channel.append(car)


if __name__ == "__main__":
    try:
        telegram_channel.telegram_bot_send_text("PARSER STARTED")
        while True:
            for i in range(start_page, end_page):
                go_to_page(i)
                write_cars_on_page()
            submit_new_cars()
            # Перезапуск каждые 60 сек
            time.sleep(60)
            # очистка списка от переполнений
            if len(all_cars_lst_dic) > 10_000:
                all_cars_lst_dic = []
                sorted_by_views_dic = []

    finally:
        time.sleep(15)
        browser.quit()

