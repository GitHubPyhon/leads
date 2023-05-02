import time
import pytest
from datetime import datetime

from sqlalchemy.sql import text
from fastapi.testclient import TestClient
from app.main import app
from app import utils
from app.db.base import SessionLocal


client = TestClient(app)


def create_task(start_date: str, end_date: str):
    db = SessionLocal()
    try:
        result = db.execute(text(
            f"""
                insert into tasks (start_date, end_date, status)
                values ('{start_date}', '{end_date}', 'CREATED')
                RETURNING id
            """
        ))
        db.commit()
        task_id = result.fetchone()[0]
        return task_id
    finally:
        db.close()


@pytest.fixture(scope="class")
def task_id():
    return create_task("2023-01-01", "2023-01-01")


class TestDownloadLeads:

    def test_start_date_gt_end_date(self):
        response = client.post("/download-leads/?start_date=2023-05-04&end_date=2023-05-03")
        assert response.status_code == 400
        assert response.text == "start_date > end_date"

    def test_create_task(self):
        response = client.post("/download-leads/?start_date=2023-01-01&end_date=2023-01-02")
        assert response.status_code == 202
        assert isinstance(response.json().get("task_id"), int)


class TestTaskStatus:

    def test_task_not_found(self, task_id):
        response = client.get(f"/tasks/{task_id + 1}")
        assert response.status_code == 404
        assert response.text == "Task not found"

    def test_task_status(self, task_id):
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json().get("status") == "CREATED"


class TestGetLeads:

    def test_get_leads_task_not_found(self, task_id):
        response = client.get(f"/leads/{task_id + 1}?start_=1&end_=5")
        assert response.status_code == 404
        assert response.text == "Task not found"

    def test_get_lead_task_not_succesfull(self, task_id):
        response = client.get(f"/leads/{task_id}?start_=1&end_=5")
        assert response.status_code == 500

    @pytest.mark.parametrize(
        "day_count, start_date, end_date",
        [
            # One day
            (1, "2023-01-01", "2023-01-01"),
            # Two days for testing paginations
            (2, "2023-01-01", "2023-01-02"),
        ]
    )
    def test_get_leads(self, day_count, start_date, end_date):
        task_id = create_task(start_date, end_date)
        utils.start_downloading_leads(
            task_id,
            datetime.strptime(start_date, "%Y-%m-%d"),
            datetime.strptime(end_date, "%Y-%m-%d"),
        )

        # wait until received(created) from remote API
        time.sleep(utils.API_TIME_DELAY * day_count)

        total_count = day_count * utils.API_RECORDS_TO_RETURN

        if total_count % utils.API_RECORDS_TO_RETURN:
            pages = total_count // utils.API_RECORDS_TO_RETURN + 1
        else:
            pages = total_count // utils.API_RECORDS_TO_RETURN

        start_, end_ = 1, utils.API_RECORDS_TO_RETURN
        for i in range(pages):
            response = client.get(f"/leads/{task_id}?start_={start_}&end_={end_}")
            assert response.status_code == 200
            assert int(response.headers["X-Total-Count"]) == total_count
            assert len(response.json()) == utils.API_RECORDS_TO_RETURN
            start_, end_ = end_ + 1, end_ + utils.API_RECORDS_TO_RETURN

            # TODO: validate returned value "created_at"
            # it must be start_day <= "created_at" <= end_date


class TestDeleteTask:

    def test_task_delete_not_found(self, task_id):
        response = client.delete(f"/leads/{task_id + 1}")
        assert response.status_code == 404
        assert response.text == "Task not found"

    def test_task_delete(self, task_id):
        response = client.delete(f"/leads/{task_id}")
        assert response.status_code == 204
