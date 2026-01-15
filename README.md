# Drop Me Recycling API

A backend service for managing recycling transactions, user points, and machine interactions for Drop Me's smart recycling ecosystem.

## 🎯 Project Overview

This system implements the core recycling flow: **Scan → Recycle → Earn Points**

### Key Features

- ✅ User registration and authentication
- ✅ Recycling transaction processing
- ✅ Points calculation and management
- ✅ Duplicate transaction detection
- ✅ Complete audit trail
- ✅ RESTful API design
- ✅ OpenAPI/Swagger documentation
- ✅ Docker containerization

## 🏗️ Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  Django API  │─────▶│ PostgreSQL  │
│ (Machine/UI)│      │   (REST)     │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Business   │
                    │    Logic     │
                    │   (Services) │
                    └──────────────┘
```


### Data Models

**User**
- Extended Django User model
- Tracks total points
- Indexed for efficient lookups

**RecyclingTransaction**
- Records each recycling action
- Enforces duplicate prevention via DB constraint
- Stores transaction status and metadata

**PointsHistory**
- Immutable audit log
- Tracks every points change
- Links to originating transaction

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Setup & Run

```bash
# Clone the repository
git clone https://github.com/aliemadabdo/dropme-recycling-backend
cd dropme-recycling-backend

# Create environment file
cp .env.example .env

# Start services
docker-compose up -d

# Create superuser (optional)
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

## 📝 API Endpoints

### User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/register/` | Register new user | No |
| GET | `/api/users/me/` | Get user profile | Yes |
| PATCH | `/api/users/me/` | Update user profile | Yes |
| GET | `/api/users/me/stats/` | Get user statistics | Yes |

### Recycling Transactions

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/transactions/create/` | Create recycling transaction | Yes |
| GET | `/api/transactions/` | List user transactions | Yes |
| GET | `/api/transactions/{id}/` | Get transaction details | Yes |

### Points

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/points/history/` | View points history | Yes |

## 💡 Usage Examples

### Register a User

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "phone_number": "+1234567890",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

### Create Recycling Transaction

```bash
curl -X POST http://localhost:8000/api/transactions/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "material_type": "plastic",
    "item_code": "BOTTLE_12345",
    "machine_id": "MACHINE_001"
  }'
```

**Success Response (201):**
```json
{
  "message": "Transaction completed successfully",
  "transaction": {
    "id": "uuid-here",
    "material_type": "plastic",
    "points_earned": 10,
    "status": "completed",
    "created_at": "2026-01-14T12:00:00Z"
  },
  "user_points": 10
}
```

## 🛡️ Business Rules & Fraud Prevention

### 1. Duplicate Transaction Detection
- **Rule**: Each item code can only be recycled once per user
- **Implementation**: Database constraint + pre-check

### 2. Rate Limiting
- **Daily Limit**: Max 50 transactions per user per day (configurable)
- **Interval Limit**: Minimum 5 seconds between transactions (configurable)

### 3. Transaction Atomicity
- **Implementation**: Database transactions ensure:
  - Transaction record created
  - User points updated
  - History record created
  - All succeed or all fail



## 🎯 Assumptions

### Assumptions

1. **Authentication**: Using Django's built-in auth (in production, would use JWT/OAuth)
2. **Processing**: Assumed all data is processes on the server side and the machine only send the sensors raw data
3. **Machine IDs**: Optional field for tracking which machine processed the transaction
4. **Material Types**: Fixed set of recyclable materials
5. **Points Rules**: Simple point-per-item system (could be weight-based in real system)


### What Would I Improve With More Time

1. **Authentication**: Implement JWT tokens or session-based auth
2. **Caching**: Redis for frequently accessed data (user points, stats)
3. **Async Processing**: Celery for background tasks (notifications, analytics)
4. **Soft Deletes**: Retain historical data instead of hard deletes
5. **Admin Panel**: Enhanced Django admin for operations team




## 🔒 Security Considerations

- ✅ SQL injection protection (Django ORM)
- ✅ CSRF protection enabled
- ✅ Password validation
- ✅ Environment-based configuration
- ✅ Database constraints for data integrity

