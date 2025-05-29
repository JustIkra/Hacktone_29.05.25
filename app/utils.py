from passlib.context import CryptContext

# Создаём объект контекста для хэширования с алгоритмом bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Получить хэш пароля.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверить, что пароль пользователя совпадает с хэшем.
    """
    return pwd_context.verify(plain_password, hashed_password)
