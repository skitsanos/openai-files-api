import openai
from flask import current_app, make_response, request

from components.openai.openai_summarizer import OpenAIFileReferenceSummarizer

DEFAULT_MODEL = "gpt-4-0125-preview"


def handler(file_id: str):
    json_data = request.json

    user_input = json_data.get('user_input',
                               "Summarize the text from the given file") if json_data else "Summarize the text from the given file"
    instructions = json_data.get('instructions',
                                 "You are helpful assistant.") if json_data else "You are helpful assistant."
    model = json_data.get('model', current_app.config.get('openai', {}).get('model',
                                                                            DEFAULT_MODEL)) if json_data else DEFAULT_MODEL

    try:
        result = OpenAIFileReferenceSummarizer().run(
            file_ids=[file_id],
            model=model,
            user_input=user_input,
            instructions=instructions
        )
        return result["documents"]

    except openai.BadRequestError as openai_error:
        current_app.logger.error(f'OpenAI Error: {openai_error.body["message"]}')
        return make_response({"error": openai_error.body["message"]}, 400)

    except KeyError as e:
        current_app.logger.error(f'KeyError: {e["message"]}')
        return make_response({"error": "KeyError occurred"}, 400)
    except Exception as e:
        current_app.logger.error(f'An unexpected error occurred: {e["message"]}')
        return make_response({"error": "An unexpected error occurred"}, 500)
