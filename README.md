# EarthRISE Prompt Exchange

[![Python: 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![EarthRISE: Development](https://img.shields.io/badge/EarthRISE-Development-b50000?labelColor=191f4c)](https://appliedsciences.nasa.gov/what-we-do/capacity-building/develop)

A Django web application for NASA EarthRISE domain experts to share, discover, and collaborate on AI prompts. Access is restricted to authorized EarthRISE personnel via Google OAuth and email-based allowlist.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Local Development](#local-development)
  - [Prerequisites](#prerequisites)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Create the Conda environment](#2-create-the-conda-environment)
  - [3. Configure environment variables](#3-configure-environment-variables)
  - [4. Run database migrations](#4-run-database-migrations)
  - [5. Create a superuser](#5-create-a-superuser)
  - [6. Configure Google OAuth](#6-configure-google-oauth)
  - [7. Seed domains (optional)](#7-seed-domains-optional)
  - [8. Start the development server](#8-start-the-development-server)
- [Access Control](#access-control)
- [Production Deployment](#production-deployment)
  - [1. Provision the server](#1-provision-the-server)
  - [2. Install Conda on the server](#2-install-conda-on-the-server)
  - [3. Deploy application files](#3-deploy-application-files)
  - [4. Create the Conda environment](#4-create-the-conda-environment-1)
  - [5. Configure production environment variables](#5-configure-production-environment-variables)
  - [6. Initialize the application](#6-initialize-the-application)
  - [7. Configure systemd socket and service](#7-configure-systemd-socket-and-service)
  - [8. Configure Nginx](#8-configure-nginx)
  - [9. Configure Google OAuth for production](#9-configure-google-oauth-for-production)
  - [10. Enable and start services](#10-enable-and-start-services)
- [Environment Variable Reference](#environment-variable-reference)
- [Sub-path Deployment](#sub-path-deployment)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5.x |
| Authentication | django-allauth (Google OAuth 2.0) |
| Forms | django-crispy-forms + crispy-bootstrap4 |
| Frontend | Bootstrap 5.3, Bootstrap Icons, Horizon Design System |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL (recommended) |
| WSGI server | Gunicorn |
| Reverse proxy | Nginx |
| Package management | Conda (environment.yml) |

---

## Local Development

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download) installed
- A Google Cloud project with OAuth 2.0 credentials (see [Configure Google OAuth](#6-configure-google-oauth))
- Git

---

### 1. Clone the repository

```bash
git clone <repository-url>
cd nasa_prompts
```

---

### 2. Create the Conda environment

The `environment.yml` file defines all dependencies. Create the environment from it:

```bash
conda env create -f environment.yml
```

This creates an environment named **`nasa_prompts`** with Python 3.13 and all required packages. Activate it:

```bash
conda activate nasa_prompts
```

To update the environment after future changes to `environment.yml`:

```bash
conda env update -f environment.yml --prune
```

---

### 3. Configure environment variables

The application uses [python-decouple](https://github.com/HBNetwork/python-decouple) to read settings from a `.env` file. Create one in the project root:

```bash
cp .env.example .env   # if an example exists, otherwise create it fresh
```

Minimum required `.env` for local development:

```ini
SECRET_KEY=your-long-random-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### 4. Run database migrations

```bash
python manage.py migrate
```

---

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

The superuser bypasses the EarthRISE group access check and can access `/admin/`.

---

### 6. Configure Google OAuth

The application authenticates users via Google. You need a Google Cloud OAuth 2.0 client.

**Create credentials:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Add authorized redirect URI:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```
5. Note the **Client ID** and **Client Secret**

**Register in Django admin:**

1. Start the dev server and navigate to `http://localhost:8000/admin/`
2. Go to **Sites** → edit the default site → set domain to `localhost:8000`, name to `localhost`
3. Go to **Social Applications** → **Add** → select provider **Google**
4. Fill in Client ID and Secret Key from the step above
5. Move `localhost` from "Available sites" to "Chosen sites"
6. Save

---

### 7. Seed domains (optional)

Domains can be created through the Django admin at `/admin/prompts/domain/add/` or via the shell:

```bash
python manage.py shell
```

```python
from prompts.models import Domain
Domain.objects.create(name="Hydrology", description="Water resources and hydrological modeling")
Domain.objects.create(name="Land Cover", description="Land use and land cover change analysis")
# add more as needed
```

---

### 8. Start the development server

```bash
python manage.py runserver
```

Visit `http://localhost:8000`. Log in with Google OAuth using a superuser-associated Google account, or add your email to the AllowedEmail list first (see [Access Control](#access-control)).

---

## Access Control

Access is restricted to members of the **EarthRISE** Django group. The middleware (`prompts/middleware.py`) enforces this on every request.

**To grant access to a user:**

**Option A — AllowedEmail (recommended for new users):** Add their email in the admin at `/admin/prompts/allowedemail/`. On their first Google OAuth login, they will be automatically added to the EarthRISE group.

**Option B — Manual group assignment:** In `/admin/auth/user/`, find the user, open their record, and add them to the **EarthRISE** group under "Groups".

The **EarthRISE** group is created automatically on first use. Superusers and staff always bypass the group check.

---

## Production Deployment

The `deployment/` directory contains ready-to-use systemd and Nginx config files for deploying at a sub-path (e.g., `https://eax.sciencecloud.nasa.gov/prompt-exchange`).

### 1. Provision the server

Recommended: Ubuntu 22.04 LTS or RHEL 8+. Install system packages:

```bash
sudo apt update && sudo apt install -y nginx postgresql postgresql-contrib
```

---

### 2. Install Conda on the server

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3
/opt/miniconda3/bin/conda init bash
source ~/.bashrc
```

---

### 3. Deploy application files

Copy the project to the server. The deployment configs assume `/srv/prompt-exchange`:

```bash
sudo mkdir -p /srv/prompt-exchange
sudo chown $USER:$USER /srv/prompt-exchange
git clone <repository-url> /srv/prompt-exchange
# or rsync from your local machine:
# rsync -av --exclude='.git' --exclude='db.sqlite3' ./ user@server:/srv/prompt-exchange/
```

---

### 4. Create the Conda environment

```bash
cd /srv/prompt-exchange
conda env create -f environment.yml
```

Find the path to the conda environment:

```bash
conda env list
# note the path shown next to nasa_prompts, e.g. /opt/miniconda3/envs/nasa_prompts
```

---

### 5. Configure production environment variables

Create `/srv/prompt-exchange/.env`:

```ini
SECRET_KEY=your-long-random-production-secret-key
DEBUG=False
ALLOWED_HOSTS=eax.sciencecloud.nasa.gov
CSRF_TRUSTED_ORIGINS=https://eax.sciencecloud.nasa.gov

# Sub-path prefix (must match the Nginx location block)
SCRIPT_NAME=/prompt-exchange

# Protocol for OAuth callbacks
ACCOUNT_DEFAULT_HTTP_PROTOCOL=https

# PostgreSQL (recommended for production)
# DATABASE_URL or individual vars — uncomment the postgres block in settings.py and add:
DB_NAME=prompt_exchange
DB_USER=prompt_exchange
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Email (optional — defaults to console backend if omitted)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.nasa.gov
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@nasa.gov
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@nasa.gov
```

Secure the file:

```bash
chmod 600 /srv/prompt-exchange/.env
```

**Set up PostgreSQL** (if using it):

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE prompt_exchange;
CREATE USER prompt_exchange WITH PASSWORD 'your-db-password';
GRANT ALL PRIVILEGES ON DATABASE prompt_exchange TO prompt_exchange;
\q
```

Then uncomment the PostgreSQL `DATABASES` block in `nasa_prompts/settings.py` and install `psycopg2`:

```bash
conda activate nasa_prompts
pip install psycopg2-binary
```

---

### 6. Initialize the application

```bash
conda activate nasa_prompts
cd /srv/prompt-exchange

python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --no-input
```

Create the logs directory:

```bash
mkdir -p /srv/prompt-exchange/logs
```

---

### 7. Configure systemd socket and service

The `deployment/` directory contains the socket and service files. Copy them to systemd and update the Gunicorn `ExecStart` path to point to the conda environment.

**Socket:**

```bash
sudo cp deployment/gunicorn.socket /etc/systemd/system/prompt-exchange.socket
```

**Service** — edit to use the conda gunicorn binary before copying:

Open `deployment/gunicorn.service` and update `ExecStart`:

```ini
ExecStart=/opt/miniconda3/envs/nasa_prompts/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/prompt-exchange/gunicorn.sock \
    --log-file /srv/prompt-exchange/logs/gunicorn.log \
    --access-logfile /srv/prompt-exchange/logs/gunicorn-access.log \
    nasa_prompts.wsgi:application
```

Replace `/opt/miniconda3/envs/nasa_prompts` with the actual path from `conda env list` if different.

```bash
sudo cp deployment/gunicorn.service /etc/systemd/system/prompt-exchange.service
```

---

### 8. Configure Nginx

```bash
sudo cp deployment/nginx.conf /etc/nginx/sites-available/prompt-exchange
sudo ln -s /etc/nginx/sites-available/prompt-exchange /etc/nginx/sites-enabled/
```

Update `nginx.conf` if your hostname or SSL certificate paths differ from the defaults:

| Placeholder | Replace with |
|---|---|
| `eax.sciencecloud.nasa.gov` | Your server's hostname |
| `/etc/ssl/certs/eax.sciencecloud.nasa.gov.crt` | Path to your TLS certificate |
| `/etc/ssl/private/eax.sciencecloud.nasa.gov.key` | Path to your TLS private key |

Test the Nginx config and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### 9. Configure Google OAuth for production

1. In [Google Cloud Console](https://console.cloud.google.com/), add the production redirect URI to your OAuth client:
   ```
   https://eax.sciencecloud.nasa.gov/prompt-exchange/accounts/google/login/callback/
   ```
2. Log into the Django admin at `https://eax.sciencecloud.nasa.gov/prompt-exchange/admin/`
3. Update the **Site** record: set domain to `eax.sciencecloud.nasa.gov`
4. Update (or create) the **Social Application** for Google with your production Client ID and Secret, associated with the production site

---

### 10. Enable and start services

```bash
sudo systemctl daemon-reload
sudo systemctl enable prompt-exchange.socket prompt-exchange.service
sudo systemctl start prompt-exchange.socket prompt-exchange.service
sudo systemctl restart nginx
```

Check status:

```bash
sudo systemctl status prompt-exchange.socket
sudo systemctl status prompt-exchange.service
sudo journalctl -u prompt-exchange.service -f
```

The application is now available at `https://eax.sciencecloud.nasa.gov/prompt-exchange`.

---

## Environment Variable Reference

All variables are read via `python-decouple` from a `.env` file in the project root or from real environment variables.

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes | insecure dev key | Django secret key — generate a strong random value for production |
| `DEBUG` | No | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated list of allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | Prod | _(empty)_ | Comma-separated list of trusted origins for CSRF (e.g. `https://example.nasa.gov`) |
| `SCRIPT_NAME` | Prod | _(empty)_ | URL prefix when deployed at a sub-path (e.g. `/prompt-exchange`) |
| `ACCOUNT_DEFAULT_HTTP_PROTOCOL` | Prod | `http` | Set to `https` in production for correct OAuth redirect URIs |
| `DB_NAME` | Prod | — | PostgreSQL database name |
| `DB_USER` | Prod | — | PostgreSQL user |
| `DB_PASSWORD` | Prod | — | PostgreSQL password |
| `DB_HOST` | Prod | `localhost` | PostgreSQL host |
| `DB_PORT` | Prod | `5432` | PostgreSQL port |
| `EMAIL_BACKEND` | No | console backend | Django email backend class |
| `EMAIL_HOST` | No | `localhost` | SMTP server hostname |
| `EMAIL_PORT` | No | `587` | SMTP port |
| `EMAIL_USE_TLS` | No | `True` | Enable STARTTLS |
| `EMAIL_HOST_USER` | No | _(empty)_ | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | _(empty)_ | SMTP password |
| `DEFAULT_FROM_EMAIL` | No | `noreply@nasa-prompts.gov` | Default sender address |

---

## Sub-path Deployment

The application supports being served at a sub-path (e.g., `/prompt-exchange`) alongside other applications on the same hostname. Two settings work together to make this work:

- **`SCRIPT_NAME`** in `.env` — tells Django to prefix all reversed URLs with this path. It is passed to Django as `FORCE_SCRIPT_NAME`.
- **Nginx rewrite** in `nginx.conf` — strips the prefix before forwarding requests to Gunicorn, so Django always sees clean paths internally.

If you change the sub-path, update both the `SCRIPT_NAME` value in `.env` **and** the `location` block and static/media `alias` paths in `nginx.conf`.

To deploy at the root path (no sub-path), leave `SCRIPT_NAME` unset or empty and update the Nginx `location` block accordingly.


## License

The EarthRISE Toolkit is distributed by EarthRISE under the terms of the MIT License. See
[LICENSE](https://github.com/NASA-EarthRISE/earthrise-toolkit_EarthRISE-Prompt-Exchange/blob/main/LICENSE) in this directory for more information.