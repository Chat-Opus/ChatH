import json
import time
import uuid

from fastapi import FastAPI, Request

app = FastAPI()
MODEL = "local-hle-judge"


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{"id": MODEL, "object": "model", "owned_by": "local"}],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()

    # TEST-ONLY mock: this deliberately does not evaluate the answer.
    result = {
        "extracted_final_answer": "MOCK",
        "reasoning": "Mock Judge response; no correctness evaluation was performed.",
        "correct": "yes",
        "confidence": 100,
        "strict": True,
    }

    return {
        "id": "chatcmpl-" + uuid.uuid4().hex,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model", MODEL),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(result),
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
