import requests
import dotenv
config = dotenv.dotenv_values('.env')
request_url = config['request_url']
token = config['token']
response = requests.post(request_url + "/login", headers={"Authorization": token}, json={'reason': 'Я делаю advanced версию'})
print(response.status_code, response.reason)
print(response.headers)
print(response.text)