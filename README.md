# Document Reader (FastAPI)

[![Build Status](https://github.com/michael7nightingale/Document-TTS-Reader-FastAPI/actions/workflows/fastapi-app.yml/badge.svg)](https://github.com/michael7nightingale/Document-TTS-Reader-FastAPI/actions/workflows/fastapi-app.yml/)
[![Build Status](https://github.com/michael7nightingale/Document-TTS-Reader-FastAPI/actions/workflows/codeql.yml/badge.svg)](https://github.com/michael7nightingale/Document-TTS-Reader-FastAPI/actions/workflows/codeql.yml/)
[![Build Status](https://github.com/michael7nightingale/Document-TTS-Reader-FastAPI/actions/workflows/docker-image.yml/badge.svg)](https://github.com/michael7nightingale/Document-TTS-Reader-FastAPI/actions/workflows/docker-image.yml/)

Here is FastAPI RESTful API with MongoDB database for managing documents (.pdf, .doc, etc.). There is CRUD for documents with main doc file and covert image uploading.
You can get test from current page or document at all. Also, you can request current page TTS audio, which will be your response )).  

*NOTE*: .git root is project root;

## Stack
- `Python 3.11`;
- `FastAPI`;
- `MongoDB`;
- `fastapi_authtools` (my authentication library);
- `gtts` text-to-speach library;
- `langdetect` for managing for managing pdf files;
- `Pydantic 2.0`;
- `Motor` database library;
- `Docker`;
- `pytest` in async mode for testing;
- `flake8` linter;

## Requirements
I use `Python 3.11` as the project language.
The environment variables seem to be nice, but you can change it with ones you need
(.dev.env for developing, .docker.env for running application in Docker, .test.env for testing).  

You can install application requirements with:
```commandline
pip install -r requirements.txt
```

## Tests and linters
First install development requirements with:
```commandline
pip install -r dev-requirements.txt
```

To run flake8 linter:
```commandline
flake8
```

To run tests:
```commandline
export MONGODB_VERSION=6.0-ubi8
docker run --name mongodb -d mongodb/mongodb-community-server:$MONGODB_VERSION
pytest
```

or write this for more information:
```commandline
pytest -s -vv
```


## Running application
You can run it using `Docker`. Run this command in the project root directory.
The server is default running at `localhost:8000`.

```commandline
docker-compose up -d --build
```

For local running using `uvicorn` run:
```commandline
export MONGODB_VERSION=6.0-ubi8
docker run --name mongodb -d mongodb/mongodb-community-server:$MONGODB_VERSION
uvicorn app.main:create_app --reload --port 8000
```
