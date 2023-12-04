from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import csv

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"  
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
def shutdown():
    pass

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile = File(...), name_col: int = Form(...), age_col: int = Form(...)):
    contents = await file.read()
    decoded_content = contents.decode('utf-8').splitlines()

    csv_reader = csv.reader(decoded_content)
    headers = next(csv_reader)

    name_index, age_index = name_col, age_col

    for row in csv_reader:
        name = row[name_index]
        age = int(row[age_index])
        db_user = User(name=name, age=age)
        db = SessionLocal()
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()

    return {"file_info": file.filename, "headers": headers}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
