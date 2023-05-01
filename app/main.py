from datetime import date, datetime, timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, status, BackgroundTasks, Path, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models import models
from app.schemas import schemas
from app.db.base import get_db, engine
from app.utils import start_downloading_leads


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/download-leads/")
def download_leads(
        background_tasks: BackgroundTasks,
        start_date: date = datetime.utcnow().date(),
        end_date: date = datetime.utcnow().date() + timedelta(days=1),
        db: Session = Depends(get_db)
):
    # Create task
    task_db = models.Task(start_date=start_date, end_date=end_date)
    db.add(task_db)
    db.commit()

    # Start downloading on backgroud
    background_tasks.add_task(
        start_downloading_leads,
        task_id=task_db.id,
        start_date=start_date,
        end_date=end_date
    )

    return JSONResponse(
        content={"task_id": task_db.id},
        status_code=status.HTTP_202_ACCEPTED
    )


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def task_status(
        task_id: Annotated[int, Path(gt=0)],
        db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter_by(id=task_id).one_or_none()

    if task is None:
        return JSONResponse(content={"error": "Item not found"}, status_code=404)

    task_response = schemas.TaskResponse(
        status=task.status,
        args={"start_date": task.start_date, "end_date": task.end_date}
    )

    return task_response


@app.get("/leads/{task_id}", response_model=list[schemas.Lead])
def get_leads(
        task_id: Annotated[int, Path(gt=0)],
        start_: Annotated[int, Query(gt=0)],
        end_: Annotated[int, Query(gt=1, lt=1000)],
        response: Response,
        db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter_by(id=task_id).one_or_none()

    if task is None:
        return JSONResponse(content={"error": "Task not found"}, status_code=404)

    if task.status != "SUCCESFULL":
        return JSONResponse(
            content={"status": task.status},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    query = db.query(
        models.User.id, models.User.created_at, models.User.full_name,
        models.User.email, models.Country.country_id).\
        join(models.Country).\
        filter(models.User.task_id == task_id)

    total_count = query.count()
    records = query.slice(start_ - 1, end_)

    response_data = []
    for row in records:
        response_data.append(schemas.Lead(**dict(zip(row._fields, row))))

    response.headers["X-Total-Count"] = str(total_count)

    return response_data


@app.delete("/leads/{task_id}")
def delete_task(
        task_id: Annotated[int, Path(gt=0)],
        db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter_by(id=task_id).one_or_none()

    if task is None:
        return JSONResponse(content={"error": "Task not found"}, status_code=404)

    db.delete(task)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
