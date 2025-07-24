# Sibol API

A back-end of Sibol.

## Requirements

- [Python 3](https://www.python.org/downloads)
- [PostgreSQL](https://www.postgresql.org/download) (optional)
- [Git](https://git-scm.com/downloads)

## Getting Started

Follow the following steps to setup the project.

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

2. Activate the virtual environment:

   ```bash
   # Windows
   .\venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. Install all packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Get the `.env` file from the admin, and paste inside the root directory.

5. Run the project:

   ```bash
   uvicorn app.main:app
   ```

6. Open your browser and go to `http://localhost:8000/docs` to access the API documentation.

## License

This project is licensed under the terms described in the [LICENSE](./LICENSE) file.
