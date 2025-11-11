import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozed_tech_project.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import Item, Category, Supplier, PurchaseOrder, PurchaseOrderItem
from crm.models import Customer, Contact, Interaction

# Create user groups with specific permissions
def setup_groups():
    """
    Creates user groups with predefined permissions
    """

    # 1. Inventory Manager - Full access to inventory
    inventory_manager, created = Group.objects.get_or_create(name='Inventory Manager')
    if created:
        print("[+] Created 'Inventory Manager' group")
        # Add all inventory permissions
        inventory_permissions = Permission.objects.filter(
            content_type__app_label='inventory'
        )
        inventory_manager.permissions.set(inventory_permissions)
        print(f"  Added {inventory_permissions.count()} inventory permissions")

    # 2. Sales Team - CRM access + view inventory
    sales_team, created = Group.objects.get_or_create(name='Sales Team')
    if created:
        print("[+] Created 'Sales Team' group")
        # All CRM permissions
        crm_permissions = Permission.objects.filter(
            content_type__app_label='crm'
        )
        # View-only inventory permissions
        inventory_view_permissions = Permission.objects.filter(
            content_type__app_label='inventory',
            codename__startswith='view_'
        )
        sales_team.permissions.set(list(crm_permissions) + list(inventory_view_permissions))
        print(f"  Added {crm_permissions.count()} CRM permissions")
        print(f"  Added {inventory_view_permissions.count()} inventory view permissions")

    # 3. Warehouse Staff - Manage items and purchase orders
    warehouse_staff, created = Group.objects.get_or_create(name='Warehouse Staff')
    if created:
        print("[+] Created 'Warehouse Staff' group")
        # Item and PurchaseOrder permissions
        item_ct = ContentType.objects.get_for_model(Item)
        po_ct = ContentType.objects.get_for_model(PurchaseOrder)
        poi_ct = ContentType.objects.get_for_model(PurchaseOrderItem)

        warehouse_permissions = Permission.objects.filter(
            content_type__in=[item_ct, po_ct, poi_ct]
        )
        # Add view permissions for categories and suppliers
        category_view = Permission.objects.filter(
            content_type__model='category',
            codename__startswith='view_'
        )
        supplier_view = Permission.objects.filter(
            content_type__model='supplier',
            codename__startswith='view_'
        )

        warehouse_staff.permissions.set(
            list(warehouse_permissions) + list(category_view) + list(supplier_view)
        )
        print(f"  Added warehouse-related permissions")

    # 4. Read Only - View access to everything
    read_only, created = Group.objects.get_or_create(name='Read Only')
    if created:
        print("[+] Created 'Read Only' group")
        # All view permissions
        view_permissions = Permission.objects.filter(
            codename__startswith='view_'
        )
        read_only.permissions.set(view_permissions)
        print(f"  Added {view_permissions.count()} view permissions")

    print("\n" + "="*60)
    print("Groups created successfully!")
    print("="*60)
    print("\nTo assign users to groups:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Authentication and Authorization > Users")
    print("3. Select a user")
    print("4. In 'Groups' section, select appropriate groups")
    print("5. Save")
    print("\nAvailable groups:")
    print("  - Inventory Manager - Full inventory access")
    print("  - Sales Team - Full CRM + view inventory")
    print("  - Warehouse Staff - Manage items & purchase orders")
    print("  - Read Only - View-only access to everything")
    print("="*60)


if __name__ == '__main__':
    setup_groups()
