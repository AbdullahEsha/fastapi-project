from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from config.dbConnect import get_db
from services.authService import handle_forgot_password, handle_register, handle_login, handle_logout, handle_reset_password
from schemas.authSchemas import ForgotPasswordRequest, RegisterRequest, LoginRequest, ResetPasswordRequest

authRouter = APIRouter()

# Register user
@authRouter.post("/register/")
def registerRouter(data: RegisterRequest, db: Session = Depends(get_db)):
    return handle_register(data.name, data.email, data.password, db)

# Login user
@authRouter.post("/login/")
def loginRouter(data: LoginRequest, db: Session = Depends(get_db)):
    return handle_login(data.email, data.password, db)

# Logout user
@authRouter.post("/logout/")
def logoutRouter(request: Request):
    return handle_logout(request)

# forgot password
@authRouter.post("/forgot-password/")
def forgotPasswordRouter(data: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return handle_forgot_password(data.email, background_tasks, db)

# Reset password
@authRouter.post("/reset-password/:token")
def resetPasswordRouter(data: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    return handle_reset_password(data.email, data.password, data.confirm_password, db)
