from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time
import random
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

driver = webdriver.Firefox()
print('браузер запущен')

driver.get('https://app.mayak.bz/users/sign_in')
print('сайт входа загружен')
wait = WebDriverWait(driver, 10)
print('ожидание появления полей ввода')

login_input = wait.until(EC.presence_of_element_located((By.ID, 'login')))
password_input = wait.until(EC.presence_of_element_located((By.ID, 'user_password')))
submit_btn = wait.until(EC.presence_of_element_located((By.NAME, 'commit')))
print('найдены поля для ввода логина и пароля и кнопки входа')

login_input.send_keys('mariya.strong@gmail.com')
password_input.send_keys('Mariya5')
print('ввод логина и пароля')

submit_btn.click()
print('тап по кнопке входа')

try:
    print('проверяем наличие всплывающего окна')
    pop_up = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.modal.show')))
    print('если обнаружили всплывающее окно то закрываем')
    close_btn = pop_up.find_element(By.CSS_SELECTOR, 'button.close')
    close_btn.click()
    WebDriverWait(driver, 1).until(EC.invisibility_of_element(pop_up))
    print('закрыли')
except TimeoutException:
    print('не появилось, идем далее')

print('переходим на страницу продавца')
driver.get('https://app.mayak.bz/wb/sellers/2071435?from_date=2025-10-10&to_date=2025-11-08&period=месяц+%2830+суток%29&sort_field=revenue&sort_order=desc&fbs=true&tab=goods&id=2071435')
print('переход на страницу продавца')
print('ждем загрузку страницы')

print('ищем заголовок таблицы')
thead = driver.find_element(By.CSS_SELECTOR, 'div.fixed-table-header table thead')

allowed_fields = {
    'brand-product','brand-seller','brand-category','brand-sku',
    'revenue','sales','lost_revenue','lost_sales',
    'brand_max_price','brand_min_price','brand_avg_price',
}
order = [
    'brand-product','brand-seller','brand-category','brand-sku',
    'revenue','sales','lost_revenue','lost_sales',
    'brand_max_price','brand_min_price','brand_avg_price',
]

print('начинаем сбор заголовков таблицы')
title = {}
for i in thead.find_elements(By.CSS_SELECTOR, 'th[data-field]'):
    j = i.get_attribute('data-field')
    if j in allowed_fields:
        txt = i.find_element(By.CSS_SELECTOR, '.th-inner').get_attribute('innerText') or ''
        title[j] = ' '.join(txt.split())

headers = ['Фото'] + [title[j] for j in order]
name = 'wb_products6.csv'

print('создаем CSV файл и записываем заголовки')
with open(name, 'w', newline='', encoding='utf-8') as f:
    csv.writer(f).writerow(headers)

parsed = urlparse(driver.current_url)
q = parse_qs(parsed.query)
all = []

print('собираем данные по всем страницам')
for p in range(1, 501):
    print(f'обработка страницы {p}')
    q['goods_page'] = [str(p)]
    q['page'] = [str(p-1)]
    new_query = urlencode({k: v[0] for k, v in q.items()}, doseq=False)
    new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', new_query, ''))
    driver.get(new_url)

    print('ждем загрузку страницы данных')
    time.sleep(10)

    container = driver.find_element(By.CSS_SELECTOR, 'div.fixed-table-body')
    print('контейнер таблицы найден')

    height = driver.execute_script('return arguments[0].scrollHeight;', container)
    viewport = driver.execute_script('return arguments[0].clientHeight;', container)
    current = driver.execute_script('return arguments[0].scrollTop;', container)

    down = random.randint(int(viewport*0.4), int(viewport*0.9))
    up = random.randint(int(viewport*0.1), int(viewport*0.3))

    n_down = min(current + down, height - viewport)
    driver.execute_script('arguments[0].scrollTop = arguments[1];', container, n_down)

    n_up = max(n_down - up, 0)
    driver.execute_script('arguments[0].scrollTop = arguments[1];', container, n_up)

    print('ищем таблицу с данными')
    tbody = driver.find_element(By.CSS_SELECTOR, 'div.fixed-table-body table tbody')
    rows = tbody.find_elements(By.CSS_SELECTOR, 'tr')
    print(f'найдено строк: {len(rows)}')

    page_data = []
    for tr in rows:
        td = tr.find_elements(By.CSS_SELECTOR, 'td')
        row = []
        img = td[0].find_elements(By.TAG_NAME, 'img')
        src = img[0].get_attribute('src')
        row.append(src)
        for idx in range(1, 12):
            if idx >= len(td):
                row.append('')
                continue
            txt = (td[idx].get_attribute('innerText') or '').strip()
            row.append(' '.join(txt.split()))
        page_data.append(row)

    all.extend(page_data)
    print(f'page {p}: {len(rows)} товаров, всего собрано {len(all)}')

    if page_data:
        print(f'запись данных страницы {p} в CSV')
        with open(name, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(page_data)

print(f'Собрано строк {len(all)}. файл: {name}')

driver.quit()