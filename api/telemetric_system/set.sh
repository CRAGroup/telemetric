#!/usr/bin/env python3
"""
Seed test data for telemetric system
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database.connection import get_db_context
from models.vehicle import Vehicle
from models.driver import Driver
from models.telemetry import TelemetryData
from models.user import User
from core.security.auth import get_password_hash

def seed_users(db: Session):
    """Create test users"""
    users = [
        User(
            email="admin@telemetric.com",
            password_hash=get_password_hash("Admin123!"),
            full_name="Admin User",
            role="admin",
            is_active=True
        ),
        User(
            email="manager@telemetric.com",
            password_hash=get_password_hash("Manager123!"),
            full_name="Fleet Manager",
            role="manager",
            is_active=True
        )
    ]
    
    for user in users:
        existing = db.query(User).filter(User.email == user.email).first()
        if not existing:
            db.add(user)
            print(f"✓ Created user: {user.email}")
    
    db.commit()

def seed_drivers(db: Session):
    """Create test drivers"""
    drivers = [
        Driver(
            full_name="John Kamau",
            license_number="DL001234",
            phone="+254722334455",
            email="john.kamau@example.com",
            license_expiry=datetime.now() + timedelta(days=730)
        ),
        Driver(
            full_name="Mary Wanjiku",
            license_number="DL005678",
            phone="+254733445566",
            email="mary.wanjiku@example.com",
            license_expiry=datetime.now() + timedelta(days=365)
        ),
        Driver(
            full_name="Peter Omondi",
            license_number="DL009012",
            phone="+254744556677",
            email="peter.omondi@example.com",
            license_expiry=datetime.now() + timedelta(days=500)
        )
    ]
    
    for driver in drivers:
        existing = db.query(Driver).filter(Driver.license_number == driver.license_number).first()
        if not existing:
            db.add(driver)
            print(f"✓ Created driver: {driver.full_name}")
    
    db.commit()
    return drivers

def seed_vehicles(db: Session, drivers):
    """Create test vehicles"""
    vehicle_data = [
        ("KAA 123X", "Toyota", "Land Cruiser", 2023, "SUV", "White"),
        ("KBB 456Y", "Nissan", "Patrol", 2022, "SUV", "Black"),
        ("KCC 789Z", "Isuzu", "D-Max", 2023, "Pickup", "Silver"),
        ("KDD 012A", "Toyota", "Hilux", 2021, "Pickup", "Red"),
        ("KEE 345B", "Mitsubishi", "L200", 2022, "Pickup", "Blue"),
    ]
    
    vehicles = []
    for i, (reg, make, model, year, vtype, color) in enumerate(vehicle_data):
        existing = db.query(Vehicle).filter(Vehicle.registration_number == reg).first()
        if not existing:
            vehicle = Vehicle(
                registration_number=reg,
                make=make,
                model=model,
                year=year,
                vin_number=f"VIN{random.randint(100000, 999999)}",
                fuel_tank_capacity=80.0,
                vehicle_type=vtype,
                color=color,
                status="active",
                driver_id=drivers[i % len(drivers)].id if i < len(drivers) else None
            )
            db.add(vehicle)
            vehicles.append(vehicle)
            print(f"✓ Created vehicle: {reg}")
    
    db.commit()
    return vehicles

def seed_telemetry(db: Session, vehicles):
    """Create sample telemetry data"""
    # Nairobi coordinates
    base_lat = -1.286389
    base_lon = 36.817223
    
    for vehicle in vehicles[:3]:  # Only for first 3 vehicles
        # Create telemetry for last 24 hours
        for hour in range(24):
            timestamp = datetime.now() - timedelta(hours=hour)
            
            telemetry = TelemetryData(
                vehicle_id=vehicle.id,
                timestamp=timestamp,
                latitude=base_lat + random.uniform(-0.1, 0.1),
                longitude=base_lon + random.uniform(-0.1, 0.1),
                speed=random.uniform(0, 100),
                heading=random.uniform(0, 360),
                rpm=random.randint(1000, 4000),
                fuel_level=random.uniform(20, 100),
                engine_temperature=random.uniform(80, 95),
                battery_voltage=random.uniform(12.0, 14.5)
            )
            db.add(telemetry)
        
        print(f"✓ Created telemetry data for: {vehicle.registration_number}")
    
    db.commit()

def main():
    print("=" * 60)
    print("Seeding Test Data for Telemetric System")
    print("=" * 60)
    
    with get_db_context() as db:
        print("\n1. Creating users...")
        seed_users(db)
        
        print("\n2. Creating drivers...")
        drivers = seed_drivers(db)
        
        print("\n3. Creating vehicles...")
        vehicles = seed_vehicles(db, drivers)
        
        print("\n4. Creating telemetry data...")
        seed_telemetry(db, vehicles)
    
    print("\n" + "=" * 60)
    print("✓ Test data seeding completed!")
    print("=" * 60)
    print("\nTest Credentials:")
    print("  Admin:   admin@telemetric.com / Admin123!")
    print("  Manager: manager@telemetric.com / Manager123!")
    print("\n")

if __name__ == "__main__":
    main()
