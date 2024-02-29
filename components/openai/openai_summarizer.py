import logging
import os
from typing import Dict, Any, Iterable

from haystack import component, Document
from openai import OpenAI
from openai._types import NotGiven, NOT_GIVEN
from openai.types.beta import assistant_create_params

from components.openai.openai_helpers import create_thread_and_run, wait_on_run, get_response

client = OpenAI()

# https://platform.openai.com/docs/models
DEFAULT_MODEL = "gpt-4-0125-preview"


def summarize_text(text_to_summarize: str,
                   model: str = DEFAULT_MODEL,
                   system_instructions: str = "You are a helpful assistant. You are asked to summarize the text.",
                   **kwargs):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_instructions
            },
            {
                "role": "user",
                "content": text_to_summarize
            }
        ],
        **kwargs
    )
    return response.choices[0].message.content.strip()


@component
class OpenAITextSummarizer:
    @component.output_types(text=str, **{})
    def run(self, text: str, model=DEFAULT_MODEL, **kwargs: Any) -> Dict[str, Any]:
        return {"text": summarize_text(text_to_summarize=text, model=model, **kwargs)}


@component
class OpenAIDocumentSummarizer:
    @component.output_types(documents=list[Document], **{})
    def run(self, documents: list[Document], model: str = DEFAULT_MODEL, **kwargs: Any) -> Dict[str, Any]:
        summaries: list[Document] = []

        for doc in documents:
            summary = summarize_text(text_to_summarize=doc.content, model=model, **kwargs)
            summaries.append(Document(content=summary))
        return {"documents": summaries}


@component
class OpenAIFileSummarizer:
    @component.output_types(documents=list[Document], **{})
    def run(self,
            path: str,
            model: str = DEFAULT_MODEL,
            user_input: str = "Summarize the text from the given file",
            instructions="You are helpful assistant.",
            tools: Iterable[assistant_create_params.Tool] | NotGiven = NOT_GIVEN,
            metadata: dict[str, Any] = None,
            **kwargs: Any) -> \
            Dict[str, Any]:
        summaries: list[Document] = []

        openai_client = OpenAI()

        logging.info(f"Summarizing the file: {os.path.basename(path)}")

        assistant_file = openai_client.files.create(file=open(path, "rb"), purpose="assistants")

        logging.info(f"File uploaded: {assistant_file.id}")

        assistant_tools = tools if tools is not NOT_GIVEN else [{"type": "retrieval"}]

        assistant = openai_client.beta.assistants.create(
            instructions=instructions,
            model=model,
            tools=assistant_tools,
            file_ids=[assistant_file.id]
        )

        logging.info(f"Assistant created: {assistant.id}")

        logging.info(f"User input: {user_input}")

        thread, run = create_thread_and_run(
            openai_client,
            user_input,
            assistant.id
        )

        logging.info(f"Thread created: {thread.id}")

        run = wait_on_run(openai_client, run, thread)

        logging.info(f"Gathering the response from the assistant: {run.id}")

        messages = get_response(openai_client, thread)

        for m in messages.data:
            if m.role == "assistant":
                doc = Document(content=m.content[0].text.value,
                               meta={
                                   "source": os.path.basename(path),
                                   "type": "summary",
                                   "model": model
                               })

                # if it has 'metadata', merge it with the meta
                if metadata is not None:
                    doc.meta.update(metadata)

                summaries.append(doc)

        logging.info(f"Assistant response gathered")

        # drop the assistant
        openai_client.beta.assistants.delete(assistant.id)

        openai_client.files.delete(assistant_file.id)

        return {"documents": summaries}


@component
class OpenAIFileReferenceSummarizer:
    @component.output_types(documents=list[Document], **{})
    def run(self,
            file_ids: list[str],
            model: str = DEFAULT_MODEL,
            user_input: str = "Summarize the text from the given file",
            instructions="You are helpful assistant.",
            tools: Iterable[assistant_create_params.Tool] | NotGiven = NOT_GIVEN,
            metadata: dict[str, Any] = None,
            **kwargs: Any) -> \
            Dict[str, Any]:
        summaries: list[Document] = []

        openai_client = OpenAI()

        logging.info(f"Summarizing the files: {file_ids}")

        assistant_tools = tools if tools is not NOT_GIVEN else [{"type": "retrieval"}]

        assistant = openai_client.beta.assistants.create(
            instructions=instructions,
            model=model,
            tools=assistant_tools,
            file_ids=file_ids
        )

        logging.info(f"Assistant created: {assistant.id}")

        logging.info(f"User input: {user_input}")

        thread, run = create_thread_and_run(
            openai_client,
            user_input,
            assistant.id
        )

        logging.info(f"Thread created: {thread.id}")

        run = wait_on_run(openai_client, run, thread)

        logging.info(f"Gathering the response from the assistant: {run.id}")

        messages = get_response(openai_client, thread)

        for m in messages.data:
            if m.role == "assistant":
                doc = Document(content=m.content[0].text.value,
                               meta={
                                   "sources": file_ids,
                                   "type": "summary",
                                   "model": model
                               })

                # if it has 'metadata', merge it with the meta
                if metadata is not None:
                    doc.meta.update(metadata)

                summaries.append(doc)

        logging.info(f"Assistant response gathered")

        # drop the assistant
        openai_client.beta.assistants.delete(assistant.id)

        return {"documents": summaries}
