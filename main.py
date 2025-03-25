from fastapi import FastAPI, Request
from logic import civilID
import uvicorn
app = FastAPI()

@app.post("/residency_permit")
async def process_image(request: Request):
    return await civilID.process_upload_file(request)

# if __name__ == "__main__":
#     uvicorn.run(app, host="localhost", port=8999)
