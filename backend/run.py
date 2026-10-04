import os
from app import create_app
from app.models import db, Role, User, RoomType, Room

app = create_app()

def init_db_defaults():
    """Seed initial core system roles and room types if database is empty."""
    with app.app_context():
        try:
            db.create_all()
            
            # Check default roles
            if Role.query.count() == 0:
                admin_role = Role(role_name='Admin', description='Full System Administrator Access')
                manager_role = Role(role_name='Hotel Manager', description='Operations & Revenue Analytics Access')
                receptionist_role = Role(role_name='Receptionist', description='Front Desk Booking Management')
                db.session.add_all([admin_role, manager_role, receptionist_role])
                db.session.commit()
                print("[OK] Default system roles created.")

            # Check default admin user
            if User.query.count() == 0:
                admin_role = Role.query.filter_by(role_name='Admin').first()
                admin_user = User(
                    full_name='Admin Manager',
                    email='admin@hotelanalytics.com',
                    phone='9876543210',
                    role_id=admin_role.id
                )
                admin_user.set_password('Admin@123')
                db.session.add(admin_user)

                manager_role = Role.query.filter_by(role_name='Hotel Manager').first()
                mgr_user = User(
                    full_name='Revenue Manager',
                    email='manager@hotelanalytics.com',
                    phone='9876543211',
                    role_id=manager_role.id
                )
                mgr_user.set_password('Manager@123')
                db.session.add(mgr_user)
                
                db.session.commit()
                print("[OK] Default staff accounts created (admin@hotelanalytics.com / Admin@123).")

            # Check default room types
            if RoomType.query.count() == 0:
                types = [
                    RoomType(type_name='Standard Single', base_price=2500.00, capacity=1, description='Cozy single bed room with work desk and high-speed Wi-Fi', total_rooms=10),
                    RoomType(type_name='Deluxe Double', base_price=4500.00, capacity=2, description='Spacious room with king-size bed and city skyline view', total_rooms=15),
                    RoomType(type_name='Executive Suite', base_price=8500.00, capacity=3, description='Luxury suite with separate living area, balcony, and jacuzzi', total_rooms=8),
                    RoomType(type_name='Presidential Villa', base_price=15000.00, capacity=4, description='Ultra-premium villa with private pool and personal butler service', total_rooms=4),
                ]
                db.session.add_all(types)
                db.session.commit()

                # Add sample physical rooms
                rooms = []
                for rt in RoomType.query.all():
                    prefix = rt.type_name[0].upper()
                    for i in range(1, 6):
                        rooms.append(Room(
                            room_number=f"{prefix}-10{i}",
                            room_type_id=rt.id,
                            status='available',
                            floor=1
                        ))
                db.session.add_all(rooms)
                db.session.commit()
                print("[OK] Default room categories and inventory initialized.")

        except Exception as e:
            print(f"Notice: Database auto-init warning: {e}")

if __name__ == '__main__':
    init_db_defaults()
    print("Starting Flask REST API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
