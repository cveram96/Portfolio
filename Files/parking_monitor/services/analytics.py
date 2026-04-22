from db.crud import save_metric
from datetime import datetime

def calculate_analytics(current_occupancy: int, total_spaces: int):
    """
    Called periodically to save analytics
    """
    if total_spaces == 0:
        return
        
    occupancy_percentage = (current_occupancy / total_spaces) * 100
    save_metric("occupancy_percentage", occupancy_percentage)
    
    # In a full system we would aggregate historical logs to calculate peak hours
    # and track individual vehicles (with DeepSORT) or space states for average stay duration.
    # For MVP, we save the instant percentage to build charts.
