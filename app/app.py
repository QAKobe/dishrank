from fastapi import FastAPI

app = FastAPI(title="DishRank MVP")

@app.get("/")
def home():
    return {"message": "Hello from DishRank!"}
