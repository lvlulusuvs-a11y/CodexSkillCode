# Secrets Management: Dont Store Secrets in Code

Hardcoding secrets is the most common security mistake.

## What is a Secret

- Database passwords
- API keys and tokens
- Encryption keys
- Private certificates
- OAuth client secrets

Anything that grants access to a system is a secret.

## What NOT to Do

BAD:
DB_PASSWORD = "supersecret123"
API_KEY = "sk_live_xxxxxxxxxxxx"

Bad in code. Bad in configs in git. Bad in Dockerfiles.
Bad anywhere that ends up in version control.

## Environment Variables (Minimum)

import os

DB_PASSWORD = os.environ["DB_PASSWORD"]
STRIPE_KEY = os.environ["STRIPE_SECRET_KEY"]

Store in your CI/CD secrets manager, not in files.

## Secret Managers (Better)

Use AWS Secrets Manager, Vault, or GCP Secret Manager:

import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region: str = "us-east-1") -> str:
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region,
    )
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
    except ClientError as e:
        raise Exception(f"Failed to get secret {secret_name}") from e

# Usage
DB_PASSWORD = get_secret("prod/db/password")

## Vault Integration

import hvac

client = hvac.Client(url="https://vault.example.com", token=VAULT_TOKEN)
secret = client.secrets.kv.v2.read_secret_version(
    path="database/credentials",
    mount_point="secret",
)
DB_PASSWORD = secret["data"]["data"]["password"]

## Preventing Secret Leaks

1. Use .gitignore to exclude secret files
2. Use git-secrets or trufflehog to scan for secrets
3. Never echo secrets in CI/CD logs
4. Rotate secrets regularly
5. Use short-lived credentials

## Secret Scanning

Pre-commit hook:

git-secrets --scan
git-secrets --add "sk_live_"

CI check:
trufflehog git --since-commit HEAD~1

## Incident Response for Secret Leak

1. Revoke the leaked secret immediately
2. Rotate all credentials that share the same key
3. Audit logs for unauthorized access
4. Update scanning rules to catch similar patterns
5. Document and learn from the incident


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
