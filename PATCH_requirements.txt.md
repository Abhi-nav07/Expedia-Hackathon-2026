# Patch for backend/requirements.txt (from Module 1)

Pydantic's EmailStr type (used in app/schemas/auth.py) requires an extra
package that wasn't needed until this module. Add this line:

    email-validator==2.2.0

Place it under the "Validation / Config" section, e.g.:

    # Validation / Config
    pydantic==2.9.2
    pydantic-settings==2.5.2
    email-validator==2.2.0

Then rebuild the backend image:

    docker-compose build backend
