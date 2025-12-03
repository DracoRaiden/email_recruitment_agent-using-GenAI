from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 1. Define a data model for the Response
# This ensures your API always returns data in this exact structure.
class ApplicationStatus(BaseModel):
    user_id: int
    status: str
    description: Optional[str] = None

# 2. Create Mock Data (Simulating a Database)
# In a real app, this would be a SQL query.
mock_database = {
    101: {"status": "Pending", "desc": "Your application is under review."},
    102: {"status": "Accepted", "desc": "Congratulations! You have been selected."},
    103: {"status": "Rejected", "desc": "We regret to inform you..."},
    104: {"status": "Interview", "desc": "Please schedule your interview."}
}

# 3. Create the Endpoint
@app.get("/applications/{user_id}", response_model=ApplicationStatus)
async def get_application_status(user_id: int):
    
    # Check if user exists in our mock DB
    data = mock_database.get(user_id)
    
    if not data:
        # If user not found, return a 404 Error
        raise HTTPException(status_code=404, detail="Application not found for this User ID")
    
    # Return the data matching the Pydantic model
    return ApplicationStatus(
        user_id=user_id,
        status=data["status"],
        description=data["desc"]
    )