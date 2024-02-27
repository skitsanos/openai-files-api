from openai import OpenAI
from flask import current_app, make_response

client = OpenAI()


def handler(file_id: str):
    try:
        file_details = client.files.retrieve(file_id)
        return file_details.dict()
    except Exception as e:
        current_app.logger.error(f'{e.body["message"]}')

        return make_response({
            "error": e.body["message"]
        }, 400)
