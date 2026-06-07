# Docker Hub Credentials Walkthrough

This is the end-to-end GUI walkthrough for preparing Docker Hub publishing from GitHub Actions.

Use this when you want to run the CI workflow with:

```text
publish_image: true
```

## What You Are Setting Up
The CI workflow needs two GitHub repository secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

These are not typed into the workflow run screen.

They are saved once in GitHub repository settings, and GitHub Actions injects them into the workflow automatically.

## Step 1: Login To Docker Hub
Open Docker Hub:

```text
https://hub.docker.com/
```

Login with your Docker Hub account.

Confirm your Docker Hub username. Use the username, not email, for:

```text
DOCKERHUB_USERNAME
```

## Step 2: Create Docker Hub Access Token
In Docker Hub, go to:

```text
Docker Hub
-> Account Settings
-> Security
-> Access Tokens
-> Generate new token
```

Use a clear token name, for example:

```text
modelopslab-github-actions
```

Recommended access:

```text
Read, Write
```

Generate the token.

Copy the token immediately. Docker Hub will not show the token value again after you leave the page.

This token becomes:

```text
DOCKERHUB_TOKEN
```

Do not use your Docker Hub account password.

## Step 3: Add GitHub Actions Secret For Username
Open your GitHub repository.

Go to:

```text
GitHub repository
-> Settings
-> Secrets and variables
-> Actions
-> New repository secret
```

Create this secret:

```text
Name:
DOCKERHUB_USERNAME

Value:
your Docker Hub username
```

Save the secret.

## Step 4: Add GitHub Actions Secret For Token
In the same GitHub Actions secrets area:

```text
GitHub repository
-> Settings
-> Secrets and variables
-> Actions
-> New repository secret
```

Create this secret:

```text
Name:
DOCKERHUB_TOKEN

Value:
the Docker Hub access token
```

Save the secret.

## Step 5: Verify Secret Names
Go to:

```text
GitHub repository
-> Settings
-> Secrets and variables
-> Actions
-> Repository secrets
```

Confirm these exact names exist:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

GitHub will not show the secret values after saving. That is expected.

## Step 6: Run CI Without Publishing
Use this for normal validation.

Go to:

```text
GitHub repository
-> Actions
-> ci
-> Run workflow
-> Branch: main
-> publish_image: false
-> Run workflow
```

Expected behavior:

```text
pytest runs
Docker image builds
Docker Hub login is skipped
Docker Hub push is skipped
```

## Step 7: Run CI With Docker Hub Publishing
Use this only when you want to publish the image.

Go to:

```text
GitHub repository
-> Actions
-> ci
-> Run workflow
-> Branch: main
-> publish_image: true
-> Run workflow
```

Expected behavior:

```text
pytest runs
Docker image builds
Docker Hub secrets are validated
Docker Hub login runs
Docker image is tagged for Docker Hub
Docker image is pushed
```

## Step 8: Verify Published Image On Docker Hub
Open Docker Hub:

```text
Docker Hub
-> Repositories
-> modelopslab-serving
-> Tags
```

Expected tags:

```text
<git-sha>
ci
```

The Git SHA tag is the important traceable tag.

The `ci` tag is a moving convenience tag.

## Common Errors
If CI says:

```text
Missing GitHub Actions secret: DOCKERHUB_USERNAME
```

Fix:

```text
Add the DOCKERHUB_USERNAME repository secret in GitHub Actions secrets.
```

If CI says:

```text
Missing GitHub Actions secret: DOCKERHUB_TOKEN
```

Fix:

```text
Create a Docker Hub access token and add it as DOCKERHUB_TOKEN.
```

If Docker Hub login still fails:

```text
check username is Docker Hub username, not email
check token is access token, not account password
check token was copied fully
check token has write access
check secret names match exactly
```

## Safety Rules
- Do not commit the token.
- Do not paste the token into `.env`.
- Do not paste the token into docs.
- Do not print the token in logs.
- Revoke and recreate the token if it leaks.
