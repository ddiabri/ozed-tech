"""
Management command to populate the database with test data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from inventory.models import Category, Supplier, Item, PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem
from crm.models import Customer, Contact, Interaction


class Command(BaseCommand):
    help = 'Populate the database with test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            SalesOrderItem.objects.all().delete()
            SalesOrder.objects.all().delete()
            PurchaseOrderItem.objects.all().delete()
            PurchaseOrder.objects.all().delete()
            Interaction.objects.all().delete()
            Contact.objects.all().delete()
            Customer.objects.all().delete()
            Item.objects.all().delete()
            Supplier.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared!'))

        self.stdout.write('Starting data population...')

        # Create or get admin user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ozedtech.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user (password: admin123)'))
        else:
            self.stdout.write(f'Using existing admin user')

        # Create Categories
        self.stdout.write('Creating categories...')
        categories_data = [
            ('Electronics', 'Electronic devices and components'),
            ('Computer Hardware', 'Computer parts and accessories'),
            ('Office Supplies', 'General office supplies and stationery'),
            ('Furniture', 'Office and home furniture'),
            ('Software', 'Software licenses and subscriptions'),
            ('Networking', 'Network equipment and cables'),
            ('Storage', 'Storage devices and solutions'),
            ('Peripherals', 'Computer peripherals and accessories'),
        ]
        categories = []
        for name, desc in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  Created category: {name}')

        # Create Suppliers
        self.stdout.write('Creating suppliers...')
        suppliers_data = [
            ('TechVendor Inc', 'John Smith', 'john@techvendor.com', '+1-555-0101', '123 Tech Street, San Francisco, CA'),
            ('Global Electronics', 'Sarah Johnson', 'sarah@globalelectronics.com', '+1-555-0102', '456 Electronics Ave, New York, NY'),
            ('Office Depot Pro', 'Mike Wilson', 'mike@officedepotpro.com', '+1-555-0103', '789 Supply Road, Chicago, IL'),
            ('Hardware Solutions', 'Emily Davis', 'emily@hardwaresolutions.com', '+1-555-0104', '321 Hardware Blvd, Austin, TX'),
            ('Network Systems Co', 'David Brown', 'david@networksystems.com', '+1-555-0105', '654 Network Lane, Seattle, WA'),
        ]
        suppliers = []
        for name, contact, email, phone, address in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'contact_person': contact,
                    'email': email,
                    'phone': phone,
                    'address': address
                }
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'  Created supplier: {name}')

        # Create Items
        self.stdout.write('Creating inventory items...')
        items_data = [
            ('Laptop Dell XPS 15', 'DELL-XPS-15', 'High-performance laptop', categories[1], suppliers[0], 15, Decimal('1299.99'), 5),
            ('Laptop HP Pavilion', 'HP-PAV-14', '14-inch business laptop', categories[1], suppliers[1], 8, Decimal('899.99'), 5),
            ('Monitor 27" 4K', 'MON-27-4K', '4K Ultra HD monitor', categories[0], suppliers[0], 12, Decimal('399.99'), 3),
            ('Wireless Mouse', 'MSE-WIRELESS', 'Ergonomic wireless mouse', categories[7], suppliers[1], 45, Decimal('29.99'), 10),
            ('Mechanical Keyboard', 'KBD-MECH-RGB', 'RGB mechanical keyboard', categories[7], suppliers[0], 22, Decimal('89.99'), 10),
            ('Office Chair Premium', 'CHR-PREM-01', 'Ergonomic office chair', categories[3], suppliers[2], 5, Decimal('349.99'), 2),
            ('Standing Desk', 'DSK-STAND-01', 'Adjustable standing desk', categories[3], suppliers[2], 3, Decimal('599.99'), 2),
            ('USB-C Hub 7-Port', 'HUB-USBC-7', '7-port USB-C hub', categories[7], suppliers[1], 30, Decimal('49.99'), 8),
            ('External SSD 1TB', 'SSD-EXT-1TB', 'Portable SSD 1TB', categories[6], suppliers[3], 18, Decimal('129.99'), 5),
            ('Webcam HD Pro', 'CAM-HD-PRO', '1080p HD webcam', categories[7], suppliers[1], 25, Decimal('79.99'), 8),
            ('Headset Wireless', 'HEAD-WIRE-01', 'Noise-cancelling headset', categories[7], suppliers[0], 0, Decimal('149.99'), 5),
            ('Router WiFi 6', 'RTR-WIFI6', 'WiFi 6 router', categories[5], suppliers[4], 10, Decimal('199.99'), 3),
            ('Network Switch 24-Port', 'SW-24PORT', 'Managed 24-port switch', categories[5], suppliers[4], 4, Decimal('299.99'), 2),
            ('Paper A4 (500 sheets)', 'PAPER-A4-500', 'Premium A4 paper', categories[2], suppliers[2], 120, Decimal('8.99'), 20),
            ('Printer Ink Cartridge', 'INK-BK-XL', 'Black XL ink cartridge', categories[2], suppliers[2], 2, Decimal('34.99'), 5),
            ('Whiteboard Large', 'WB-LARGE-01', 'Large magnetic whiteboard', categories[2], suppliers[2], 6, Decimal('159.99'), 2),
            ('Cable HDMI 6ft', 'CBL-HDMI-6', 'Premium HDMI cable', categories[5], suppliers[1], 55, Decimal('12.99'), 15),
            ('Power Strip 6-Outlet', 'PWR-STRIP-6', '6-outlet surge protector', categories[0], suppliers[1], 35, Decimal('24.99'), 10),
            ('Docking Station', 'DOCK-USB-C', 'Universal USB-C docking', categories[7], suppliers[3], 7, Decimal('179.99'), 3),
            ('Monitor Arm Dual', 'ARM-DUAL-MON', 'Dual monitor arm mount', categories[3], suppliers[2], 9, Decimal('89.99'), 5),
        ]
        items = []
        for name, sku, desc, category, supplier, qty, price, threshold in items_data:
            item, created = Item.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'description': desc,
                    'category': category,
                    'supplier': supplier,
                    'quantity': qty,
                    'unit_price': price,
                    'low_stock_threshold': threshold
                }
            )
            items.append(item)
            if created:
                self.stdout.write(f'  Created item: {name} (Stock: {qty})')

        # Create Customers
        self.stdout.write('Creating customers...')
        customers_data = [
            ('Acme Corporation', 'active', 'Manufacturing', '100 Business Parkway, Boston, MA', 'Boston', 'MA', 'USA', '02101', Decimal('50000.00'), 'https://www.acmecorp.com'),
            ('TechStart Solutions', 'active', 'Technology', '200 Startup Ave, San Francisco, CA', 'San Francisco', 'CA', 'USA', '94105', Decimal('30000.00'), 'https://www.techstart.com'),
            ('Global Enterprises Ltd', 'active', 'Consulting', '300 Corporate Blvd, New York, NY', 'New York', 'NY', 'USA', '10001', Decimal('75000.00'), 'https://www.globalent.com'),
            ('SmallBiz Inc', 'prospect', 'Retail', '400 Main Street, Chicago, IL', 'Chicago', 'IL', 'USA', '60601', Decimal('15000.00'), 'https://www.smallbiz.com'),
            ('Enterprise Systems', 'active', 'IT Services', '500 Tech Drive, Austin, TX', 'Austin', 'TX', 'USA', '78701', Decimal('100000.00'), 'https://www.entsys.com'),
            ('Innovate Labs', 'prospect', 'Research', '600 Research Park, Seattle, WA', 'Seattle', 'WA', 'USA', '98101', Decimal('25000.00'), 'https://www.innovatelabs.com'),
            ('Premier Partners', 'active', 'Finance', '700 Financial Center, Miami, FL', 'Miami', 'FL', 'USA', '33101', Decimal('60000.00'), 'https://www.premierpartners.com'),
            ('Digital Dynamics', 'active', 'Marketing', '800 Creative Lane, Los Angeles, CA', 'Los Angeles', 'CA', 'USA', '90001', Decimal('40000.00'), 'https://www.digitaldynamics.com'),
        ]
        customers = []
        for company, cust_type, industry, addr, city, state, country, postal, credit, website in customers_data:
            customer, created = Customer.objects.get_or_create(
                company_name=company,
                defaults={
                    'customer_type': cust_type,
                    'industry': industry,
                    'address': addr,
                    'city': city,
                    'state': state,
                    'country': country,
                    'postal_code': postal,
                    'credit_limit': credit,
                    'website': website
                }
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'  Created customer: {company}')

        # Create Contacts
        self.stdout.write('Creating contacts...')
        contacts_data = [
            ('James', 'Anderson', 'CEO', 'james.anderson@acmecorp.com', '+1-555-1101', customers[0], True),
            ('Lisa', 'Martinez', 'CTO', 'lisa.martinez@techstart.com', '+1-555-1102', customers[1], True),
            ('Robert', 'Taylor', 'Procurement Manager', 'robert.taylor@globalent.com', '+1-555-1103', customers[2], True),
            ('Jennifer', 'White', 'Owner', 'jennifer.white@smallbiz.com', '+1-555-1104', customers[3], True),
            ('Michael', 'Harris', 'IT Director', 'michael.harris@entsys.com', '+1-555-1105', customers[4], True),
            ('Patricia', 'Clark', 'Operations Manager', 'patricia.clark@acmecorp.com', '+1-555-1106', customers[0], False),
            ('David', 'Lewis', 'Purchasing Agent', 'david.lewis@globalent.com', '+1-555-1107', customers[2], False),
        ]
        contacts = []
        for first, last, title, email, phone, customer, is_primary in contacts_data:
            contact, created = Contact.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'title': title,
                    'phone': phone,
                    'customer': customer,
                    'is_primary': is_primary
                }
            )
            contacts.append(contact)
            if created:
                self.stdout.write(f'  Created contact: {first} {last}')

        # Create Interactions
        self.stdout.write('Creating interactions...')
        interaction_types = ['call', 'email', 'meeting', 'note']
        interaction_subjects = [
            'Initial consultation call',
            'Product demonstration',
            'Pricing discussion',
            'Follow-up on quote',
            'Technical support request',
            'Order confirmation',
            'Delivery schedule review',
            'Quarterly business review'
        ]

        for i in range(15):
            days_ago = random.randint(1, 60)
            Interaction.objects.create(
                customer=random.choice(customers[:5]),  # Active customers
                contact=random.choice(contacts),
                interaction_type=random.choice(interaction_types),
                subject=random.choice(interaction_subjects),
                description=f'Discussion regarding {random.choice(interaction_subjects).lower()}. Customer expressed interest in our products.',
                interaction_date=timezone.now() - timedelta(days=days_ago),
                user=user
            )
        self.stdout.write(f'  Created 15 interactions')

        # Create Purchase Orders
        self.stdout.write('Creating purchase orders...')
        for i in range(5):
            days_ago = random.randint(10, 90)
            order_date = date.today() - timedelta(days=days_ago)
            expected_date = order_date + timedelta(days=random.randint(7, 21))

            po = PurchaseOrder.objects.create(
                order_number=f'PO-2025-{1000 + i}',
                supplier=random.choice(suppliers),
                order_date=order_date,
                expected_delivery_date=expected_date,
                status=random.choice(['draft', 'pending', 'approved', 'received']),
                notes=f'Purchase order for inventory restocking - {order_date.strftime("%B %Y")}'
            )

            # Add items to purchase order
            num_items = random.randint(2, 5)
            selected_items = random.sample(items, num_items)
            for item in selected_items:
                quantity = random.randint(5, 20)
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    item=item,
                    quantity=quantity,
                    unit_price=item.unit_price
                )

            self.stdout.write(f'  Created purchase order: {po.order_number}')

        # Create Sales Orders
        self.stdout.write('Creating sales orders...')
        statuses = ['draft', 'confirmed', 'processing', 'shipped', 'delivered']
        payment_statuses = ['unpaid', 'partial', 'paid']

        for i in range(12):
            days_ago = random.randint(1, 45)
            order_date = date.today() - timedelta(days=days_ago)
            expected_date = order_date + timedelta(days=random.randint(3, 14))

            status_choice = random.choice(statuses)
            payment_choice = random.choice(payment_statuses)

            # More recent orders more likely to be in earlier stages
            if days_ago < 7:
                status_choice = random.choice(['draft', 'confirmed', 'processing'])
            elif days_ago < 21:
                status_choice = random.choice(['processing', 'shipped'])
            else:
                status_choice = random.choice(['delivered', 'shipped'])

            so = SalesOrder.objects.create(
                order_number=f'SO-2025-{2000 + i}',
                customer=random.choice(customers[:5]),  # Active customers only
                contact=random.choice(contacts),
                order_date=order_date,
                expected_delivery_date=expected_date,
                status=status_choice,
                payment_status=payment_choice,
                discount=Decimal(random.choice([0, 50, 100, 200])),
                tax=Decimal('0.00'),
                shipping_cost=Decimal(random.choice([0, 25, 50, 75])),
                notes=f'Sales order for {order_date.strftime("%B %Y")} - Customer requested expedited shipping' if random.random() > 0.5 else ''
            )

            # Add items to sales order (only items with stock)
            available_items = [item for item in items if item.quantity > 0]
            num_items = random.randint(1, 4)
            selected_items = random.sample(available_items, min(num_items, len(available_items)))

            for item in selected_items:
                quantity = random.randint(1, min(5, item.quantity))
                discount_amount = Decimal(random.choice([0, 0, 0, 10, 20]))  # Most items no discount

                SalesOrderItem.objects.create(
                    sales_order=so,
                    item=item,
                    quantity=quantity,
                    unit_price=item.unit_price,
                    discount=discount_amount
                )

            so.calculate_totals()

            # Calculate tax (8% sales tax)
            so.tax = (so.subtotal - so.discount) * Decimal('0.08')
            so.calculate_totals()

            self.stdout.write(f'  Created sales order: {so.order_number} - {so.get_status_display()}')

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Categories: {Category.objects.count()}')
        self.stdout.write(f'Suppliers: {Supplier.objects.count()}')
        self.stdout.write(f'Items: {Item.objects.count()}')
        self.stdout.write(f'Customers: {Customer.objects.count()}')
        self.stdout.write(f'Contacts: {Contact.objects.count()}')
        self.stdout.write(f'Interactions: {Interaction.objects.count()}')
        self.stdout.write(f'Purchase Orders: {PurchaseOrder.objects.count()}')
        self.stdout.write(f'Sales Orders: {SalesOrder.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\nAdmin user: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('Server: http://127.0.0.1:8000/'))
