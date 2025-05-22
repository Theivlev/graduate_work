from fastapi import HTTPException, status

def ensure_user_owns_resource(request_user_id, token_user_id, action: str = "выполнить действие"):
    if str(request_user_id) != str(token_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Вы не можете {action} от имени другого пользователя"
        )