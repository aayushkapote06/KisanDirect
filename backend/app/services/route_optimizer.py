"""
services/route_optimizer.py - AI & Algorithmic Route Optimization

This module implements route optimization for agricultural logistics.
It solves the Traveling Salesperson Problem (TSP) / Multi-Stop Delivery Problem
using the Haversine distance formula and a 2-Opt heuristic optimization algorithm.

Why this matters for farmers:
- Reduces travel distance between multiple delivery points
- Reduces fuel cost and delivery time
- Compares baseline (unoptimized sequential order) vs optimized order
- Quantifies exact kilometers and time saved!
"""

import math
from typing import List, Dict, Any


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth (in km)
    using the Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_total_route_distance(points: List[Dict[str, Any]]) -> float:
    """Calculate the total distance traversing the points in given order."""
    total_dist = 0.0
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        dist = haversine_distance(p1["lat"], p1["lng"], p2["lat"], p2["lng"])
        total_dist += dist
    return round(total_dist, 2)


def two_opt_optimize(points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    2-Opt Optimization Algorithm for Delivery Sequencing.
    Keeps the start point (Depot/Farmer Farm) fixed at index 0.
    Iteratively swaps pairs of edges to eliminate overlapping routes
    and find the shortest path.
    """
    if len(points) <= 3:
        return points[:]

    best_route = points[:]
    improved = True
    iterations = 0
    max_iterations = 50

    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        for i in range(1, len(best_route) - 1):
            for j in range(i + 1, len(best_route)):
                # 2-opt swap: reverse the order between i and j
                new_route = best_route[:i] + best_route[i : j + 1][::-1] + best_route[j + 1 :]
                if calculate_total_route_distance(new_route) < calculate_total_route_distance(best_route):
                    best_route = new_route
                    improved = True
                    break
            if improved:
                break

    return best_route


def optimize_delivery_route(
    depot: Dict[str, Any],
    deliveries: List[Dict[str, Any]],
    avg_speed_kmh: float = 35.0
) -> Dict[str, Any]:
    """
    Accepts:
    - depot: starting location (farmer's collection center / farm) with {name, address, lat, lng}
    - deliveries: list of delivery stops with {id, recipient, address, lat, lng, order_id}

    Returns:
    - baseline_route & baseline_distance
    - optimized_route & optimized_distance
    - distance_saved_km
    - time_saved_minutes
    - percentage_distance_saved
    """
    if not deliveries:
        return {
            "baseline_distance_km": 0.0,
            "optimized_distance_km": 0.0,
            "distance_saved_km": 0.0,
            "time_saved_minutes": 0.0,
            "percentage_saved": 0.0,
            "route": [depot],
        }

    # Baseline: sequential order as received
    baseline_stops = [depot] + deliveries
    baseline_distance = calculate_total_route_distance(baseline_stops)

    # Optimized using 2-opt heuristic
    optimized_stops = two_opt_optimize(baseline_stops)
    optimized_distance = calculate_total_route_distance(optimized_stops)

    distance_saved = max(0.0, round(baseline_distance - optimized_distance, 2))
    percent_saved = (
        round((distance_saved / baseline_distance) * 100, 1)
        if baseline_distance > 0
        else 0.0
    )

    # Estimate travel time based on avg rural/semi-urban speed (35 km/h)
    baseline_time_min = round((baseline_distance / avg_speed_kmh) * 60, 1)
    optimized_time_min = round((optimized_distance / avg_speed_kmh) * 60, 1)
    time_saved_min = max(0.0, round(baseline_time_min - optimized_time_min, 1))

    # Add stop numbers and leg distances
    route_details = []
    for idx, stop in enumerate(optimized_stops):
        leg_dist = 0.0
        if idx > 0:
            prev = optimized_stops[idx - 1]
            leg_dist = round(haversine_distance(prev["lat"], prev["lng"], stop["lat"], stop["lng"]), 2)
        route_details.append({
            "stop_number": idx + 1,
            "name": stop.get("name") or stop.get("recipient") or f"Stop {idx+1}",
            "address": stop.get("address", ""),
            "lat": stop["lat"],
            "lng": stop["lng"],
            "leg_distance_km": leg_dist,
            "is_depot": idx == 0,
            "order_id": stop.get("order_id")
        })

    return {
        "baseline_distance_km": baseline_distance,
        "baseline_estimated_time_min": baseline_time_min,
        "optimized_distance_km": optimized_distance,
        "optimized_estimated_time_min": optimized_time_min,
        "distance_saved_km": distance_saved,
        "time_saved_minutes": time_saved_min,
        "percentage_saved": percent_saved,
        "optimized_stops": route_details,
    }
