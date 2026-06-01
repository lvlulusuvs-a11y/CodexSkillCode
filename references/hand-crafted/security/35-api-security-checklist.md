# API Security Checklist

Every API endpoint should pass this checklist.

## Authentication

- [ ] Protected endpoints require valid token
- [ ] Tokens expire (short-lived access tokens)
- [ ] Refresh tokens rotate
- [ ] Rate limit on auth endpoints

## Authorization

- [ ] Users can only access their own resources
- [ ] Admin endpoints check role
- [ ] No IDOR (Insecure Direct Object Reference)
- [ ] ACL enforced on all write operations

## Input Validation

- [ ] All input validated (type, length, format)
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (output encoding)
- [ ] Size limits on request body
- [ ] File upload type and size limits

## Output

- [ ] No sensitive data in responses
- [ ] Error messages dont leak internals
- [ ] CORS configured properly
- [ ] Security headers set

## Infrastructure

- [ ] HTTPS enforced
- [ ] Rate limiting on all endpoints
- [ ] Request logging enabled
- [ ] Secrets not in code
- [ ] Dependencies scanned for vulnerabilities

## Monitoring

- [ ] Auth failures logged and alerted
- [ ] Error rate monitored
- [ ] Suspicious patterns detected
- [ ] Audit trail for data changes

## Common API Vulnerabilities

1. Injection (SQL, NoSQL, OS command)
2. Broken authentication
3. Excessive data exposure
4. Lack of rate limiting
5. Broken function authorization
6. Mass assignment
7. Security misconfiguration
8. Insecure deserialization

## Testing

- [ ] Automated security tests in CI
- [ ] Dependency scanning
- [ ] Static analysis (SAST)
- [ ] Dynamic analysis (DAST)
- [ ] Penetration testing (quarterly)


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.
