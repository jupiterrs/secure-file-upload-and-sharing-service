import os
from datetime import datetime

from fastapi import (
    Path,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
    Request,
    Body,
    APIRouter,
    Form,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from app.auth import authenticate_user, create_access_token, get_current_user
from app.db import add_user, files_collection, users
from app.models import FileMetadata, User, VisibilityToggleRequest

app = FastAPI()
router = APIRouter()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_login_register(request: Request):
    with open("frontend/login_register.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    with open("frontend/dashboard.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.post("/register")
async def register(user: User):
    success = await add_user(user)

    if not success:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"msg": "User registered successfully"}


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await authenticate_user(form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user["username"]})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    is_public: bool = Form(False),
    user: dict = Depends(get_current_user),
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    metadata = FileMetadata(
        filename=file.filename,
        content_type=file.content_type,
        size=os.path.getsize(file_location),
        upload_time=datetime.utcnow(),
        username=user["username"],
        is_public=is_public,
    )

    await files_collection.insert_one(metadata.dict())
    return {"filename": file.filename}


@app.get("/files/{filename}")
async def get_file(
    filename: str, user: dict = Depends(get_current_user, use_cache=False)
):
    file_doc = await files_collection.find_one({"filename": filename})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    if not file_doc.get("is_public", False):
        if not user or (
            user["username"] != file_doc["username"]
            and user["username"] not in file_doc.get("shared_with", [])
        ):
            raise HTTPException(status_code=403, detail="Unauthorized access")

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(file_path)


@app.delete("/files/{filename}")
async def delete_file_route(
    filename: str = Path(..., description="Type the file you want to delete"),
    user: dict = Depends(get_current_user),
):
    file_path = os.path.join(UPLOAD_DIR, filename)

    metadata = await files_collection.find_one(
        {"filename": filename, "username": user["username"]}
    )

    if not metadata:
        raise HTTPException(
            status_code=403, detail="Unauthhorized access, type in your file name"
        )

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    files_collection.delete_one({"filename": filename})
    return {"detail": "File deleted"}


@app.get("/files")
async def search_files(
    name: str = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None),
    content_type: str = Query(None),
    user: dict = Depends(get_current_user),
):
    query = {"$or": [{"username": user["username"]}, {"shared_with": user["username"]}]}
    if name:
        query["filename"] = {"$regex": name, "$options": "i"}

    if content_type:
        query["content_type"] = content_type

    if from_date and to_date:
        try:
            query["upload_time"] = {
                "$gte": datetime.fromisoformat(from_date),
                "$lte": datetime.fromisoformat(to_date),
            }
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS",
            )

    results = await files_collection.find(query, {"_id": 0}).to_list(length=100)
    return results


@app.post("/files/share")
async def share_file(
    filename: str = Body(...),
    share_with_username: str = Body(...),
    user: dict = Depends(get_current_user),
):
    file_doc = await files_collection.find_one(
        {"filename": filename, "username": user["username"]}
    )
    if not file_doc:
        raise HTTPException(
            status_code=404, detail="File not found or not owned by you"
        )

    share_user = await users.find_one({"username": share_with_username})
    if not share_user:
        raise HTTPException(status_code=404, detail="User to share with not found")

    if share_with_username not in file_doc.get("shared_with", []):
        await files_collection.update_one(
            {"filename": filename, "username": user["username"]},
            {"$push": {"shared_with": share_with_username}},
        )

    return {"detail": f"File '{filename}' shared with '{share_with_username}'"}


@router.get("/public-files")
async def get_public_files():
    public_files = await files_collection.find({"is_public": True}, {"_id": 0}).to_list(
        length=100
    )
    return public_files


@app.post("/files/toggle-visibility")
async def toggle_visibility(
    payload: VisibilityToggleRequest,
    user: dict = Depends(get_current_user),
):
    file_doc = await files_collection.find_one(
        {"filename": payload.filename, "username": user["username"]}
    )
    if not file_doc:
        raise HTTPException(
            status_code=404, detail="File not found or not owned by user"
        )

    await files_collection.update_one(
        {"filename": payload.filename, "username": user["username"]},
        {"$set": {"is_public": payload.make_public}},
    )

    return {
        "detail": f"File visibility updated to {'public' if payload.make_public else 'private'}."
    }


app.include_router(router)
