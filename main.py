# from fastapi import FastAPI

# # 1. Create the App
# app = FastAPI()

# # 2. Create a "Route"
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Attendance App Kitchen!"}

## 2 times
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from datetime import datetime

# app = FastAPI()

# # --- THE DATABASE (Temporary) ---
# # We use a simple list for now. If you restart the server, this data disappears.
# # We will replace this with SQLite in the next phase.
# fake_db = []

# # --- THE MODEL (The Bouncer) ---
# # This defines strict rules for data sent to us.
# class CheckIn(BaseModel):
#     id: int
#     name: str
#     # 'location' is optional, but if provided, must be a string
#     location: str = "Office" 

# # --- ROUTES ---

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to Smart Attendance API"}

# # GET route to see all check-ins
# @app.get("/checkins")
# def get_checkins():
#     return fake_db

# # POST route to create a NEW check-in
# @app.post("/checkin")
# def create_checkin(log: CheckIn):
#     # 1. Add a timestamp (Server side logic)
#     entry = log.dict()
#     entry['time'] = datetime.now()
    
#     # 2. Save to our fake database
#     fake_db.append(entry)
    
#     # 3. Return success message
#     return {"message": "Check-in successful", "data": entry}

from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime

# 1. SETUP THE DATABASE
# This tells the code to create a file named 'database.db'
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# The Engine is responsible for the connection to the file
engine = create_engine(sqlite_url)

# 2. DEFINE THE TABLE (The Shelf)
# table=True means "Create a real table in the database for this"
class CheckIn(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    location: str
    time: datetime = Field(default_factory=datetime.now)

# 3. CREATE THE APP
app = FastAPI()

# This runs when the server starts to ensure the file/table exists
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# 4. ROUTES

@app.post("/checkin")
def create_checkin(log: CheckIn):
    # Open a session (a temporary workspace)
    with Session(engine) as session:
        session.add(log)      # Add the new data to the workspace
        session.commit()      # Save changes permanently to the file
        session.refresh(log)  # Refresh data (to get the generated ID)
        return log

@app.get("/checkins")
def get_checkins():
    with Session(engine) as session:
        # distinct "select" command: "Select all objects from the CheckIn table"
        statement = select(CheckIn)
        results = session.exec(statement).all()
        return results