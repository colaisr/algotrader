import pyautogui


def login_tws_user(settings):
    image = pyautogui.locateOnScreen("login.png")

    # Searches for the image
    while image == None:
        image = pyautogui.locateOnScreen("login.png")
        print("still haven't found the image")
    print("Logging in with users credentials from Server")
    pyautogui.write(settings.TWSUSER)
    pyautogui.PAUSE = 5
    pyautogui.press('tab')
    pyautogui.PAUSE = 5
    pyautogui.write(settings.TWSPASS)
    pyautogui.PAUSE = 5
    pyautogui.press('enter')
    print("Login complete")



