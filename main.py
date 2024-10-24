from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schema import UserCreate, UserResponse, Token, PostCreate, PostResponse, CommentCreate, CommentResponse
from crud import create_user, authenticate_user, create_new_post, create_comment, read_posts, read_comments, like_post, unlike_post, get_user
from auth import create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from models import User

app = FastAPI()

@app.post("/users/", response_model=UserResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

# Posts
@app.post("/posts/", response_model=PostResponse)
def create_new_post_endpoint(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_new_post(db, post, current_user)

@app.get("/posts/", response_model=list[PostResponse])
def read_posts_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return read_posts(db, skip, limit)

# Comments
@app.post("/comments/", response_model=CommentResponse)
def create_comment_endpoint(comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_comment(db, comment, current_user)

@app.get("/comments/{post_id}", response_model=list[CommentResponse])
def read_comments_endpoint(post_id: int, db: Session = Depends(get_db)):
    return read_comments(db, post_id)

# Likes
@app.post("/posts/{post_id}/like")
def like_post_endpoint(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return like_post(db, post_id, current_user)

@app.delete("/posts/{post_id}/like")
def unlike_post_endpoint(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return unlike_post(db, post_id, current_user)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
