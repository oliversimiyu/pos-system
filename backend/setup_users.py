from django.contrib.auth import get_user_model

User = get_user_model()

# Update admin user to have admin role
try:
    admin = User.objects.get(username='admin')
    admin.role = 'admin'
    admin.save()
    print(f"✓ Updated {admin.username} to admin role")
except User.DoesNotExist:
    print("✗ Admin user not found")

# Create a test cashier if doesn't exist
cashier_username = 'cashier'
if not User.objects.filter(username=cashier_username).exists():
    cashier = User.objects.create_user(
        username=cashier_username,
        password='cashier123',
        first_name='Test',
        last_name='Cashier',
        email='cashier@pos.com',
        role='cashier'
    )
    print(f"✓ Created cashier user: {cashier_username} / cashier123")
else:
    cashier = User.objects.get(username=cashier_username)
    cashier.role = 'cashier'
    cashier.save()
    print(f"✓ Updated {cashier_username} to cashier role")

print("\nUser Accounts:")
print("-" * 50)
for user in User.objects.all():
    print(f"{user.username:15} | {user.role:10} | Active: {user.is_active}")
