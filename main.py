from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime, timedelta
import jwt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许的源列表
origins = [
    "http://localhost",
    "http://localhost:5500",  # 前端可能运行的地址
    "http://127.0.0.1:5500",  # 另一种本地地址格式
]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的源列表
    allow_credentials=True,
    allow_methods=["*"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的 HTTP 头部
)

# 秘钥和算法配置
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# 模拟一个存储校验码的数据库
fake_code_db = {"user": "123456"}  # 假设这是预存的校验码

class VerificationRequest(BaseModel):
    code: str

class ModifyRequest(BaseModel):
    new_data: dict
    token: str

# 校验码验证函数
def verify_code(verification_code: str):
    stored_code = fake_code_db.get("user")
    if stored_code != verification_code:
        raise HTTPException(status_code=401, detail="Invalid verification code")

# 生成 Token
def create_token():
    expiration = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
    return token

# 解密并验证 Token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/verify")
def verify_code_endpoint(request: VerificationRequest):
    verify_code(request.code)
    token = create_token()
    return {"message": "Verification successful", "token": token}

@app.post("/modify-data")
def modify_data(request: ModifyRequest):
    decode_token(request.token)
    # 此处执行数据修改的逻辑
    return {"message": "Data modified successfully", "new_data": request.new_data}

# 启动命令：uvicorn main:app --reload
