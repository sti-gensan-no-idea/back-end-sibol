# Atuna API

A back-end of Atuna.

## Requirements

- [Python 3](https://www.python.org/downloads)
- [PostgreSQL](https://www.postgresql.org/download) (optional)
- [Git](https://git-scm.com/downloads)

## Getting Started

Follow the following steps to setup the project.

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```
2. Install uv (package installer and resolver):
```pip install uv```
 ```uv venv```


3. Activate the virtual environment:

   ```bash
   # Windows
   .\venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

4. Install all packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Get the `.env` file from the admin, and paste inside the root directory.

6. Run the project:

   ```bash
   uvicorn app.main:app
   ```

7. Open your browser and go to `http://localhost:8000/docs` to access the API documentation.

## License

This project is licensed under the terms described in the [LICENSE](./LICENSE) file.

```API Endpoints

Users

POST /api/v1/users/register - Register a new user
POST /api/v1/users/login - User login
GET /api/v1/users/me - Get current user info
GET /api/v1/users/{user_id} - Get a user by ID
GET /api/v1/users/ - Get a list of users (Admin/Sub-admin only)
PUT /api/v1/users/{user_id} - Update a user
DELETE /api/v1/users/{user_id} - Delete (deactivate) a user


Properties

POST /api/v1/properties/ - Create a new property
GET /api/v1/properties/{property_id} - Get a property by ID
GET /api/v1/properties/ - Get a list of properties
PUT /api/v1/properties/{property_id} - Update a property
DELETE /api/v1/properties/{property_id} - Delete a property
POST /api/v1/properties/{property_id}/generate-description - Generate AI property description
GET /api/v1/properties/{property_id}/ar-view - Get AR view data for a property


Contracts


POST /api/v1/contracts/ - Create a new contract
GET /api/v1/contracts/{contract_id} - Get a contract by ID
GET /api/v1/contracts/ - Get a list of contracts (Admin/Sub-admin/Agent only)
PUT /api/v1/contracts/{contract_id} - Update a contract
DELETE /api/v1/contracts/{contract_id} - Delete a contract
GET /api/v1/contracts/{contract_id}/analyze - Analyze contract with AI


Swagger API Documentation
FastAPI generates Swagger UI documentation at http://localhost:8000/docs
Includes endpoint descriptions, request/response schemas, and interactive testing
Use the "Authorize" button to input JWT tokens for protected endpoints

Test all CRUD operations directly in the Swagger UI


AR Implementation
Properties can include a 3D model URL (ar_model_url) for AR viewing
AR scene configuration (ar_scene_config) is generated on property creation/update
The /api/v1/properties/{id}/ar-view endpoint returns AR-compatible data
Supports WebXR or mobile AR frameworks (e.g., ARKit/ARCore) on the frontend
3D models should be stored in GLB format at the configured AR_MODEL_STORAGE_URL

Security
JWT authentication for all endpoints except /api/v1/users/register and /api/v1/users/login
Role-based access control (Admin/Sub-admin for most write operations, Agent/Client for read operations)
Password hashing with bcrypt
CORS middleware for cross-origin requests```