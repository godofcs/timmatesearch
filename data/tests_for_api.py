from requests import get, post, delete

print(get("/api/v2/forum/1").json())  # Корректный запрос get
print(get("/api/v2/forum/YandexLyceum").json())  # Не корректный запрос get
# Корректный post запрос
print(post('/api/v2/forum',
           json={"title": "Как написать сайт на python?",
                 "question": "не получается написать сайт на python, помогите!",
                 "theme": "Python",
                 "answers": "",
                 "user_id": ""}).json())
# Не корректный post запрос, ошибка запроса заключается в том, что в answers и users_id должна
# передаваться строка, а в запросе переданы числа!
print(post('/api/v2/forum',
           json={"title": "Как написать сайт на python?",
                 "question": "не получается написать сайт на python, помогите!",
                 "theme": "Python",
                 "answers": 3,
                 "user_id": 3}).json())
print(delete('/api/v2/forum/1').json())  # Корректный запрос
print(delete('/api/v2/forum/YandexLyceum').json())  # Некорректный запрос
