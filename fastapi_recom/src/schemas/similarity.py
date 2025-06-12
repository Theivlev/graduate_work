class UserSimilarityBase(BaseModel):
    user1_id: UUID
    user2_id: UUID
    similarity: float


class UserSimilarityCreate(UserSimilarityBase):
    pass


class UserSimilaritySchema(UserSimilarityBase):
    class Config:
        from_attributes = True


class MovieSimilarityBase(BaseModel):
    movie1_id: UUID
    movie2_id: UUID
    similarity: float


class MovieSimilarityCreate(MovieSimilarityBase):
    pass


class MovieSimilaritySchema(MovieSimilarityBase):
    class Config:
        from_attributes = True