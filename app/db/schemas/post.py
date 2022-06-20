from pydantic import BaseModel


class Post(BaseModel):
    id: int
    text: str
    files: str
    link: str
    preview: dict
    author_id: int
    like_count: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "text": "text",
                "files": "path_to_files",
                "link": "link",
                "preview": {
                    "description": "description",
                    "file": "path_to_file"
                },
                "author_id": 1,
                'like_count': 1
            }
        }


class PostLikeCount(BaseModel):
    like_count: int

    class Config:
        schema_extra = {
            "example": {
                'like_count': 1
            }
        }


class ListOfPostsInResponse(BaseModel):
    posts: list[Post]

    class Config:
        schema_extra = {
            'example': {
                'posts': [Post.Config.schema_extra.get("example")]
            }
        }


class PostCreate(BaseModel):
    text: str | None = None
    files: str | None = None
    link: str | None = None
    preview: dict | None = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "text": "text",
                "files": "path_to_files",
                "link": "link",
                "preview": {
                    "description": "description",
                    "file": "path_to_file"
                }
            }
        }
