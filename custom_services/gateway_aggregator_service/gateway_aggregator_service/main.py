from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://0.0.0.0:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def handle(request: Request):
    print(request)
    return {"message": "I am root"}

@app.get("/api/v1/")
async def handle_api(request: Request):
    print(request)
    return {"message": "received"}

