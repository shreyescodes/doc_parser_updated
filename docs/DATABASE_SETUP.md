# Database Setup Guide

This guide will help you set up the database for the LP Document Parser application.

## Prerequisites

1. **PostgreSQL** installed and running
2. **Python 3.11+** installed
3. **pip** package manager

## Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Copy environment file:**
```bash
cp env.example .env
```

2. **Edit `.env` file with your database credentials:**
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/doc_parser
DB_HOST=localhost
DB_PORT=5432
DB_NAME=doc_parser
DB_USER=your_username
DB_PASSWORD=your_password
```

3. **Run the automated setup script:**
```bash
python scripts/setup_db.py
```

This script will:
- Create necessary directories
- Create the database if it doesn't exist
- Run database migrations
- Create a default admin user

### Option 2: Manual Setup

#### Step 1: Create Database

Connect to PostgreSQL and create the database:

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE doc_parser;

-- Create user (optional)
CREATE USER doc_parser_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE doc_parser TO doc_parser_user;

-- Exit psql
\q
```

#### Step 2: Configure Environment

Copy and edit the environment file:

```bash
cp env.example .env
```

Edit `.env` with your database settings:

```bash
DATABASE_URL=postgresql://doc_parser_user:your_password@localhost:5432/doc_parser
DB_HOST=localhost
DB_PORT=5432
DB_NAME=doc_parser
DB_USER=doc_parser_user
DB_PASSWORD=your_password
```

#### Step 3: Run Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### Step 4: Create Admin User

```bash
python scripts/create_user.py admin admin@example.com admin123 --admin
```

## Database Schema

The application uses the following main tables:

### Users
- User authentication and authorization
- Admin and regular user roles

### Documents
- Main document metadata
- Processing status and results

### Capital Call Details
- Extracted data from capital call notices
- Call amounts, dates, fund information

### Distribution Details
- Extracted data from distribution notices
- Distribution amounts, performance metrics

### Processing Logs
- Audit trail of document processing
- Error logs and processing times

### Document Templates
- Configurable extraction rules
- Field mappings for different document types

## Migration Commands

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description of changes"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Apply one migration at a time
alembic upgrade +1
```

### Rollback Migrations

```bash
# Rollback to previous migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Check Migration Status

```bash
# Show current migration status
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show <revision_id>
```

## Database Management Scripts

### Reset Database

⚠️ **Warning: This will delete all data!**

```bash
python scripts/reset_db.py
```

### Create New User

```bash
python scripts/create_user.py username email password [--admin]
```

### Initialize Database

```bash
python scripts/init_db.py
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists
- Check firewall settings

#### 2. Migration Failed

**Error:** `alembic.util.exc.CommandError: Can't locate revision identified by 'xxxxx'`

**Solutions:**
- Check migration history: `alembic history`
- Reset database: `python scripts/reset_db.py`
- Manually fix migration files

#### 3. Permission Denied

**Error:** `psycopg2.ProgrammingError: permission denied for database`

**Solutions:**
- Grant proper permissions to database user
- Check user roles and privileges
- Use superuser for initial setup

### Database Maintenance

#### Backup Database

```bash
# Create backup
pg_dump -h localhost -U username -d doc_parser > backup.sql

# Restore backup
psql -h localhost -U username -d doc_parser < backup.sql
```

#### Monitor Database

```bash
# Check database size
psql -d doc_parser -c "SELECT pg_size_pretty(pg_database_size('doc_parser'));"

# Check table sizes
psql -d doc_parser -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

## Production Considerations

### Security

1. **Change default passwords**
2. **Use strong database credentials**
3. **Enable SSL connections**
4. **Regular security updates**
5. **Backup encryption**

### Performance

1. **Database indexing**
2. **Connection pooling**
3. **Query optimization**
4. **Regular maintenance**

### Monitoring

1. **Database metrics**
2. **Slow query logging**
3. **Connection monitoring**
4. **Disk space monitoring**

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Full database connection string | - |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | doc_parser |
| `DB_USER` | Database username | - |
| `DB_PASSWORD` | Database password | - |
| `SECRET_KEY` | JWT secret key | - |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |

## Support

If you encounter issues:

1. Check the logs in `logs/app.log`
2. Verify environment configuration
3. Test database connectivity
4. Review migration history
5. Check PostgreSQL logs

For additional help, refer to the main README.md or create an issue in the repository.
