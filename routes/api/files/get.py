from openai import OpenAI
from flask import current_app, make_response

client = OpenAI()


def handler():
    try:
        return client.files.list().dict()
    except Exception as e:
        current_app.logger.error(f'{e.body["message"]}')

        return make_response({
            "error": e.body["message"]
        }, 400)
