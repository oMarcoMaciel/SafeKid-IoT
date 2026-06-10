import collections
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..cards.models import Card
from ..scanners.models import Scanner
from .models import TrackingLog

# RSSI to Meters constants
MEASURED_POWER = -62
N_ENV = 2.5

def rssi_to_meters(rssi: int) -> float:
    """Estimates distance in meters based on RSSI"""
    if not rssi:
        return 0.0
    return 10 ** ((MEASURED_POWER - rssi) / (10 * N_ENV))

def get_live_tracking(db: Session):
    """Returns the current location status of all students with trackers"""
    cards = db.query(Card).filter(Card.tracker_mac != None).all()  # noqa: E711
    
    results = []
    now_utc = datetime.now(timezone.utc)
    
    for card in cards:
        last_log = db.query(TrackingLog)\
            .filter(TrackingLog.mac == card.tracker_mac)\
            .order_by(TrackingLog.timestamp.desc())\
            .first()
        
        status = "offline"
        if last_log:
            log_time = last_log.timestamp
            if log_time.tzinfo is None:
                log_time = log_time.replace(tzinfo=timezone.utc)
                
            if now_utc - log_time <= timedelta(minutes=2):
                status = "online"
        
        results.append({
            "student_name": card.name,
            "mac": card.tracker_mac,
            "status": status,
            "rssi": last_log.rssi if last_log else None,
            "zone": last_log.zone if last_log else "Unknown",
            "last_seen": last_log.timestamp if last_log else None
        })
    
    return results

def get_heatmap_data(db: Session, mac: str):
    """Returns structured data for stacked bar charts per scanner"""
    now_utc = datetime.now(timezone.utc)
    start_time = now_utc - timedelta(days=1)
    
    logs = db.query(TrackingLog).filter(
        TrackingLog.mac == mac,
        TrackingLog.timestamp >= start_time
    ).order_by(TrackingLog.timestamp.asc()).all()

    scanners = {s.identifier: s.name for s in db.query(Scanner).all()}
    
    # Aggregation for Bar Chart (Hourly)
    agg_bar = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
    
    # Aggregation for RSSI Curve (5-minute windows for smoothness)
    agg_rssi = collections.defaultdict(lambda: collections.defaultdict(list))
    
    for log in logs:
        dt = log.timestamp
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # Bar chart: Hour granularity
        hour_iso = dt.replace(minute=0, second=0, microsecond=0).isoformat()
        if not hour_iso.endswith('Z') and '+00:00' not in hour_iso:
            hour_iso += 'Z'
        agg_bar[log.scanner][hour_iso][log.zone] += 1
        
        # RSSI curve: 5-minute granularity for a smooth continuous curve
        minute_5 = (dt.minute // 5) * 5
        time_iso = dt.replace(minute=minute_5, second=0, microsecond=0).isoformat()
        if not time_iso.endswith('Z') and '+00:00' not in time_iso:
            time_iso += 'Z'
        agg_rssi[log.scanner][time_iso].append(log.rssi)

    # Generate the last 24 hours (Hourly)
    hours_iso = []
    curr = now_utc.replace(minute=0, second=0, microsecond=0) - timedelta(hours=23)
    for _ in range(24):
        h_str = curr.isoformat()
        if not h_str.endswith('Z') and '+00:00' not in h_str:
            h_str += 'Z'
        hours_iso.append(h_str)
        curr += timedelta(hours=1)

    zones = ["Very Near", "Near", "Far"]
    payload = []
    
    for s_id in sorted(agg_bar.keys()):
        s_name = scanners.get(s_id, f"Scanner {s_id}")
        
        # 1. Stacked Bar Series
        scanner_series = []
        for zone in zones:
            series_data = []
            for h in hours_iso:
                series_data.append({"x": h, "y": agg_bar[s_id][h][zone]})
            scanner_series.append({"name": zone, "data": series_data})
            
        # 2. RSSI Curve Series
        rssi_data = []
        # Sort timestamps for the curve
        for t_iso in sorted(agg_rssi[s_id].keys()):
            avg_rssi = sum(agg_rssi[s_id][t_iso]) / len(agg_rssi[s_id][t_iso])
            rssi_data.append({"x": t_iso, "y": round(avg_rssi, 1)})
        
        scanner_rssi_series = [{"name": "Signal Strength (RSSI)", "data": rssi_data}]

        payload.append({
            "scanner_id": s_id,
            "scanner_name": s_name,
            "series": scanner_series,
            "rssi_series": scanner_rssi_series
        })
    
    return payload

def log_tracking(db: Session, mac: str, rssi: int, scanner_id: str):
    """Business logic for logging tracking data"""
    card = db.query(Card).filter(Card.tracker_mac == mac).first()
    if not card:
        return None

    if rssi >= -55:
        zone = "Very Near"
    elif rssi >= -75:
        zone = "Near"
    else:
        zone = "Far"

    log = TrackingLog(mac=mac, rssi=rssi, zone=zone, scanner=scanner_id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log, card.name
