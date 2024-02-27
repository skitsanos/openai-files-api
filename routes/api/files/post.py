import os
from uuid import uuid4

from flask import request, make_response, g, current_app
from openai import OpenAI

client = OpenAI()


def handler():
    if 'file' not in request.files:
        current_app.logger.error('No file uploaded.')

        return make_response(
            {
                "error":
                    {
                        "message": 'No file uploaded.'}
            },
            400
        )

    purpose = request.form.get('purpose')
    # throw an error if the purpose is not provided
    if purpose is None:
        return make_response(
            {
                "error":
                    {
                        "message": 'Purpose is required. '
                                   'Use "fine-tune" for Fine-tuning and "assistants" for Assistants and Messages.'
                    }
            },
            400
        )

    uuid = str(uuid4())

    upload_dir = g.app.config['server']['uploads'] or os.path.join('uploads')
    # Create the directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)

    uuid_path = os.path.join(upload_dir, uuid)
    if not os.path.exists(uuid_path):
        os.makedirs(uuid_path)

    files_uplodaded = []

    for file in request.files.getlist('file'):
        path_to_file = os.path.join(uuid_path, file.filename)

        if os.access(uuid_path, os.W_OK):
            file.save(path_to_file)

            try:
                file_details = client.files.create(file=open(path_to_file, "rb"), purpose=purpose)

                # remove the file after it has been uploaded
                os.remove(path_to_file)

                files_uplodaded.append(file_details.dict())
            except Exception as e:
                current_app.logger.error(f'{e.body["message"]}')

                return make_response({
                    "error": e.body["message"]
                }, 400)
        else:
            return make_response(
                {
                    "error":
                        {
                            "message": 'Permission denied to write to the directory.'
                        }
                },
                500
            )

    # remove the directory after all files have been uploaded
    os.rmdir(uuid_path)

    return files_uplodaded
