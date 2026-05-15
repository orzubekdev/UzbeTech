from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from database import engine, Base, get_db
from sqlalchemy.orm import Session
from models import User, Message, Reply
from auth import get_current_user, verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
import os

# Create DB tables
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="UzbeTech Platform")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

if not os.path.exists("static"):
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    os.makedirs("static/img", exist_ok=True)
if not os.path.exists("templates"):
    os.mkdir("templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Enterprise Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # CSP: Allow self, inline styles/scripts for demo simplicity, but restrict external
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; frame-ancestors 'none';"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Ensure HTTPS redirection in production could go here
    return response

@app.get("/", response_class=HTMLResponse)
@limiter.limit("50/minute")
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/services", response_class=HTMLResponse)
@limiter.limit("50/minute")
async def read_services(request: Request):
    return templates.TemplateResponse(request=request, name="services.html")

@app.get("/portfolio", response_class=HTMLResponse)
@limiter.limit("50/minute")
async def read_portfolio(request: Request):
    return templates.TemplateResponse(request=request, name="portfolio.html")

@app.get("/about", response_class=HTMLResponse)
@limiter.limit("50/minute")
async def read_about(request: Request):
    return templates.TemplateResponse(request=request, name="about.html")

@app.get("/contact", response_class=HTMLResponse)
@limiter.limit("50/minute")
async def read_contact(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html")

@app.post("/api/contact")
@limiter.limit("5/minute")
async def submit_contact(request: Request, name: str = Form(...), email: str = Form(...), content: str = Form(...), phone: str = Form(None), db: Session = Depends(get_db)):
    msg = Message(name=name, email=email, content=content, phone=phone)
    db.add(msg)
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Message sent successfully"})

# Admin routes
@app.get("/admin/login", response_class=HTMLResponse)
@limiter.limit("10/minute")
async def admin_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin_login.html")

@app.post("/admin/login")
@limiter.limit("5/minute") # Brute force protection
async def admin_login_submit(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    # Secure HttpOnly Cookie
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, samesite="Lax", secure=True) # secure=True requires HTTPS
    return response

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(Message).order_by(Message.created_at.desc()).all()
    return templates.TemplateResponse(request=request, name="admin.html", context={"user": current_user, "messages": messages})

@app.get("/admin/logout")
async def admin_logout(request: Request):
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("access_token")
    return response

if __name__ == "__main__":
    import uvicorn
    # Make sure to run exactly this way
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
