from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.twilio_config import client, VERIFY_SERVICE_SID
from app.jwt import create_access_token


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

        # 🔐 CREATE JWT TOKEN
        access_token = create_access_token(
            data={
                "sub": emp.mobile_number,
                "emp_id": emp.emp_id,
                "role": emp.role
            }
        )
       
        return {
            "accessToken": access_token,
            "currentUser": {
                "emp_id": emp.emp_id,
                "mobile": emp.mobile_number,
                "role": emp.role,
                "full_name": emp.full_name
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))