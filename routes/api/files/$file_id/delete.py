from openai import OpenAI
from flask import current_app, make_response

client = OpenAI()


def handler(file_id: str):
    """
    Delete a file from the OpenAI API
    :param file_id:
    :return:
    """
    try:
        result = client.files.delete(file_id)
        return result.dict()
    except Exception as e:
        current_app.logger.error(f'{e.body["message"]}')

        return make_response({
            "error": e.body["message"]
        }, 400)
