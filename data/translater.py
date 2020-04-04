import requests, pprint


KEY = "trnsl.1.1.20200404T133725Z.a9a3679b94bbbfcb.298c50f77580453e4ea51a16df17f32d2d07d118"
URL_TRANSLATE = "https://translate.yandex.net/api/v1.5/tr.json/translate"


def translate(words):
    try:
        params = {
            "key": KEY,
            "text": words,
            "lang": "en",
            "format": "plain",
        }
        response = requests.get(URL_TRANSLATE, params=params).json()
        pprint.pprint(response)
        return response["text"][0]
    except Exception:
        return words
