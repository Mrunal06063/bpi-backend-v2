from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from app.twilio_config import client, VERIFY_SERVICE_SID
from app.jwt import create_access_token
from app.database import engine


router = APIRouter(prefix="/auth", tags=["Auth"])
 
 
# ======================
# SCHEMAS
# ======================
class SendOTP(BaseModel):
    mobile: str
    role: str
 
 
class VerifyOTP(BaseModel):
    mobile: str
    otp: str
    role: str
 
 
# ======================
# SEND OTP
# ======================
@router.post("/send-otp")
def send_otp(data: SendOTP):
    try:
        client.verify.v2.services(VERIFY_SERVICE_SID).verifications.create(
            to=f"+91{data.mobile}",
            channel="sms"
        )
        return {"message": "OTP sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
 
 
# ======================
# VERIFY OTP + JWT
# ======================
@router.post("/verify-otp")
def verify_otp(data: VerifyOTP):
    try:
        verification = client.verify.v2.services(
            VERIFY_SERVICE_SID
        ).verification_checks.create(
            to=f"+91{data.mobile}",
            code=data.otp
        )
 
        if verification.status != "approved":
            raise HTTPException(status_code=401, detail="Invalid OTP")

        #  FETCH EMPLOYEE DATA FROM DATABASE
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT emp_id, mobile_number, role, full_name
                    FROM employees
                    WHERE mobile_number = :mobile AND role = :role
                """),
                {"mobile": data.mobile, "role": data.role}
            ).fetchone()

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Employee not found or role mismatch"
                )

        # 🔐 CREATE JWT TOKEN
        access_token = create_access_token(
            data={
                "sub": result.mobile_number,
                "emp_id": result.emp_id,
                "role": result.role
            }
        )

        return {
            "accessToken": access_token,
            "currentUser": {
                "emp_id": result.emp_id,
                "mobile": result.mobile_number,
                "role": result.role,
                "full_name": result.full_name
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))