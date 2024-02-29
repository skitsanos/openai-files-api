# openai-files-api

This is a simple API to upload files into and interact with files from OpenAI's GPT engine.
The API is built using Flask and uses the OpenAI Python library to interact with the OpenAI API.

Most of the tasks are automated via Taskfile used by [Task](https://taskfile.dev/) - a task runner / build tool that
aims to be simpler and easier to use than, for example, GNU Make.

## Installation

1. Clone the repository using `git clone` or download the repository as a zip file and extract it
2. Install support for the Taskfile, details can be found [here](https://taskfile.dev/#/installation)
3. Install the required packages using `pip install -r requirements.txt` or run `task install`
4. Modify environment variables in the `Taskfile.yaml` file

- `OPENAI_API_KEY` - Your OpenAI API key
- `AUTH_TOKEN` - The token to be used for authentication

## Configuration

The configuration file is located at `config.yaml` and contains the following options:

```yaml
server:
  bind: 0.0.0.0
  port: 5000
  uploads: .uploads

cors:
  origins: "*"
  methods: [ "GET", "POST", "DELETE" ]
  allow_headers: [ "Content-Type", "Authorization" ]

openai:
  model: gpt-4-turbo-preview
```

- `server` - The server configuration section
    - `bind` - The IP address to bind the server to
    - `port` - The port to bind the server to
    - `uploads` - The directory to store the uploaded files
- `cors` - The CORS configuration section, used to configure the CORS policy for the server
    - `origins` - The allowed origins
    - `methods` - The allowed methods
    - `allow_headers` - The allowed headers
- `openai` - The OpenAI configuration section
    - `model` - The model to use for the OpenAI API

You can also override `bind` and `port` using environment variables `BIND` and `PORT` respectively. Environment
variables have higher priority than the configuration file.

## Usage

To start the server, run `task start`. The server will start on the IP address and port specified in the configuration.

To stop the server, press `Ctrl+C` in the terminal.

## Generating Systemd Service File

To generate a systemd service file, run `task generate-unit-file`. The service file will be generated in the current
directory. The name of the service file will be `openai-files-api.service` and can be overridden using
the `DEPLOYMENT_SERVICE_NAME` variable in Taskfile.yaml.

## Deploying the Server

To deploy the server, run `task deploy-to-remote`. This will generate a systemd service file and copy it to
the `/etc/systemd/system` on remote machine. The service will be enabled and started. During deployment Task will copy
the `config.yaml`, code and `Taskfile.yaml` to the remote machine.

To deploy to the remote machine, you need to modify the `DEPLOYMENT_ENDPOINT` and `DEPLOYMENT_USERNAME` variables in
the `Taskfile.yaml` file.

You can also build a Docker image using `task docker-build`. You can override the image name using the `DOCKER_TAG`
variable.

## API Endpoints

The API has the following endpoints:

- `GET /api` - The root endpoint, returns a welcome message in JSON format
- `POST /api/files` - Upload a file to the server
- `GET /api/files` - List all the files on the server
- `GET /api/files/<file_id>` - Get the details of a file
- `GET /api/files/<file_id>/summarize` - Summarize the file using the OpenAI API
- `DELETE /api/files/<file_id>` - Delete the file from the server

> For the supported file types and the request and response formats, please refer to the OpenAPI documentation at
https://platform.openai.com/docs/assistants/tools/supported-files.
