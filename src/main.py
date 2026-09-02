from fastapi import FastAPI
from services.gemini import ask_gemini
from database.db_operator import create_user, get_user, login


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello"}


@app.post("/ask")
async def ask(prompt: str):
	return await ask_gemini(prompt)


@app.post("/users")
def register(username:str, email:str, password:str):
    create_user(username, email, password)
    return {"message": "User created successfully"}


@app.get("/users/{user_id}")
def user_info(user_id: int):
    return get_user(user_id)


@app.post("/login")
def sign_in(email:str, password: str):
    user_id =  login(email, password)

    if user_id is None:
        return {"success": False}

    return {
		"success": True,
		"user_id": user_id
	}
