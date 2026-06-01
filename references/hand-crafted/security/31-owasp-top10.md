# Security: OWASP Top 10 for Backend Developers

Security is not optional. It is built into every endpoint.

## 1. Broken Access Control

Check permissions on EVERY endpoint.

@app.get("/admin/users")
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403)
    return await user_service.get_all()

Dont forget about:
- Direct object references (/users/{id} - can I see other users?)
- Missing function-level access control
- POST, PUT, DELETE without auth checks

## 2. Cryptographic Failures

Use modern cryptography, dont roll your own.

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

## 3. Injection

Always use parameterized queries.

BAD: cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
GOOD: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

## 4. Insecure Design

Security must be designed in from the start, not added later.

- Rate limiting on auth endpoints
- Input validation on all endpoints
- Output encoding to prevent XSS
- CSRF protection for cookies

## 5. Security Misconfiguration

Use security headers on all responses.

response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["Content-Security-Policy"] = "default-src 'self'"
response.headers["Strict-Transport-Security"] = "max-age=31536000"

## 6. Vulnerable Dependencies

Keep dependencies up to date. Scan regularly.

pip-audit
safety check --full-report
trivy filesystem .

## 7. Auth Failures

Rate limit login attempts. Use secure password hashing.

## 8. Data Integrity Failures

Use HTTPS. Validate JWTs properly. Sign webhook payloads.

## 9. Logging Failures

Log auth attempts, access violations, data changes.
Never log passwords, tokens, or personal data.

## 10. SSRF

Validate URLs that users provide. Dont fetch from internal networks.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.
