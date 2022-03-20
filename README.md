# ystestassignmet

# Test Assignment

1. Install dependencies
    
  `python -m venv t-env`
  `source t-env/bin/activate`
  `pip install -r requirements.txt`

2. Run database in Docker
  
  `docker run --detach --name songs_db --publish 127.0.0.1:27017:27017 mongo:4.4`

3. Change cwd to project's directory root

4. Run linter and mypy
  
  `pylint songs/`
  `pyling tests/`
  `mypy songs/`

5. Run Unit tests from cwd

  `python -m pytest -s -v tests/unit`

6. Create config.env with content for test purposes:
  
  """FLASK_ENV=development
  MONGO_URI=mongodb://localhost:27017/songs_db"""

7. Upgrade database with index

  `python upgrade.py`

8. Run End-to-end tests from cwd

  `python -m pytest -s -v tests/e2e`

9. Run special populate test for data insertion

  `python -m pytest --populate tests/e2e/test_populate.py`

10. Run development server from `cwd` with

  `flask run`

11. Try app with http client
