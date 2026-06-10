import collections
import statistics
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
    ).all()

    scanners = {s.identifier: s.name for s in db.query(Scanner).all()}
    
    agg = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
    agg_rssi = collections.defaultdict(lambda: collections.defaultdict(list))
    
    for log in logs:
        dt = log.timestamp
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        hour_iso = dt.replace(minute=0, second=0, microsecond=0).isoformat()
        if not hour_iso.endswith('Z') and '+00:00' not in hour_iso:
            hour_iso += 'Z'
        
        agg[log.scanner][hour_iso][log.zone] += 1
        distance = round(rssi_to_meters(log.rssi), 2)
        agg_rssi[log.scanner][hour_iso].append(distance)

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
    
    for s_id in sorted(agg.keys()):
        s_name = scanners.get(s_id, f"Scanner {s_id}")
        scanner_series = []
        
        for zone in zones:
            series_data = []
            for h in hours_iso:
                series_data.append({"x": h, "y": agg[s_id][h][zone]})
            scanner_series.append({"name": zone, "data": series_data})
            
        boxplot_data = []
        for h in hours_iso:
            rssi_list = agg_rssi[s_id][h]
            if rssi_list:
                if len(rssi_list) >= 2:
                    q1, median, q3 = statistics.quantiles(rssi_list, n=4)
                    y_val = [min(rssi_list), q1, median, q3, max(rssi_list)]
                else:
                    val = rssi_list[0]
                    y_val = [val, val, val, val, val]
                boxplot_data.append({"x": h, "y": y_val})
        
        scanner_boxplot = [{"type": "boxPlot", "name": "Distance (m)", "data": boxplot_data}]

        payload.append({
            "scanner_id": s_id,
            "scanner_name": s_name,
            "series": scanner_series,
            "boxplot_series": scanner_boxplot
        })
    
    return payload

def log_tracking(db: Session, mac: str, rssi: int, scanner_id: str):
    """Processes and logs a tracking signal. Returns the log object or None if ignored."""
    # Check if this MAC belongs to a registered student
    card = db.query(Card).filter(Card.tracker_mac == mac).first()
    if not card:
        return None

    # Classify zone
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
