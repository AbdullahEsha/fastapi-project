# filepath @services/authService.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Template
from fastapi import Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from helper.createToken import create_access_token
from models.User import User
from config.dbConnect import get_db
from dotenv import load_dotenv
from jose import jwt
from passlib.hash import bcrypt
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

def handle_register(name: str, email: str, password: str, db: Session = Depends(get_db)):
    # Check if the email is already registered
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    # Hash the password
    hashed_password = bcrypt.hash(password)

    # Create new user
    new_user = User(name=name, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user": {"id": new_user.id, "email": new_user.email}}

def handle_login(email: str, password: str, db: Session = Depends(get_db)):
    # Fetch user from the database
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify the hashed password
    if not bcrypt.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=int(os.getenv("TOKEN_EXPIRES", 30)))  # Default to 30 minutes
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "role": user.role}
    }

def handle_logout(request: Request):
    try:
        # Extract and decode the token
        token = request.headers.get("Authorization").split(" ")[1]
        decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])

        # expire the token
        decoded_token.update({"exp": datetime.utcnow()})
        
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        else:
            return {"message": "User logged out successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

from fastapi import BackgroundTasks  # Ensure you import BackgroundTasks

def handle_forgot_password(
    email: str, 
    background_tasks: BackgroundTasks,
    db: Session  # Correctly accepts db as a regular parameter
):
    try:
        # Fetch user from the database using the email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=int(os.getenv("TOKEN_EXPIRES", 30)))
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
        # Render HTML template
        with open("view/emailTemplate.html", "r") as template_file:
            template_content = template_file.read()
    
        template = Template(template_content)
        rendered_template = template.render(
            url=os.getenv("APP_URL", "http://localhost:3000"),
            token=access_token,
            email=email,
            current_year=datetime.now().year
        )
    
        # Send email
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            body=rendered_template,
            subtype="html",
        )
    
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message)

        return {"message": "Password reset email sent successfully."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# forgot password reset
def handle_reset_password(password: str, confirm_password: str, request: Request, db: Session = Depends(get_db)):
    try:
        # Check if the password and confirm password match
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        # Hash the password
        hashed_password = bcrypt.hash(password)
        
        # get the token from the request params and decode it
        token = request.path_params.get("token")
        decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])

        # Fetch user from the database using the email
        user = db.query(User).filter(User.email == decoded_token["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update the user's password
        user.password = hashed_password
        db.commit()
        return {"message": "Password reset successful"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
