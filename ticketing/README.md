# Ticketing System Documentation

A comprehensive support ticketing system for managing customer issues, requests, and interactions.

## Features

### Core Functionality
- **Ticket Management**: Create, update, view, and manage support tickets
- **Auto-generated Ticket Numbers**: Sequential ticket numbers (TKT-000001, TKT-000002, etc.)
- **Status Tracking**: New, Open, In Progress, Pending, Resolved, Closed, Reopened
- **Priority Levels**: Low, Medium, High, Urgent, Critical
- **Categories**: Technical, Billing, Product Inquiry, Feature Request, Bug Report, etc.

### Advanced Features
- **Comments System**: Internal and public comments on tickets
- **File Attachments**: Upload and manage ticket attachments
- **Audit Trail**: Complete history of all ticket changes
- **Assignment**: Assign tickets to specific users
- **SLA Tracking**: Due dates, estimated hours, actual hours
- **Metrics**: Response time, resolution time, overdue tracking
- **Tags**: Flexible tagging system for organization

## API Endpoints

### Base URL
All ticketing endpoints are prefixed with `/api/ticketing/`

### Tickets

#### List Tickets
```
GET /api/ticketing/tickets/
```

**Query Parameters:**
- `status`: Filter by status (new, open, in_progress, pending, resolved, closed, reopened)
- `priority`: Filter by priority (low, medium, high, urgent, critical)
- `category`: Filter by category
- `customer`: Filter by customer ID
- `assigned_to`: Filter by assigned user ID
- `my_tickets=true`: Show only tickets assigned to current user
- `unassigned=true`: Show only unassigned tickets
- `overdue=true`: Show only overdue tickets
- `created_after`: Filter by creation date (YYYY-MM-DD)
- `created_before`: Filter by creation date (YYYY-MM-DD)
- `search`: Search in ticket number, subject, description, tags

**Example:**
```bash
GET /api/ticketing/tickets/?status=open&priority=high
GET /api/ticketing/tickets/?my_tickets=true
GET /api/ticketing/tickets/?search=login%20issue
```

#### Create Ticket
```
POST /api/ticketing/tickets/
Content-Type: application/json

{
  "subject": "Cannot login to account",
  "description": "User is experiencing login issues after password reset",
  "priority": "high",
  "category": "technical",
  "customer": 1,
  "assigned_to": 2,
  "due_date": "2024-12-31T23:59:59Z",
  "estimated_hours": 2.5,
  "tags": "login, authentication, urgent"
}
```

#### Get Ticket Details
```
GET /api/ticketing/tickets/{id}/
```

Returns full ticket details including:
- All basic information
- Related customer details
- Assigned user details
- All comments
- All attachments
- Complete history
- Calculated metrics (response time, resolution time, overdue status)

#### Update Ticket
```
PUT /api/ticketing/tickets/{id}/
PATCH /api/ticketing/tickets/{id}/

{
  "status": "in_progress",
  "priority": "urgent",
  "actual_hours": 3.0
}
```

#### Delete Ticket
```
DELETE /api/ticketing/tickets/{id}/
```

### Custom Ticket Actions

#### Assign Ticket
```
POST /api/ticketing/tickets/{id}/assign/

{
  "user_id": 2
}
```

#### Change Status
```
POST /api/ticketing/tickets/{id}/change_status/

{
  "status": "resolved"
}
```

#### Add Comment
```
POST /api/ticketing/tickets/{id}/add_comment/

{
  "content": "Issue has been resolved by resetting the cache",
  "is_internal": false
}
```

#### Add Attachment
```
POST /api/ticketing/tickets/{id}/add_attachment/
Content-Type: multipart/form-data

file: [binary file data]
description: "Screenshot of error message"
```

### Ticket Lists

#### My Tickets
```
GET /api/ticketing/tickets/my_tickets/
```

#### Unassigned Tickets
```
GET /api/ticketing/tickets/unassigned/
```

#### Overdue Tickets
```
GET /api/ticketing/tickets/overdue/
```

#### Ticket Statistics
```
GET /api/ticketing/tickets/statistics/
```

Returns comprehensive statistics:
```json
{
  "total_tickets": 150,
  "by_status": {
    "new": 10,
    "open": 25,
    "in_progress": 30,
    "pending": 15,
    "resolved": 50,
    "closed": 20
  },
  "by_priority": {
    "low": 40,
    "medium": 60,
    "high": 30,
    "urgent": 15,
    "critical": 5
  },
  "by_category": {
    "technical": 80,
    "billing": 20,
    "product": 30,
    ...
  },
  "overdue_count": 5,
  "unassigned_count": 12,
  "my_tickets_count": 8,
  "avg_resolution_time_hours": 24.5
}
```

### Comments

#### List Comments
```
GET /api/ticketing/comments/
GET /api/ticketing/comments/?ticket=1
GET /api/ticketing/comments/?is_internal=true
```

#### Create Comment
```
POST /api/ticketing/comments/

{
  "ticket": 1,
  "content": "Following up with customer",
  "is_internal": true
}
```

### Attachments

#### List Attachments
```
GET /api/ticketing/attachments/
GET /api/ticketing/attachments/?ticket=1
```

#### Upload Attachment
```
POST /api/ticketing/attachments/
Content-Type: multipart/form-data

ticket: 1
file: [binary file data]
description: "Error log file"
```

### History

#### View Ticket History
```
GET /api/ticketing/history/
GET /api/ticketing/history/?ticket=1
GET /api/ticketing/history/?action=status_changed
```

## Models

### Ticket
- `ticket_number`: Auto-generated unique identifier
- `subject`: Ticket title
- `description`: Detailed description
- `status`: Current status
- `priority`: Priority level
- `category`: Ticket category
- `customer`: Related customer (FK)
- `assigned_to`: Assigned user (FK)
- `created_by`: User who created ticket (FK)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `resolved_at`: Resolution timestamp
- `closed_at`: Closure timestamp
- `due_date`: SLA due date
- `estimated_hours`: Estimated work hours
- `actual_hours`: Actual work hours
- `tags`: Comma-separated tags

### TicketComment
- `ticket`: Related ticket (FK)
- `author`: Comment author (FK)
- `content`: Comment text
- `is_internal`: Internal note flag
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### TicketAttachment
- `ticket`: Related ticket (FK)
- `file`: Uploaded file
- `filename`: Original filename
- `file_size`: File size in bytes
- `uploaded_by`: User who uploaded (FK)
- `uploaded_at`: Upload timestamp
- `description`: File description

### TicketHistory
- `ticket`: Related ticket (FK)
- `user`: User who made the change (FK)
- `action`: Type of action
- `field_name`: Changed field
- `old_value`: Previous value
- `new_value`: New value
- `timestamp`: When change occurred

## Admin Interface

The ticketing system includes a comprehensive Django admin interface with:

- **Color-coded status and priority badges**
- **Inline editing of comments and attachments**
- **Complete audit trail view**
- **Advanced filtering and searching**
- **Overdue ticket highlighting**
- **Human-readable file sizes**
- **Autocomplete for customer and user selection**

Access at: `/admin/ticketing/`

## Usage Examples

### Python (Django Shell)
```python
from ticketing.models import Ticket
from crm.models import Customer
from django.contrib.auth.models import User

# Create a ticket
customer = Customer.objects.first()
user = User.objects.first()

ticket = Ticket.objects.create(
    subject="Product inquiry",
    description="Customer wants to know about pricing",
    customer=customer,
    priority="medium",
    category="product",
    created_by=user
)

# Add a comment
from ticketing.models import TicketComment
comment = TicketComment.objects.create(
    ticket=ticket,
    author=user,
    content="Sent pricing information via email",
    is_internal=False
)

# Change status
ticket.status = "resolved"
ticket.save()
```

### JavaScript (Fetch API)
```javascript
// Get all high priority tickets
fetch('/api/ticketing/tickets/?priority=high', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
})
.then(response => response.json())
.then(data => console.log(data));

// Create a new ticket
fetch('/api/ticketing/tickets/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    subject: 'Bug report',
    description: 'Application crashes on startup',
    priority: 'urgent',
    category: 'bug',
    customer: 1
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Add a comment
fetch('/api/ticketing/tickets/1/add_comment/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    content: 'Working on this issue now',
    is_internal: false
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Permissions

All ticketing endpoints require authentication. The default permission class is `IsAuthenticated`.

## Best Practices

1. **Always set a priority** when creating tickets
2. **Use tags** for better organization and searchability
3. **Add internal notes** for team communication
4. **Set due dates** for time-sensitive issues
5. **Track actual hours** for billing and analytics
6. **Use proper categories** for better reporting
7. **Update status regularly** to keep customers informed
8. **Add detailed descriptions** to avoid back-and-forth
9. **Attach relevant files** (screenshots, logs, etc.)
10. **Review history** to understand ticket progression

## Integration with Other Apps

The ticketing system integrates with:
- **CRM**: Tickets are linked to customers
- **Dashboard**: Ticket statistics can be displayed
- **Session Security**: All API calls are protected by session management

## Future Enhancements

Potential additions:
- Email notifications on ticket updates
- Automated ticket assignment based on category
- SLA violation alerts
- Customer portal for ticket viewing
- Ticket templates for common issues
- Knowledge base integration
- Bulk ticket operations
- Advanced reporting and analytics
