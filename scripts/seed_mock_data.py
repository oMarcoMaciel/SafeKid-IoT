import os
import random
import sys
from datetime import datetime, timedelta, timezone

# Adiciona o diretório pai ao path para importar os modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Base, SessionLocal, engine
from backend.models import AccessLog, Card, Scanner, TrackingLog


def seed():
    print("Seeding database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Clear existing data (optional, but good for clean demo)
    db.query(TrackingLog).delete()
    db.query(Scanner).delete()
    db.query(Card).delete()
    db.query(AccessLog).delete()

    # 2. Add Scanners
    scanners = [
        Scanner(identifier="esp32-central", name="Main Entrance"),
        Scanner(identifier="esp32-playground", name="Playground Area")
    ]
    db.add_all(scanners)
    db.commit()

    # 3. Add Cards (Students)
    cards = [
        Card(uid="AA:BB:CC:DD", name="Alice Smith", role="student", tracker_mac="00:11:22:33:44:55", is_active=True),
        Card(uid="11:22:33:44", name="Bob Johnson", role="student", tracker_mac="66:77:88:99:AA:BB", is_active=True),
    ]
    db.add_all(cards)
    db.commit()

    # 4. Add Tracking Logs (last 24 hours)
    now = datetime.now(timezone.utc)
    
    # Alice: Moves between near and far at entrance
    # Bob: Mostly in playground, sometimes leaves
    
    for student_mac, scanner_id in [("00:11:22:33:44:55", "esp32-central"), ("66:77:88:99:AA:BB", "esp32-playground")]:
        for h in range(24):
            # Each hour has some points
            hour_start = now - timedelta(hours=h)
            
            # Base RSSI for this hour to simulate "zones"
            # We want a curve, so let's use a sine-like variation over 24h
            base_rssi = -65 + 15 * (1 + (h / 12)) # simple variation
            
            for m in range(0, 60, 5): # Every 5 minutes
                timestamp = hour_start.replace(minute=m, second=random.randint(0,59))
                
                # Add some random noise to RSSI
                noise = random.randint(-5, 5)
                # Ensure Alice and Bob have different patterns
                if "Alice" in str(student_mac):
                   rssi = -60 + noise + (10 if h < 12 else -15) # Nearer in first 12h
                else:
                   rssi = -70 + noise + (20 if (h % 6) < 3 else -10) # Oscillates every 6h
                
                # Zone classification
                if rssi >= -55: zone = "Very Near"
                elif rssi >= -75: zone = "Near"
                else: zone = "Far"
                
                log = TrackingLog(
                    mac=student_mac,
                    rssi=rssi,
                    zone=zone,
                    scanner=scanner_id,
                    timestamp=timestamp
                )
                db.add(log)
        
    db.commit()
    print("Successfully seeded scanners, cards and tracking logs!")
    db.close()

if __name__ == "__main__":
    seed()
