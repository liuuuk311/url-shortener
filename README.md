# URL Shortener Tool

This repository contains a simple URL shortener command-line application implemented in Python. The application provides two primary functions:

- **Minify:** Generate a shortened URL from a given complete URL.
- **Expand:** Retrieve the original URL from a shortened URL.

Shortened URLs have an expiration time, after which they become invalid. The mapping between original and shortened URLs is stored in a MongoDB database.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Running Locally](#running-locally)
  - [Running in Docker (with a user-defined network)](#running-in-docker-with-a-user-defined-network)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Assumptions and Design Decisions](#assumptions-and-design-decisions)
- [Notes](#notes)

---

## Features

- **Command-line interface:** Use flags `--minify` and `--expand` to perform URL shortening and expansion.
- **Expiration Handling:** Each shortened URL is valid for a configurable number of seconds (default: `3600` seconds).
- **MongoDB Integration:** Stores URL mappings using MongoDB.
- **Docker Ready:** Includes a Dockerfile for building the application image and instructions to run it in a Docker environment.
- **Automated Tests:** Unit tests implemented using `pytest`.

---

## Project Structure

```plaintext
.
├── Dockerfile
├── README.md
├── poetry.lock
├── pyproject.toml
├── tests
│   ├── __init__.py
│   └── test_services.py
└── url_shortner
    ├── __init__.py
    ├── database.py
    ├── services.py
    └── shortner.py
```

- **`url_shortner/`**: Contains the application code.
  - **`shortner.py`**: Main entry point for the command-line tool.
  - **`services.py`**: Contains business logic for minifying and expanding URLs.
  - **`database.py`**: Handles connecting to the MongoDB database.
- **`tests/`**: Contains unit tests for the services.
- **`Dockerfile`**: Docker configuration files for containerization.

---

## Requirements

- **Python 3.13**
- **Poetry** for dependency management.
- **MongoDB** (version 6.0 is recommended)
- **Docker** (if you plan to run the app in containers)
- **pytest** (for running tests)

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/liuuuk311/url-shortener.git
   cd url-shortener
   ```

2. **Install Dependencies Using Poetry:**

   Ensure you have Poetry installed. Then run:

   ```bash
   poetry install
   ```

---

## Usage

### Running Locally

Before running the application, set the required environment variables. You can create a `.env` file at the repository root:

```dotenv
MONGO_INITDB_DATABASE=shortener_db
MONGO_DATABASE=shortener_db
MONGO_URL=mongodb://mongo:27017/
```

Then, run the application with:

```bash
python url_shortner/shortner.py --minify "https://www.example.com/path?q=search"
```

or

```bash
python url_shortner/shortner.py --expand "http://short.url/YZUUrH"
```

### Running in Docker (with a user-defined network)

For this setup, you will run both MongoDB and the application on a user-defined network.

1. **Create a Docker Network:**

   ```bash
   docker network create mynetwork
   ```

2. **Run the MongoDB Container:**

   Assuming you have the `.env` file at the repository root, run:

   ```bash
   docker run -d \
     --name mongo \
     --network mynetwork \
     --env-file .env \
     -p 27017:27017 \
     mongo:6.0
   ```

3. **Build the Application Docker Image:**

   ```bash
   docker build -t url-shortener .
   ```

4. **Run the Application Container:**

   ```bash
   docker run --rm \
     --network mynetwork \
     --env-file .env \
     url-shortener --minify "https://www.example.com/path?q=search"
   ```

   The service should now be able to resolve `mongo` as the hostname to connect to your MongoDB container.

---

## Environment Variables

The application expects the following environment variables:

- **`MONGO_URL`**: MongoDB connection string.  
  Example: `mongodb://mongo:27017/`
- **`MONGO_DATABASE`**: Name of the database to use.  
  Example: `shortener_db`
- **`MONGO_INITDB_DATABASE`**: (Used by MongoDB container) Name of the initial database to create.  
  Example: `shortener_db`

You can specify these in a `.env` file and pass it to Docker using the `--env-file` flag.

---

## Testing

To run the tests, ensure you have installed the dependencies (via Poetry) and then run:

```bash
pytest tests
```

The tests use a MagicMock to simulate MongoDB interactions and cover both positive and negative cases for the minify and expand functionality.

---

## Assumptions and Design Decisions

- **Command-Line Focus:** The app is designed as a command-line tool to meet the challenge requirements.
- **Expiration Handling:** The shortened URLs expire after a configurable number of seconds, defaulting to 3600 seconds.
- **MongoDB Integration:** Uses MongoDB for storing URL mappings; service name resolution (e.g., `mongo`) is achieved through Docker networks.
- **Testing:** Unit tests are provided using pytest to ensure the core functionality works as expected.
- **Dockerization:** The application is fully containerized. Running the application in Docker requires connecting it to the same network as the MongoDB container for proper hostname resolution.

---

## Notes

- The project uses Poetry with `virtualenvs.create` disabled, so dependencies are installed globally inside the container.
- When running locally (outside Docker), ensure your MongoDB instance is accessible at the hostname specified in your environment variables.
---
