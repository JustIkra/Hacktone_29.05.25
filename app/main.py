from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SERVICES = {
    "user": "http://user-service:8001",
    "auth": "http://auth-service:8002",
    "service": "http://service-manager:8003",
    "report": "http://reporting-service:8004"
}

async def verify_token(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['auth']}/verify",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        return response.json()

@app.get("/{service_name}/{path:path}")
async def route_request(
    service_name: str,
    path: str,
    token_data: dict = Depends(verify_token),
    params: dict = {}
):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Проверка прав доступа к сервису
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['service']}/check-access",
            json={
                "user_id": token_data["user_id"],
                "service": service_name
            }
        )
        if not response.json().get("has_access"):
            raise HTTPException(status_code=403, detail="Access denied")
    
    async with httpx.AsyncClient() as client:
        service_url = f"{SERVICES[service_name]}/{path}"
        response = await client.get(service_url, params=params)
        return response.json()
