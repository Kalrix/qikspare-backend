# services/auth_service.py

import httpx
import os

API_KEY = "acd01d56-2fbd-11f0-8b17-0200cd936042"
OTP_TEMPLATE = "QIKSPARE"  # Update with your actual template name if set on 2Factor

async def send_otp_2factor(phone: str):
    url = f"https://2factor.in/API/V1/{API_KEY}/SMS/{phone}/AUTOGEN/{OTP_TEMPLATE}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    if data["Status"] == "Success":
        return {"status": "sent", "session_id": data["Details"]}
    else:
        raise Exception("Failed to send OTP: " + data.get("Details", "Unknown error"))

async def verify_otp_2factor(phone: str, otp: str):
    url = f"https://2factor.in/API/V1/{API_KEY}/SMS/VERIFY3/{phone}/{otp}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    if data["Status"] == "Success":
        return True
    return False
