from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings 


app = FastAPI(
	title=settings.APP_NAME,
	version=settings.APP_VERSION,
	description=settings.APP_DESCRIPTION,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/")
def read_root():
	return {"message": "Hello, World!"}

