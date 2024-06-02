from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import httpx
from typing import List
import aiohttp

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(HTTP_429_TOO_MANY_REQUESTS, _rate_limit_exceeded_handler)

# Claim process service URL
CLAIM_PROCESS_URL = "http://claim_process:8000"

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Welcome to the API gateway!"}

@app.post("/claims/")
@limiter.limit("10/minute")
async def process_claims(request: Request, file: UploadFile = File(...)):
    file_content = await file.read()  # Read the file content as bytes
    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        form.add_field('file',
                       file_content,
                       filename=file.filename,
                       content_type=file.content_type)

        async with session.post(f"{CLAIM_PROCESS_URL}/claims/", data=form) as response:
            response_text = await response.text()
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=response_text)
            return JSONResponse(content=response_text, status_code=response.status)

@app.get("/providers/top10")
@limiter.limit("10/minute")
async def read_top_10_providers(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CLAIM_PROCESS_URL}/providers/top10")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return JSONResponse(content=response.json(), status_code=response.status_code)

@app.post("/claims/individual")
@limiter.limit("10/minute")
async def create_individual_claim(request: Request, claim: dict):
    async with httpx.AsyncClient() as client:
        headers = {"Content-Type": "application/json"}
        response = await client.post(f"{CLAIM_PROCESS_URL}/claims/individual", headers=headers, json=claim)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return JSONResponse(content=response.json(), status_code=response.status_code)
