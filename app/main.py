from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
	title="Sibol API",
	description="A backend API for Sibol.",
	version="1.0.0",
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

