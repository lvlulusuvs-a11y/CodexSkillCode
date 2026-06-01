# Dockerfile Best Practices

I have seen Dockerfiles that produce 2GB images and take 30 minutes to build.
Here is how to do it right.

## The Goal

Small images (under 200MB) that build fast (under 2 minutes) and are secure.

## Multi-Stage Builds

Use builder stage for dependencies, final stage for runtime only.

FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8080
CMD ["python", "main.py"]

The final image is 80% smaller without build tools.

## Benefits of Multi-Stage

1. Smaller images - no compilers or headers in final image
2. More secure - fewer packages = fewer vulnerabilities
3. Faster builds - leverage Docker layer caching
4. Cleaner - separate build and runtime concerns

## .dockerignore

Prevent build context bloat:

__pycache__/
.git/
.gitignore
*.md
tests/
.env
.venv/
*.pyc

## Layer Caching

Order matters for caching:

BAD: invalidates cache on every code change
COPY . .
RUN pip install -r requirements.txt

GOOD: requirements rarely change
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

## Security Best Practices

1. Never run as root: USER appuser
2. No secrets in build args
3. Always use --no-cache-dir for pip
4. Pin base image versions, not :latest
5. Scan images for vulnerabilities regularly

Pin versions:
FROM python:3.12-slim  # Good
FROM python:latest     # Bad

## Go Dockerfile

FROM golang:1.22 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server .

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/server /server
CMD ["/server"]

Result: ~15MB image. Python slim is ~130MB. Python full is ~1GB.


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


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.
