from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.twilio_config import client, VERIFY_SERVICE_SID

router = APIRouter()

class SendOTP(BaseModel):
    mobile: str
    role: str

class VerifyOTP(BaseModel):
    mobile: str
    otp: str
    role: str


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

        return {
            "mobile": data.mobile,
            "role": data.role,
            "token": "demo-token"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
