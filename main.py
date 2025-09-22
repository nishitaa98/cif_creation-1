from datetime import timedelta
from typing import Annotated, List
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from models import AuthToken
from schemas import User
from db import DBS
from core import Security
from core.payload import generate_cif_entry  # ✅ import function from payload.py
import json

# A list of origins that are permitted to make cross-origin requests
origins = [
    "http://localhost:3000",  # frontend (React/Vue/Angular or similar)
    "http://localhost:5050",  # streamlit or other UI
    "http://10.0.125.114:3000",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Initializing resources...")
    DBS.create_db_and_tables()
    yield
    print("Application shutdown: Cleaning up resources...")

app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# CIF Creation Endpoint
# -------------------------------
@app.post("/create_cif/")
async def create_cif(
    region: str = Query(..., description="Region selection"),
    customer_type: str = Query(..., description="Customer type"),
    no_of_cif: int = Query(1, description="Number of CIF entries to generate"),
):
    """Generate CIF entries based on frontend input"""
    result = []
    for _ in range(no_of_cif):
        cif = generate_cif_entry(region=region, customer_type=customer_type)  # pass args
        result.append(cif)
    return {"count": no_of_cif, "cif_entries": result}


# -------------------------------
# Authentication (already in your code)
# -------------------------------
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DBS.SessionDep
) -> AuthToken.Token:
    user = Security.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=Security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = Security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return AuthToken.Token(access_token=access_token, token_type="bearer")


@app.post("/user")
def register(user: User.DBUser, session: DBS.SessionDep) -> User.DBUser:
    user.password = Security.pwd_context.hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
-------------------------------------------------
import random
import uuid
from datetime import datetime
from typing import Dict, Any

COUNTRY_CODE = ["IN", "US", "AE"]
STATE_CODE = ["MH", "DL", "KA"]
CUSTOMER_TYPE = ["010203", "020304", "030405"]
VILLAGE_CODES = ["556949", "50987", "8765", "64335"]

def generate_random_name():
    return random.choice(["Amit", "Sneha", "Harshada", "Rahul", "Neha", "Raj"])

def generate_cif_entry(region: str, customer_type: str) -> Dict[str, Any]:
    RRN = "SutR126261125195557074929"
    return {
        "VISUALLY IMPAIRED": "N",
        "REQUEST FOR INB": "N",
        "NATIONALITY": random.choice(COUNTRY_CODE),
        "OVD_KYC_DOCUMENT_DETAILS": str(uuid.uuid4())[:12],
        "CUSTOMER TYPE": customer_type,
        "STATE": random.choice(STATE_CODE),
        "CUSTOMER EVALUATION_REQUIRED": random.choice(["N", "Y"]),
        "LAST NAME": generate_random_name(),
        "FIRST NAME": generate_random_name(),
        "PAN AADHAR LINK": "N",
        "MIDDLE NAME": generate_random_name(),
        "DATE OF BIRTH": "21071999",
        "TRANSACTION DATE": datetime.now().strftime("%Y%m%d"),
        "VILLAGE_CODE": random.choice(VILLAGE_CODES),
        "CUSTOMER_TYPE_2": customer_type,
        "PAN_APPLIED_FLAG": "N",
        "CUSTOMER_SEGMENT": "S",
        "DOMESTIC_RISK": "ZZ",
        "HOME_BRANCH": region,   # 👈 region selected
        "SUB_DISTRICT": "04199",
        "EDUCATION_CODE": "01",
        "CONSENT_DATE": "29082025",
        "REQUEST_AUTH_ID": "3600005",
        "TITLE": "03",
        "INCOME_TAX_PAN": "",
        "STREET_ROADNAME_BLOCK": "Maharashtra India 413403 Bavi",
        "LOCALITY_VILLAGE_TEHSIL": "Malegaon Bk",
        "SOURCE_OF_FUNDS": "01",
        "RELATIVE_CODE": "F",
        "REQUEST_REFERENCE_NUMBER": RRN
    }
--------------------------
async function createCIF() {
  const region = "00036"; // user input
  const customerType = "010203"; // user input
  const noOfCif = 2; // user input

  const response = await fetch(
    `http://localhost:8000/create_cif/?region=${region}&customer_type=${customerType}&no_of_cif=${noOfCif}`,
    {
      method: "POST",
    }
  );
  const data = await response.json();
  console.log("Generated CIFs:", data);
}
