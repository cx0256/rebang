from fastapi import FastAPI, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/debug/login")
async def debug_login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Received form data:")
    print(f"  username: {form_data.username}")
    print(f"  password: {form_data.password}")
    print(f"  grant_type: {form_data.grant_type}")
    print(f"  scope: {form_data.scope}")
    print(f"  client_id: {form_data.client_id}")
    print(f"  client_secret: {form_data.client_secret}")
    
    return {
        "message": "Debug successful",
        "received_username": form_data.username,
        "received_password": form_data.password
    }

@app.post("/debug/login-raw")
async def debug_login_raw(
    username: str = Form(...),
    password: str = Form(...)
):
    print(f"Raw form data:")
    print(f"  username: {username}")
    print(f"  password: {password}")
    
    return {
        "message": "Raw debug successful",
        "received_username": username,
        "received_password": password
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)