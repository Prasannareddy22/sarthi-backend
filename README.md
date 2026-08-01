# Sarthi Backend

FastAPI service that scores a citizen profile against welfare schemes and stores each submission.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

With no configuration the API writes to a local SQLite file (`sarthi.db`), so it runs with zero setup.

## Database

Set `DATABASE_URL` to use Postgres (copy `.env.example` to `.env`):

```
DATABASE_URL=postgresql://user:password@host:5432/sarthi
```

`postgres://` URLs from managed providers are normalised to `postgresql://` automatically. Tables are
created on startup from the models in `db_models.py`:

- `users` — registered accounts; passwords are stored only as a bcrypt hash.
- `citizen_profiles` — every field of a submitted profile, the derived `caste_group`, the run summary, `created_at` and the `user_id` of the submitter when signed in.
- `eligibility_results` — one row per scheme for a profile, with its score and the full result JSON.

Set `JWT_SECRET` to a long random string in production.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register` | Create an account, returns a JWT and the user |
| POST | `/api/auth/login` | Sign in, returns a JWT and the user |
| GET | `/api/auth/me` | The signed-in user |
| GET | `/api/auth/users` | Registered accounts (no password hashes) |
| POST | `/api/match-schemes` | Score a profile, store it, return `profile_id` plus the results |
| GET | `/api/my-profiles` | The signed-in user's submissions |
| GET | `/api/profiles` | Recent submissions, newest first (`limit`, `offset`) |
| GET | `/api/profiles/{id}` | One stored profile with the results captured at submission |
| POST | `/api/extract-profile` | Parse a speech transcript into partial form fields |

## Tests

```bash
pytest
```
