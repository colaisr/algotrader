import pyautogui


def login_tws_user(settings):
    print("Logging in with users credentials from Server")
    pyautogui.write(settings.TWSUSER)
    pyautogui.PAUSE = 10
    pyautogui.press('tab')
    pyautogui.PAUSE = 10
    pyautogui.write(settings.TWSPASS)
    pyautogui.PAUSE = 10
    pyautogui.press('enter')
    print("Login complete")
