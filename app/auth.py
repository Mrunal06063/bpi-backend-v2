from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.twilio_config import client, VERIFY_SERVICE_SID
from app.jwt import create_access_token
from app.database import engine
from sqlalchemy import text


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
    rememberMe: bool = False  # Optional: defaults to False


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
        
        # ✅ FETCH EMPLOYEE FROM DB
        with engine.connect() as conn:
            emp = conn.execute(
                text("""
                    SELECT emp_id, full_name, mobile_number, role
                    FROM employees
                    WHERE mobile_number = :mobile
                      AND is_active = true
                """),
                {"mobile": data.mobile}
            ).fetchone()

        if not emp:
            raise HTTPException(
                status_code=403,
                detail="not registered employee"
            )

        # 🔐 CREATE JWT TOKEN
        # If rememberMe is True: 24 hours (1440 minutes)
        # If rememberMe is False: 60 minutes (session only)
        token_expiry = 1440 if data.rememberMe else 60

        access_token = create_access_token(
            data={
                "sub": emp.mobile_number,
                "emp_id": emp.emp_id,
                "role": emp.role
            },
            expires_in_minutes=token_expiry
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