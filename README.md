# Drop Me Recycling Backend

A comprehensive backend service for Drop Me's smart recycling ecosystem, implementing core recycling flows, API design, tooling, and monitoring capabilities.

## 📋 Task Overview

This project implements **Tasks 1, 2, and 5** from the Drop Me internship assignment, with a proposal for **Task 6**:

- **Task 1**: Core Recycling Flow - Complete implementation
- **Task 2**: API Design + Validation Layer - Complete implementation
- **Task 5**: Workflow, Tooling & Ownership - Complete implementation
- **Task 6**: Wild Card - Proposal and partial implementation

---

## 🎯 Task 1: Core Recycling Flow

### Objective
Build a minimal but functional backend service supporting the **Scan → Recycle → Earn Points** flow.

### Implementation

#### User Registration & Authentication
- Extended Django User model with phone number and points tracking
- JWT-based authentication for secure API access
- Password validation and secure user creation

#### Recycling Transaction Processing
- **Transaction Creation**: API endpoint accepts material type, item code, weight in grams, and machine ID
- **Points Calculation**: **x point per matrial**  (matrial-based system) multiplied by the matrial weight
- **Duplicate Prevention**: Database constraints prevent same item recycling
- **Atomic Operations**: Database transactions ensure data consistency

#### Data Persistence
- PostgreSQL database with proper indexing
- Three main models: User, RecyclingTransaction, PointsHistory
- Audit trail for all points changes

### Key Features
- ✅ User registration and JWT authentication
- ✅ Recycling transaction processing with validation
- ✅ Points calculation and management
- ✅ Duplicate transaction detection
- ✅ Complete audit trail
- ✅ RESTful API design

### Architecture
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

---

## 🔧 Task 2: API Design + Validation Layer

### Objective
Create robust APIs with input validation, error handling, and clear response structures.

### Implementation

#### Input Validation
- **Django REST Framework serializers** for request validation
- **Field-level validation** for all API inputs

#### Error Handling
- **Structured error responses** with consistent format
- **Meaningful HTTP status codes** 
- **Detailed error messages** for debugging and user feedback

#### Business Rule Enforcement
- **Rate Limiting**: 50 transactions/day, 5-second intervals between transactions
- **Duplicate Prevention**: Database constraints + pre-validation checks
- **Data Integrity**: Transaction atomicity for points updates

#### API Endpoints
| Method | Endpoint | Description | Validation |
|--------|----------|-------------|------------|
| POST | `/api/users/register/` | User registration | Email, password confirmation |
| POST | `/api/auth/token/` | JWT token generation | Username/password required |
| POST | `/api/transactions/create/` | Create transaction | Material type, item code validation |
| GET | `/api/users/me/stats/` | User statistics | Authentication required |

### Response Structures
```json
// Success Response
{
  "message": "Transaction completed successfully",
  "transaction": {
    "id": "uuid-here",
    "material_type": "plastic",
    "weight_grams": 250.5,
    "points_earned": 250,
    "status": "completed"
  },
  "user_points": 250
}

// Error Response
{
  "error": "Duplicate transaction detected",
  "detail": "Item BOTTLE_12345 has already been recycled"
}
```

---

## 🛠️ Task 5: Workflow, Tooling & Ownership

### Objective
Demonstrate engineering maturity through tooling, testing, and deployment automation.

### Docker Containerization
- **Multi-stage Dockerfile** for optimized production builds
- **Docker Compose** for local development and production
- **Health checks** for both database and web services
- **Environment-based configuration** with `.env` files

### Development Tooling
- **Virtual environment** setup with `dropme_venv/`
- **Requirements management** with `requirements.txt`

### API Documentation
- **OpenAPI/Swagger** documentation with `drf-spectacular`
- **Interactive API explorer** at `/api/swagger/`
- **Schema endpoint** at `/api/schema/`
- **HTTP examples** in `api_examples.http`

### Setup Automation
- **setup.sh script** for one-command installation
- **Environment file templates** for easy configuration
- **Docker-based deployment** for consistent environments

### Code Quality
- **Django REST Framework** for consistent API patterns
- **Proper error handling** and logging
- **Database indexing** for performance
- **Security best practices** (CSRF, SQL injection prevention)

---

## 🚀 Task 6: Wild Card - Machine Health Monitoring (Proposal)

### Idea
Implement a proactive health monitoring system that transforms reactive maintenance into predictive operations.

### Proposed Implementation
- **Celery + Redis** for scheduled sensor/actuator checks
- **Real-time monitoring** of weight sensors, barcode scanners, compactor motors
- **Automated failure detection** with instant admin notifications
- **Machine status management** (active/maintenance/out-of-service)
- **Minimal data payloads** reporting only failures/threshold breaches

### Business Impact
- **99% uptime** through instant failure detection
- **40% cost reduction** in maintenance with targeted repairs
- **Enhanced UX** with reliable machine availability
- **Predictive insights** for hardware lifecycle management

### Current Status
- **Proposal documented** in `docs/TASK_6.md`
- **Architecture designed** for scalable monitoring
- **Ready for implementation** with Celery/Redis stack

---

## 🏃 Quick Start Guide

### Prerequisites
- Docker & Docker Compose
- Git

### Automated Setup
```bash
# Clone and setup in one command
git clone https://github.com/aliemadabdo/dropme-recycling-backend
cd dropme-recycling-backend
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# Clone repository
git clone https://github.com/aliemadabdo/dropme-recycling-backend
cd dropme-recycling-backend

# Start services
docker-compose up -d

# Create superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

### Access Points
- **API**: http://localhost:8080
- **Swagger Docs**: http://localhost:8080/api/swagger/

---

## 📚 API Usage Examples

### 1. User Registration
```bash
curl -X POST http://localhost:8080/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "phone_number": "+1234567890",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

### 2. Obtain JWT Token
```bash
curl -X POST http://localhost:8080/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

### 3. Create Recycling Transaction
```bash
curl -X POST http://localhost:8080/api/transactions/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "material_type": "plastic",
    "item_code": "BOTTLE_12345",
    "weight_grams": 250.5,
    "machine_id": "MACHINE_001"
  }'
```

### 4. Get User Statistics
```bash
curl -X GET http://localhost:8080/api/users/me/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🏗️ Technical Architecture

### Backend Stack
- **Framework**: Django 5.0.1 + Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL 15
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Deployment**: Docker + Docker Compose

### Business Rules and Assumptions

#### Points System
```python
# Points are calculated as: 1 point per gram of recycled material
POINTS_PER_GRAM = 1

# Example calculations:
# 250g plastic bottle = 250 points
# 15g aluminum can = 15 points
# 500g glass bottle = 500 points
```

#### Rate Limiting
```python
TRANSACTION_LIMITS = {
    'max_transactions_per_day': 50,
    'min_transaction_interval': timedelta(minutes=5),
}
```

---

## �️ Database Schema

### User Model
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- phone_number (Unique, Optional)
- total_points (Integer, Default: 0)
- created_at, updated_at (Timestamps)
```

### RecyclingTransaction Model
```sql
- id (UUID Primary Key)
- user (Foreign Key)
- material_type (CharField)
- item_code (CharField, Indexed)
- weight_grams (DecimalField, 8 digits, 2 decimal places)
- points_earned (IntegerField)
- status (CharField)
- machine_id (CharField, Optional)
- created_at (Timestamp)
- updated_at (Timestamp)
- error_message (TextField, Optional)
- UNIQUE(user_id, item_code) -- Prevents duplicates
```

### PointsHistory Model
```sql
- id (Primary Key)
- user (Foreign Key)
- transaction (Foreign Key)
- points_change (Integer)
- reason (CharField)
- created_at (Timestamp)
```

---

## �🔒 Security & Validation

### Authentication & Authorization
- JWT token-based authentication
- Password hashing with Django's PBKDF2
- CSRF protection enabled
- Session-based admin access

### Input Validation
- Serializer-based validation for all inputs
- Custom validators for business rules
- Database constraints for data integrity
- SQL injection prevention via ORM

### Business Rule Enforcement
- Duplicate transaction detection
- Rate limiting per user
- Transaction atomicity
- Audit trail for all changes

---


## 🔄 Future Improvements

1. **Task 6 Implementation**: Complete machine health monitoring system
2. **Caching Layer**: Redis for user stats and frequent queries
3. **Testing Suite**: Unit tests and integration tests
4. **CI/CD Pipeline**: GitHub Actions for automated testing
