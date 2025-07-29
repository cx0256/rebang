import asyncio
from app.core.database import get_db
from app.models.user import User
from app.core.auth import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

async def create_admin():
    async for db in get_db():
        try:
            # Check if admin user already exists
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.email == 'admin@example.com'))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print('Admin user already exists')
                return
            
            # Create admin user
            hashed_password = get_password_hash('admin123')
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=hashed_password,
                is_active=True
            )
            db.add(admin_user)
            await db.commit()
            print('Admin user created successfully')
            print('Username: admin')
            print('Email: admin@example.com')
            print('Password: admin123')
        except Exception as e:
            print(f'Error creating admin user: {e}')
        break

if __name__ == '__main__':
    asyncio.run(create_admin())