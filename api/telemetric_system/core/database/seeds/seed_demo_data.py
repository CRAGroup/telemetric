"""Seed demo data for development and testing.

Creates realistic demo data including:
- Users (admin, manager, drivers, viewers)
- Vehicle types
- Vehicles with various statuses
- Drivers
- Telemetry data
- Trips
- Alerts
- Maintenance records
- Fuel transactions
"""

from datetime import datetime, timedelta
import random

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.user import User, UserRole
from telemetric_system.models.vehicle_type import VehicleType
from telemetric_system.models.vehicle import Vehicle, VehicleStatus
from telemetric_system.models.driver import Driver
from telemetric_system.models.telemetry import Telemetry
from telemetric_system.models.trip import Trip
from telemetric_system.models.alert import Alert, AlertSeverity
from telemetric_system.models.maintenance import MaintenanceRecord
from telemetric_system.models.fuel import FuelTransaction
from telemetric_system.models.admin_settings import AdminSettings
from telemetric_system.core.security.auth import hash_password


def seed_users(session):
    """Create demo users with different roles."""
    print("🔐 Seeding users...")
    
    users_data = [
        {
            "email": "admin@fleettrack.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": UserRole.ADMIN.value,
            "is_active": True
        },
        {
            "email": "manager@fleettrack.com",
            "password": "manager123",
            "full_name": "Fleet Manager",
            "role": UserRole.MANAGER.value,
            "is_active": True
        },
        {
            "email": "driver1@fleettrack.com",
            "password": "driver123",
            "full_name": "John Kamau",
            "role": UserRole.DRIVER.value,
            "is_active": True
        },
        {
            "email": "driver2@fleettrack.com",
            "password": "driver123",
            "full_name": "Mary Wanjiku",
            "role": UserRole.DRIVER.value,
            "is_active": True
        },
        {
            "email": "viewer@fleettrack.com",
            "password": "viewer123",
            "full_name": "Viewer User",
            "role": UserRole.VIEWER.value,
            "is_active": True
        },
    ]
    
    created_users = []
    for user_data in users_data:
        existing = session.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=user_data["is_active"]
            )
            session.add(user)
            created_users.append(user)
            print(f"  ✅ Created user: {user_data['email']} (role: {user_data['role']})")
        else:
            created_users.append(existing)
            print(f"  ⏭️  User exists: {user_data['email']}")
    
    session.commit()
    return created_users


def seed_vehicle_types(session):
    """Create vehicle type categories."""
    print("\n🚛 Seeding vehicle types...")
    
    types_data = [
        {"name": "Truck", "description": "Heavy duty cargo truck for long-haul transport"},
        {"name": "Van", "description": "Light commercial van for urban deliveries"},
        {"name": "Pickup", "description": "Pickup truck for versatile cargo transport"},
        {"name": "Trailer", "description": "Semi-trailer truck for large cargo"},
        {"name": "Tanker", "description": "Fuel or liquid tanker truck"},
        {"name": "Refrigerated", "description": "Refrigerated transport vehicle for perishables"},
    ]
    
    created_types = []
    for type_data in types_data:
        existing = session.query(VehicleType).filter(VehicleType.name == type_data["name"]).first()
        if not existing:
            vtype = VehicleType(**type_data)
            session.add(vtype)
            created_types.append(vtype)
            print(f"  ✅ Created vehicle type: {type_data['name']}")
        else:
            created_types.append(existing)
            print(f"  ⏭️  Vehicle type exists: {type_data['name']}")
    
    session.commit()
    return created_types


def seed_drivers(session):
    """Create demo drivers."""
    print("\n👨‍✈️ Seeding drivers...")
    
    drivers_data = [
        {
            "driver_identifier": "DRV001",
            "first_name": "John",
            "last_name": "Kamau",
            "license_number": "KE-DL-123456",
            "license_expiry": datetime.now().date() + timedelta(days=730),
            "phone_number": "+254712345678",
            "email": "john.kamau@fleettrack.com"
        },
        {
            "driver_identifier": "DRV002",
            "first_name": "Mary",
            "last_name": "Wanjiku",
            "license_number": "KE-DL-234567",
            "license_expiry": datetime.now().date() + timedelta(days=365),
            "phone_number": "+254723456789",
            "email": "mary.wanjiku@fleettrack.com"
        },
        {
            "driver_identifier": "DRV003",
            "first_name": "Peter",
            "last_name": "Omondi",
            "license_number": "KE-DL-345678",
            "license_expiry": datetime.now().date() + timedelta(days=500),
            "phone_number": "+254734567890",
            "email": "peter.omondi@fleettrack.com"
        },
        {
            "driver_identifier": "DRV004",
            "first_name": "Grace",
            "last_name": "Akinyi",
            "license_number": "KE-DL-456789",
            "license_expiry": datetime.now().date() + timedelta(days=600),
            "phone_number": "+254745678901",
            "email": "grace.akinyi@fleettrack.com"
        },
    ]
    
    created_drivers = []
    for driver_data in drivers_data:
        existing = session.query(Driver).filter(Driver.license_number == driver_data["license_number"]).first()
        if not existing:
            driver = Driver(**driver_data)
            session.add(driver)
            created_drivers.append(driver)
            print(f"  ✅ Created driver: {driver_data['first_name']} {driver_data['last_name']}")
        else:
            created_drivers.append(existing)
            print(f"  ⏭️  Driver exists: {driver_data['first_name']} {driver_data['last_name']}")
    
    session.commit()
    return created_drivers


def seed_vehicles(session, vehicle_types, drivers):
    """Create demo vehicles."""
    print("\n🚗 Seeding vehicles...")
    
    # Nairobi coordinates for demo
    nairobi_coords = [
        (-1.2921, 36.8219),  # City Center
        (-1.3167, 36.8333),  # Westlands
        (-1.2667, 36.8000),  # Industrial Area
        (-1.3500, 36.9167),  # Embakasi
        (-1.2500, 36.7500),  # Karen
    ]
    
    vehicles_data = [
        {
            "vehicle_id": "VEH001",
            "registration_number": "KCA 123A",
            "make": "Isuzu",
            "model": "NPR",
            "model_name": "Isuzu NPR",
            "year": 2020,
            "status": VehicleStatus.ACTIVE,
            "max_load_weight": 5000.0,
            "current_load_weight": 3200.0,
            "load_category": "General Cargo",
            "current_odometer": 45000.0,
            "fuel_tank_capacity": 100.0,
            "device_imei": "356938035643809",
            "latitude": nairobi_coords[0][0],
            "longitude": nairobi_coords[0][1],
        },
        {
            "vehicle_id": "VEH002",
            "registration_number": "KCB 456B",
            "make": "Mitsubishi",
            "model": "Canter",
            "model_name": "Mitsubishi Canter",
            "year": 2019,
            "status": VehicleStatus.IN_TRANSIT,
            "max_load_weight": 3000.0,
            "current_load_weight": 2100.0,
            "load_category": "Electronics",
            "current_odometer": 62000.0,
            "fuel_tank_capacity": 80.0,
            "device_imei": "356938035643810",
            "latitude": nairobi_coords[1][0],
            "longitude": nairobi_coords[1][1],
        },
        {
            "vehicle_id": "VEH003",
            "registration_number": "KCC 789C",
            "make": "Mercedes",
            "model": "Actros",
            "model_name": "Mercedes Actros",
            "year": 2021,
            "status": VehicleStatus.AWAITING_LOADING,
            "max_load_weight": 15000.0,
            "current_load_weight": 0.0,
            "load_category": "Heavy Machinery",
            "current_odometer": 28000.0,
            "fuel_tank_capacity": 400.0,
            "device_imei": "356938035643811",
            "latitude": nairobi_coords[2][0],
            "longitude": nairobi_coords[2][1],
        },
        {
            "vehicle_id": "VEH004",
            "registration_number": "KCD 012D",
            "make": "Toyota",
            "model": "Hiace",
            "model_name": "Toyota Hiace",
            "year": 2018,
            "status": VehicleStatus.IDLE,
            "max_load_weight": 1500.0,
            "current_load_weight": 0.0,
            "load_category": "Passenger",
            "current_odometer": 95000.0,
            "fuel_tank_capacity": 70.0,
            "device_imei": "356938035643812",
            "latitude": nairobi_coords[3][0],
            "longitude": nairobi_coords[3][1],
        },
        {
            "vehicle_id": "VEH005",
            "registration_number": "KCE 345E",
            "make": "Scania",
            "model": "R450",
            "model_name": "Scania R450",
            "year": 2022,
            "status": VehicleStatus.MAINTENANCE,
            "max_load_weight": 20000.0,
            "current_load_weight": 0.0,
            "load_category": "Fuel Transport",
            "current_odometer": 15000.0,
            "fuel_tank_capacity": 500.0,
            "device_imei": "356938035643813",
            "latitude": nairobi_coords[4][0],
            "longitude": nairobi_coords[4][1],
        },
    ]
    
    created_vehicles = []
    for i, vehicle_data in enumerate(vehicles_data):
        existing = session.query(Vehicle).filter(Vehicle.registration_number == vehicle_data["registration_number"]).first()
        if not existing:
            # Assign vehicle type
            if i < len(vehicle_types):
                vehicle_data["vehicle_type_id"] = vehicle_types[i % len(vehicle_types)].id
            
            # Assign driver to some vehicles
            if i < len(drivers):
                vehicle_data["driver_id"] = drivers[i].id
            
            vehicle = Vehicle(**vehicle_data)
            session.add(vehicle)
            created_vehicles.append(vehicle)
            print(f"  ✅ Created vehicle: {vehicle_data['registration_number']} - {vehicle_data['model_name']}")
        else:
            created_vehicles.append(existing)
            print(f"  ⏭️  Vehicle exists: {vehicle_data['registration_number']}")
    
    session.commit()
    return created_vehicles


def seed_admin_settings(session):
    """Create admin settings."""
    print("\n⚙️  Seeding admin settings...")
    
    settings_data = [
        {
            "key": "company_name",
            "value": "FleetTrack Kenya",
            "description": "Company name displayed in the application",
            "is_public": True,
            "category": "general"
        },
        {
            "key": "company_logo_url",
            "value": "/assets/logo.png",
            "description": "URL to company logo",
            "is_public": True,
            "category": "branding"
        },
        {
            "key": "max_speed_limit",
            "value": "120",
            "description": "Maximum speed limit in km/h for alerts",
            "is_public": False,
            "category": "alerts"
        },
        {
            "key": "maintenance_reminder_km",
            "value": "10000",
            "description": "Kilometers interval for maintenance reminders",
            "is_public": False,
            "category": "maintenance"
        },
    ]
    
    for setting_data in settings_data:
        existing = session.query(AdminSettings).filter(AdminSettings.key == setting_data["key"]).first()
        if not existing:
            setting = AdminSettings(**setting_data)
            session.add(setting)
            print(f"  ✅ Created setting: {setting_data['key']}")
        else:
            print(f"  ⏭️  Setting exists: {setting_data['key']}")
    
    session.commit()


def seed_all():
    """Run all seed functions."""
    print("=" * 60)
    print("🌱 Starting database seeding...")
    print("=" * 60)
    
    session = get_session()
    
    try:
        # Seed in order of dependencies
        users = seed_users(session)
        vehicle_types = seed_vehicle_types(session)
        drivers = seed_drivers(session)
        vehicles = seed_vehicles(session, vehicle_types, drivers)
        seed_admin_settings(session)
        
        print("\n" + "=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Vehicle Types: {len(vehicle_types)}")
        print(f"  - Drivers: {len(drivers)}")
        print(f"  - Vehicles: {len(vehicles)}")
        print("\n🔐 Test Credentials:")
        print("  Admin:   admin@fleettrack.com / admin123")
        print("  Manager: manager@fleettrack.com / manager123")
        print("  Driver:  driver1@fleettrack.com / driver123")
        print("  Viewer:  viewer@fleettrack.com / viewer123")
        print("")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_all()
