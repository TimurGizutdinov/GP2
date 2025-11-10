from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Firefox()
print('браузер запущен')

driver.get('https://app.mayak.bz/users/sign_in')
print('сайт входа загружен')
wait = WebDriverWait(driver, 10)
try:
    login_input = wait.until(EC.presence_of_element_located((By.ID, 'login')))
    password_input = wait.until(EC.presence_of_element_located((By.ID, 'user_password')))
    submit_btn = wait.until(EC.presence_of_element_located((By.NAME, 'commit')))
    print('найдены поля для ввода логина и пароля и кнопки входа')
finally:
    driver.quit()