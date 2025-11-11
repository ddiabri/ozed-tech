# Ozed Tech - Inventory, CRM & Ticketing System

A comprehensive Django-based business management system with inventory management, CRM, ticketing system, and advanced session security.

## Features

### 📦 Inventory Management
- Product categories and suppliers
- Stock tracking with low stock alerts
- Purchase orders and sales orders
- RFQs (Request for Quotes) and quote management
- Stock adjustments and inventory history

### 👥 CRM (Customer Relationship Management)
- Customer and contact management
- Interaction tracking
- Customer-linked purchase orders
- Advanced filtering and search

### 🎫 Ticketing System
- Auto-generated ticket numbers (TKT-000001, TKT-000002, etc.)
- Multiple status types and priority levels
- Customer integration
- Comments (public and internal)
- File attachments
- Complete audit trail
- SLA tracking and metrics
- Advanced filtering and statistics

### 🔐 Session Security
- Auto-logout after 30 minutes of inactivity
- Client-side activity tracking
- Session warning modal
- Complete session audit trail
- Secure cookie configuration

### 📊 Dashboard
- Overview statistics
- Inventory metrics
- Sales analytics
- Customer insights

## Technology Stack

- **Backend**: Django 5.2.8
- **API**: Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Django session authentication
- **Admin**: Django Admin with custom configurations

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- Git

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/ozed-tech.git
cd ozed-tech
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings
# Update SECRET_KEY, database credentials, etc.
```

5. **Set up PostgreSQL database**
```bash
# Create database
psql -U postgres
CREATE DATABASE "ozed-tech";
\q
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Create test data (optional)**
```bash
python create_test_tickets.py
python setup_permissions.py
```

9. **Run the development server**
```bash
python manage.py runserver
```

10. **Access the application**
- API Root: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/
- Ticketing: http://localhost:8000/api/ticketing/tickets/

## Project Structure

```
ozed-tech/
├── ozed_tech_project/      # Main project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL configuration
│   ├── session_security.py # Session middleware
│   ├── session_views.py    # Session API
│   ├── permissions.py      # Custom permissions
│   ├── static/             # Static files
│   └── templates/          # HTML templates
├── inventory/              # Inventory management app
├── crm/                    # CRM app
├── ticketing/              # Ticketing system app
├── dashboard/              # Dashboard app
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## API Documentation

### Authentication
All API endpoints require authentication. Use Django session authentication or basic authentication.

### Main Endpoints

#### Inventory
- `GET /api/inventory/items/` - List all items
- `GET /api/inventory/categories/` - List categories
- `GET /api/inventory/suppliers/` - List suppliers
- `GET /api/inventory/purchase-orders/` - List purchase orders
- `GET /api/inventory/sales-orders/` - List sales orders

#### CRM
- `GET /api/crm/customers/` - List customers
- `GET /api/crm/contacts/` - List contacts
- `GET /api/crm/interactions/` - List interactions

#### Ticketing
- `GET /api/ticketing/tickets/` - List tickets
- `POST /api/ticketing/tickets/` - Create ticket
- `GET /api/ticketing/tickets/{id}/` - Get ticket details
- `POST /api/ticketing/tickets/{id}/assign/` - Assign ticket
- `POST /api/ticketing/tickets/{id}/add_comment/` - Add comment
- `GET /api/ticketing/tickets/statistics/` - Get statistics

#### Dashboard
- `GET /api/dashboard/overview/` - Overview statistics
- `GET /api/dashboard/inventory/` - Inventory metrics
- `GET /api/dashboard/sales/` - Sales analytics

#### Session Management
- `GET /api/session-status/` - Check session status
- `GET /api/session/` - Get session details
- `POST /api/session/extend/` - Extend session

For complete API documentation, see:
- `ticketing/README.md` - Ticketing API details
- `IMPLEMENTATION_SUMMARY.md` - Complete feature documentation

## Configuration

### Session Security Settings

In `ozed_tech_project/settings.py`:

```python
# Auto-logout after 30 minutes (1800 seconds)
SESSION_COOKIE_AGE = 1800
SESSION_INACTIVITY_TIMEOUT = 1800

# Show warning 5 minutes before expiration
SESSION_WARNING_THRESHOLD = 300

# Rolling timeout (resets with activity)
SESSION_SAVE_EVERY_REQUEST = True
```

### Security Settings for Production

Before deploying to production:

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Set `SESSION_COOKIE_SECURE = True` (requires HTTPS)
4. Set `CSRF_COOKIE_SECURE = True` (requires HTTPS)
5. Use strong `SECRET_KEY` (store in environment variable)
6. Configure database credentials via environment variables

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Creating Test Data
```bash
python create_test_tickets.py
```

## Admin Panel

Access the Django admin at: http://localhost:8000/admin/

Features:
- User and permission management
- Complete CRUD operations for all models
- Color-coded ticket status and priorities
- Advanced filtering and search
- Inline editing of related objects

## Security Features

- ✅ Session timeout and activity tracking
- ✅ CSRF protection
- ✅ XSS protection via HTTPOnly cookies
- ✅ SQL injection protection (Django ORM)
- ✅ Password validation
- ✅ Secure session cookies
- ✅ Complete audit trail for tickets
- ✅ Permission-based access control

## Future Enhancements

- [ ] Email notifications for ticket updates
- [ ] Two-factor authentication
- [ ] Customer portal
- [ ] Advanced reporting and analytics
- [ ] Mobile app
- [ ] Real-time notifications
- [ ] Integration with external systems

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software. All rights reserved.

## Support

For issues or questions, please contact the development team or open an issue on GitHub.

## Acknowledgments

- Django Framework
- Django REST Framework
- PostgreSQL
- All contributors and testers

---

**Version**: 1.0
**Last Updated**: 2025-11-11
**Status**: Active Development
