To start project run: docker compose up --build

To run tests attach to web container and run: poetry run pytest app/tests/leads.py

There are 4 endpoints:
1. POST http://localhost/download-leads?start_date=2023-01-01&end_date=2023-01-31
2. GET http://localhost/tasks/{task_id}
3. GET http://localhost/leads/{task_id}?start_=1&end_=1000
4. DELETE http://localhost/leads/{task_id}

In file app/utils.py there are to variable to modify:
1. API_RECORDS_TO_RETURN: int = 5 (change to 20k like in task)
2. API_TIME_DELAY: float = 0.1 (change to 10 like in task)

