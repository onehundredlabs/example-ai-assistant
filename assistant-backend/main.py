from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from process_messages import receive_message
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "I am running 🚀"}


@app.post("/schedules")
async def schedules(message: Dict[str, str] = Body(...)):
    result = receive_message(message["text"])
    
    formatted_messages = []
    for message in result:
        if hasattr(message, "content") and message.content and (not hasattr(message, "type") or message.type != "tool"):
            formatted_messages.append({
                "content": message.content,
                "type": message.type if hasattr(message, "type") else "assistant"
            })
    
    return {"messages": formatted_messages}
