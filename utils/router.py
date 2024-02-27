import os
import re

from flask import request, jsonify, make_response


def validate_token(secret_key: str):
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return make_response({'error': {"message": "Token is missing or invalid"}}, 401)

    # Extract the token from the header
    token = token.split(' ')[1]

    # Here you'd typically verify and decode the token using your preferred method,
    # such as JWT decoding and verification.
    # For demonstration purposes, let's assume simple verification with a secret key.
    if token != secret_key:
        return make_response({'message': 'Token is invalid'}, 401)


def convert_to_url_params(input_string: str):
    """
    Convert a string to a Flask-style URL parameter
    :param input_string:
    :return:
    """
    pattern = r'\$([a-zA-Z0-9_]+)'
    result = re.sub(pattern, r'<\1>', input_string)
    return result


def load_routes(app, path):
    """
    Load routes from a directory
    :param app:
    :param path:
    :return:
    """
    for root, dirs, files in os.walk(path, followlinks=False):
        for found_dir in dirs:
            entry_point = os.path.join(root, found_dir)
            route_path = os.path.relpath(path=entry_point, start=path).replace("\\", "/")
            module_path = os.path.relpath(entry_point, path)

            methods = []
            for method in ("get", "post", "put", "delete", "options", "head", "patch"):
                if os.path.exists(os.path.join(root, found_dir, f"{method}.py")):
                    params_formatted_path = convert_to_url_params(str(route_path))
                    methods.append(method.upper())
                    module_name = f"routes.{module_path.replace(os.sep, '.')}.{method}"

                    app.logger.info(f'Route: {method.upper()} /{params_formatted_path} ({module_name})')

                    module = __import__(module_name, fromlist=["*"])
                    app.add_url_rule(f"/{params_formatted_path}",
                                     view_func=module.handler,
                                     endpoint=module_name,
                                     methods=[method.upper()]
                                     )
                # break
