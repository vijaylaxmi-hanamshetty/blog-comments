from sqlalchemy.orm import Session
from models import User, Post, Comment
from schema import UserCreate, PostCreate, CommentCreate
import bcrypt
from fastapi import HTTPException

# Function to create a new user
def create_user(db: Session, user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password.decode('utf-8'))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Function to retrieve a user by username
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Function to authenticate a user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return False
    return user

# Function to create a new post
def create_new_post(db: Session, post: PostCreate, current_user: User):
    db_post = Post(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Function to create a comment on a post
def create_comment(db: Session, comment: CommentCreate, current_user: User):
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_comment = Comment(content=comment.content, post_id=comment.post_id, user_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# Function to read posts with pagination
def read_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Post).offset(skip).limit(limit).all()

# Function to read comments for a post
def read_comments(db: Session, post_id: int):
    return db.query(Comment).filter(Comment.post_id == post_id).all()

# Function to like a post
def like_post(db: Session, post_id: int, current_user: User):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if current_user in post.liked_by:
        raise HTTPException(status_code=400, detail="Post already liked")
    
    post.liked_by.append(current_user)
    db.commit()
    return {"detail": "Post liked successfully"}

# Function to unlike a post
def unlike_post(db: Session, post_id: int, current_user: User):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if current_user not in post.liked_by:
        raise HTTPException(status_code=400, detail="Post not liked yet")

    post.liked_by.remove(current_user)
    db.commit()
    return {"detail": "Post unliked successfully"}
