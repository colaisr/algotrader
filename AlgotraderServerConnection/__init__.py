import requests


def report_login_to_server(settings):
    r = requests.post(settings.SERVERURL + '/connections/logconnection',
                      json={"user": settings.SERVERUSER})
    status_code = r.status_code
    if status_code == 200:
        return r.text
