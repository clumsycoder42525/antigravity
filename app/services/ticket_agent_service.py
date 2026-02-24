from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
import re

# Router (NO prefix here — prefix main.py me diya hai)
router = APIRouter()

# ----------------------------
# In-Memory Store
# ----------------------------
BOOKINGS: Dict[str, dict] = {}


# ----------------------------
# Request Model
# ----------------------------
class TicketRequest(BaseModel):
    user_id: str
    conversation_id: str
    question: str


# ----------------------------
# Helper Functions
# ----------------------------
def get_key(user_id: str, conversation_id: str):
    return f"{user_id}:{conversation_id}"


def extract_name(text: str):
    match = re.search(r'name is (.*)', text.lower())
    return match.group(1).title() if match else None


def extract_email(text: str):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None


def extract_date(text: str):
    match = re.search(r'\d{1,2}\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?', text.lower())
    return match.group(0) if match else None


def extract_time(text: str):
    match = re.search(r'\d{1,2}(:\d{2})?\s*(am|pm)', text.lower())
    return match.group(0) if match else None


# ----------------------------
# Ticket Booking Endpoint
# ----------------------------
@router.post("/ticket")
def ticket_agent(request: TicketRequest):

    print("🔥 BOOKING AGENT HIT")

    key = get_key(request.user_id, request.conversation_id)

    # Initialize state if not exists
    if key not in BOOKINGS:
        BOOKINGS[key] = {
            "name": None,
            "email": None,
            "date": None,
            "time": None,
            "confirmed": False
        }

    state = BOOKINGS[key]
    text = request.question

    # Extract details
    name = extract_name(text)
    if name:
        state["name"] = name

    email = extract_email(text)
    if email:
        state["email"] = email

    date = extract_date(text)
    if date and not state["date"]:
        state["date"] = date

    time = extract_time(text)
    if time and not state["time"]:
        state["time"] = time

    # ----------------------------
    # Slot Filling Flow
    # ----------------------------
    if not state["name"]:
        return {"answer": "Please provide your name."}

    if not state["email"]:
        return {"answer": "Please provide your email address."}

    if not state["date"]:
        return {"answer": "Please provide the booking date."}

    if not state["time"]:
        return {"answer": "Please provide the booking time (e.g., 5 PM)."}

    # Confirm Booking
    state["confirmed"] = True

    return {
        "answer": (
            f"✅ Booking Confirmed!\n\n"
            f"Name: {state['name']}\n"
            f"Email: {state['email']}\n"
            f"Date: {state['date']}\n"
            f"Time: {state['time']}\n\n"
            f"Your ticket has been successfully booked."
        )
    }