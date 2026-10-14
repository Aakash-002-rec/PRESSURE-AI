from fastapi import APIRouter, HTTPException, status, Depends
from ..database import get_db_connection, hash_password
from ..models import UserRegister, UserLogin, TokenResponse, UserResponse
from ..auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Normalize role: default candidate unless explicitly specified
    role = "admin" if user_data.role == "admin" else "candidate"
    pwd_hash = hash_password(user_data.password)

    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    """, (user_data.name, user_data.email, pwd_hash, role))
    user_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,))
    new_user = dict(cursor.fetchone())
    conn.close()

    token = create_access_token({"sub": str(user_id), "role": role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (login_data.email,))
    user = cursor.fetchone()

    # If user doesn't exist yet, auto-provision their candidate account seamlessly!
    if not user:
        if len(login_data.password) < 4:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 4 characters long."
            )
        # Generate friendly display name from email (e.g. aakashraja from aakashraja2502@gmail.com)
        derived_name = login_data.email.split("@")[0].replace(".", " ").replace("_", " ").title()
        pwd_hash = hash_password(login_data.password)
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, 'candidate')
        """, (derived_name, login_data.email, pwd_hash))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
    else:
        conn.close()
        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password for this account. Please verify your password."
            )

    token = create_access_token({"sub": str(user["id"]), "role": user["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "created_at": str(user["created_at"])
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "created_at": str(current_user["created_at"])
    }
