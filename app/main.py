import os

from fastapi import FastAPI

from app.routes import mount
from smart_home_common import configure_logging

configure_logging(service="security", level=os.environ.get("LOG_LEVEL", "INFO"))

app = FastAPI(title="Smart Home AI - Security Agent")
mount(app)
