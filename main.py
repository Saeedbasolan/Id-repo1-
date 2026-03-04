from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    employee_id = Column(String)
    password = Column(String)

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer)
    employee_id = Column(String)
    date = Column(Date)
    commodity_rs = Column(Float)
    tvas = Column(String)
    safe_pay = Column(String)
    ew = Column(String)

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>SB EMI Tracker</h2>
    <a href='/signup'>Company Signup</a>
    """

@app.get("/signup", response_class=HTMLResponse)
def signup_form():
    return """
    <form method='post'>
    Company Name: <input name='company_name'><br>
    Email: <input name='email'><br>
    Password: <input name='password' type='password'><br>
    <button type='submit'>Signup</button>
    </form>
    """

@app.post("/signup")
def signup(company_name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    hashed = pwd_context.hash(password)
    new_company = Company(company_name=company_name, email=email, password=hashed)
    db.add(new_company)
    db.commit()
    return RedirectResponse("/", status_code=303)
