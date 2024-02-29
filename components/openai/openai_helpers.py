import time


def submit_message(client, assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


def create_thread_and_run(client, user_input, assistant_id):
    thread = client.beta.threads.create()
    run = submit_message(client, assistant_id, thread, user_input)
    return thread, run


def get_response(client, thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="desc")


def wait_on_run(client, run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def pretty_print(messages):
    print("# Messages")
    for m in messages.data:
        print(f"{m.role}: {m.content[0].text.value}")
    print()