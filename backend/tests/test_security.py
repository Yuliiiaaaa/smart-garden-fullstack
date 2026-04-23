from app.core.security import get_password_hash, verify_password, create_access_token, verify_token

def test_password_hashing():
    password = "secret"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

def test_access_token():
    data = {"sub": "test@example.com", "role": "user"}
    token = create_access_token(data)
    decoded = verify_token(token)
    assert decoded.email == "test@example.com"
    assert decoded.role == "user"