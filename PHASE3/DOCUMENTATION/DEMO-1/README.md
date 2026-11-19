# Team Directory API

A FastAPI service for creating team members, listing all members, and finding
members by team. SQLAlchemy stores records in SQLite using `team_directory.db`.

Each `TeamMember` has an automatically generated integer `id` and three required
string fields: `name`, `team`, and `role`.

## Install Dependencies

Use Python 3.10 or newer; the project has been verified with Python 3.12.
Run all commands from the project root (the directory containing `main.py`).
SQLite is included with Python; no separate database server is required.

### Windows (PowerShell)

Install Python with the Windows Python launcher available, then run:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Ubuntu Linux

Install Python and virtual environment support if needed:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Create the environment and install the requirements:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The requirements include FastAPI, SQLAlchemy, Pydantic, and Uvicorn. These commands
use the virtual environment directly, so activation is not required.

## Run on Port 8020

Windows (PowerShell):

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8020 --reload
```

Ubuntu Linux:

```bash
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8020 --reload
```

The service is available at <http://127.0.0.1:8020>. Open the Swagger UI at
<http://127.0.0.1:8020/docs>. There is no handler for `/`, so visiting the base
URL alone returns 404.

Startup creates the database and tables if they do not exist. The database path
is relative to the working directory, so start the service from the project root
to consistently use the same database. Records persist across restarts.

`--reload` enables automatic reloads for local development. Stop the server with
`Ctrl+C`.

## Endpoints

| Method | Path | Function | Behavior | Status codes |
| --- | --- | --- | --- | --- |
| POST | `/team/` | `create_member` | Creates and returns a member, including its generated `id`. | `201 Created`; `422 Unprocessable Entity` for invalid request data |
| GET | `/team/` | `list_members` | Returns all members, or `[]` if the directory is empty. | `200 OK` |
| GET | `/team/by-team/{team_name}` | `list_members_by_team` | Returns members whose team matches the supplied name. | `200 OK`; `404 Not Found` if no members match |

The table lists normal application and request-validation responses. Unhandled
database errors can result in `500 Internal Server Error`.

## Manual Testing with Swagger UI

There is no automated test suite yet. With the server running, use
<http://127.0.0.1:8020/docs> for these manual checks. Expand each operation, select
**Try it out**, fill in its inputs, and select **Execute**. Inspect the response
code and response body.

1. **List existing members.** Execute `GET /team/`. Expect `200` and a JSON array.
   A fresh database returns `[]`; an existing database may already contain members.

2. **Create a member.** Execute `POST /team/` with this request body:

   ```json
   {
     "name": "Alice Morgan",
     "team": "Engineering",
     "role": "Developer"
   }
   ```

   Expect `201` and an object containing these values plus an integer `id`.
   Do not assume the generated ID is always `1`.

3. **Create a member in another team.** Repeat the POST with a different name,
   `"team": "Design"`, and `"role": "Designer"`. Expect `201`.

4. **List all members again.** Execute `GET /team/`. Expect `200` and an array
   containing both newly created members, along with any existing records.

5. **Filter by team.** Execute `GET /team/by-team/{team_name}` with `team_name`
   set to `Engineering`. Expect `200` and an array containing the member from
   step 2. Every returned member should have `"team": "Engineering"`; the Design
   member must not appear. Use the same spelling and case as the stored team.

6. **Check a missing team.** Use a team name that does not exist in the database.
   Expect `404` and:

   ```json
   {
     "detail": "No members found for this team"
   }
   ```

7. **Check request validation.** Execute `POST /team/` with only
   `{"name": "Incomplete Member"}`. Expect `422` with validation details for the
   missing `team` and `role` fields. The invalid request should not create a member.

8. **Check persistence.** Stop and restart the server from the same directory,
   then execute `GET /team/`. The previously created members should still exist.

Each successful POST adds another record, including when its values duplicate an
existing member. The API has no update or delete endpoint, so manual test records
remain in the database.