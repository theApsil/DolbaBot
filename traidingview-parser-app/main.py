import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import uvicorn
from services import browser_manager, settings
from db.course_handler import course_handler  # Импортируем хендлер

browser_thread = None
shutdown_event = threading.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global browser_thread, shutdown_event
    shutdown_event.clear()
    browser_thread = threading.Thread(
        target=browser_manager.run_browser,
        args=(shutdown_event,),
        daemon=True
    )
    browser_thread.start()

    yield

    # Shutdown
    shutdown_event.set()
    if browser_thread:
        browser_thread.join(timeout=5)
    browser_manager.cleanup()


app = FastAPI(lifespan=lifespan)


@app.get("/page")
def get_page():
    if browser_manager.driver is None:
        return JSONResponse(
            content={"status": "Browser is not running"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    try:
        return {"html": browser_manager.driver.page_source}
    except Exception as e:
        return JSONResponse(
            content={"status": f"Browser error: {str(e)}"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@app.get("/healthcheck")
def healthcheck():
    if browser_manager.is_ready:
        return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
    return JSONResponse(
        content={"status": "service unavailable"},
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@app.get("/last-course")
def get_last_course():
    """Получение последнего курса по ID через хендлер"""
    last_course = course_handler.get_last_course()  # Используем хендлер

    if not last_course:
        return JSONResponse(
            content={"status": "No courses found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return {
        "course": last_course.course,
        "time": last_course.date.isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)