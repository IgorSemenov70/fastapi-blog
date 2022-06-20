"""
Create table users, posts, like_users
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""CREATE TABLE users (
                id BIGSERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                hashed_password VARCHAR(255) NOT NULL);""",
    """DROP TABLE users"""),
    step("""CREATE TABLE posts (
                id BIGSERIAL PRIMARY KEY,
                text VARCHAR(255),
                files VARCHAR(1000),
                link VARCHAR(255),
                preview JSONB,
                like_count INTEGER DEFAULT 0,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE);""",
        """DROP TABLE posts"""),
    step("""CREATE TABLE like_users (
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE);""",
        """DROP TABLE like_users""")
]
