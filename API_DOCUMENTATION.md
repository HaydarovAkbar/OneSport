# OneSport API Documentation

## Overview

OneSport is a comprehensive HR/Recruiting platform that connects clients (companies) with recruiters and candidates. This API documentation provides detailed information about all available endpoints, authentication, and usage examples.

## Base URL

```
Production: https://api.onesport.com
Development: http://localhost:8000/api
```

## Authentication

OneSport uses JWT (JSON Web Tokens) for authentication. All authenticated requests must include the JWT token in the Authorization header.

### Authentication Flow

1. **Register**: Create a new user account
2. **Login**: Obtain JWT tokens
3. **Access Protected Resources**: Use access token in requests
4. **Refresh Token**: Get new access token when expired

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint:** `POST /auth/registration/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "CLIENT"
}
```

**Response:**
```json
{
  "key": "access_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "CLIENT"
  }
}
```

**Status Codes:**
- `201 Created`: User successfully created
- `400 Bad Request`: Invalid data provided
- `409 Conflict`: User already exists

### Login User

Authenticate user and obtain JWT tokens.

**Endpoint:** `POST /auth/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "CLIENT"
  }
}
```

**Status Codes:**
- `200 OK`: Authentication successful
- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Authentication failed

### Refresh Token

Get new access token using refresh token.

**Endpoint:** `POST /auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Logout User

Invalidate current session.

**Endpoint:** `POST /auth/logout/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "detail": "Successfully logged out"
}
```

---

## User Management

### Get Current User

Retrieve current authenticated user's information.

**Endpoint:** `GET /auth/user/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "CLIENT",
  "is_active": true,
  "date_joined": "2024-01-01T12:00:00Z"
}
```

### Update User Profile

Update current user's profile information.

**Endpoint:** `PATCH /auth/user/`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "role": "CLIENT"
}
```

For complete API documentation, please refer to the full documentation at: https://docs.onesport.com
