from openai import OpenAI

client = OpenAI()


def handler():
    return client.files.list().dict()
