from uuid import UUID


from .dto import AbstractDTO


class UserSimilarityBase(AbstractDTO):
    user1_id: UUID
    user2_id: UUID
    similarity: float


class UserSimilarityCreate(UserSimilarityBase):
    pass


class UserSimilaritySchema(UserSimilarityBase):
    pass


class MovieSimilarityBase(AbstractDTO):
    movie1_id: UUID
    movie2_id: UUID
    similarity: float


class MovieSimilarityCreate(MovieSimilarityBase):
    pass


class MovieSimilaritySchema(MovieSimilarityBase):
    pass
