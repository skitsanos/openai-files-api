from openai import OpenAI
from flask import current_app, make_response

client = OpenAI()


def handler(file_id: str):
    """
    Returns the contents of the specified file.
    :param file_id:
    :return:
    """
    try:
        content = client.files.retrieve_content(file_id)
        return {content}
    except Exception as e:
        current_app.logger.error(f'{e.body["message"]}')

        return make_response({
            "error": e.body["message"]
        }, 400)
