"""
Flipkart Minutes Optimization - Delivery Zone Mapping Module (Fixed)

This module provides delivery zone optimization and mapping functionality for Flipkart's 10-15 minute delivery service.
It includes zone calculation, traffic pattern analysis, and dynamic zone adjustment algorithms.

Author: Product Manager
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math
import warnings
warnings.filterwarnings('ignore')

class DeliveryZoneMapper:
    """
    Advanced delivery zone mapping and optimization class for Flipkart Minutes.
    
    This class provides methods to:
    - Calculate optimal delivery zones around dark stores
    - Analyze traffic patterns and delivery success rates
    - Implement dynamic zone adjustment logic
    - Optimize delivery routes and coverage areas
    """
    
    def __init__(self, data_path='../data/'):
        """
        Initialize the DeliveryZoneMapper with data path.
        
        Args:
            data_path (str): Path to the data directory
        """
        self.data_path = data_path
        self.sample_data = None
        self.dark_stores = {
            'DS001': {'lat': 12.9716, 'lon': 77.5946, 'name': 'Koramangala'},
            'DS002': {'lat': 12.9698, 'lon': 77.7500, 'name': 'Whitefield'},
            'DS003': {'lat': 13.0067, 'lon': 77.5664, 'name': 'Malleshwaram'},
            'DS004': {'lat': 12.9279, 'lon': 77.6271, 'name': 'BTM Layout'},
            'DS005': {'lat': 13.0358, 'lon': 77.5970, 'name': 'Hebbal'}
        }
        
    def load_data(self):
        """
        Load all required datasets for delivery zone analysis.
        
        Returns:
            bool: True if all data loaded successfully, False otherwise
        """
        try:
            self.sample_data = pd.read_csv(f'{self.data_path}sample_data.csv')
            self.sample_data['timestamp'] = pd.to_datetime(self.sample_data['timestamp'])
            self.sample_data['hour'] = self.sample_data['timestamp'].dt.hour
            
            # Update dark_stores to only include stores that exist in the data
            available_stores = self.sample_data['dark_store_id'].unique()
            original_stores = self.dark_stores.copy()
            self.dark_stores = {k: v for k, v in self.dark_stores.items() if k in available_stores}
            
            print(f"✅ Data loaded successfully!")
            print(f"📍 Available dark stores: {list(self.dark_stores.keys())}")
            
            missing_stores = set(original_stores.keys()) - set(self.dark_stores.keys())
            if missing_stores:
                print(f"⚠️ Note: These stores are defined but have no data: {list(missing_stores)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: Latitude and longitude of first point
            lat2, lon2: Latitude and longitude of second point
            
        Returns:
            float: Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def calculate_travel_time(self, distance_km, hour, traffic_factor=1.0):
        """
        Calculate travel time based on distance, hour, and traffic conditions.
        
        Args:
            distance_km (float): Distance in kilometers
            hour (int): Hour of the day (0-23)
            traffic_factor (float): Traffic multiplication factor
            
        Returns:
            float: Travel time in minutes
        """
        # Base speed in different traffic conditions (km/h)
        if hour in [7, 8, 9, 17, 18, 19, 20]:  # Peak hours
            base_speed = 15 * traffic_factor  # Slower during peak hours
        elif hour in [10, 11, 12, 13, 14, 15, 16]:  # Business hours
            base_speed = 25 * traffic_factor
        else:  # Off-peak hours
            base_speed = 35 * traffic_factor
        
        # Add pickup and delivery time
        pickup_delivery_time = 3  # 3 minutes total
        
        travel_time = (distance_km / base_speed) * 60 + pickup_delivery_time
        return travel_time
    
    def generate_delivery_zones(self, target_delivery_time=12):
        """
        Generate optimal delivery zones for each dark store.
        
        Args:
            target_delivery_time (int): Target delivery time in minutes
            
        Returns:
            dict: Delivery zones for each dark store
        """
        delivery_zones = {}
        
        for store_id, store_info in self.dark_stores.items():
            zones = {}
            
            # Calculate zones for different times of day
            for hour in range(24):
                # Binary search to find optimal radius
                min_radius = 0.1
                max_radius = 10.0
                optimal_radius = 1.0
                
                for _ in range(20):  # Binary search iterations
                    test_radius = (min_radius + max_radius) / 2
                    estimated_time = self.calculate_travel_time(test_radius, hour)
                    
                    if estimated_time <= target_delivery_time:
                        optimal_radius = test_radius
                        min_radius = test_radius
                    else:
                        max_radius = test_radius
                
                zones[hour] = {
                    'radius_km': round(optimal_radius, 2),
                    'estimated_delivery_time': round(self.calculate_travel_time(optimal_radius, hour), 1),
                    'coverage_area_km2': round(math.pi * optimal_radius ** 2, 2)
                }
            
            delivery_zones[store_id] = {
                'store_info': store_info,
                'hourly_zones': zones,
                'avg_radius': round(np.mean([z['radius_km'] for z in zones.values()]), 2),
                'avg_coverage': round(np.mean([z['coverage_area_km2'] for z in zones.values()]), 2)
            }
        
        return delivery_zones
    
    def analyze_delivery_performance(self):
        """
        Analyze current delivery performance by time and store.
        
        Returns:
            pd.DataFrame: Delivery performance analysis
        """
        if self.sample_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        performance_analysis = self.sample_data.groupby(['dark_store_id', 'hour']).agg({
            'delivery_time_minutes': ['mean', 'std', 'min', 'max'],
            'orders_fulfilled': 'sum',
            'orders_cancelled': 'sum',
            'csat_score': 'mean'
        }).round(2)
        
        # Flatten column names
        performance_analysis.columns = ['_'.join(col).strip() for col in performance_analysis.columns.values]
        performance_analysis = performance_analysis.reset_index()
        
        # Calculate derived metrics
        performance_analysis['total_orders'] = (
            performance_analysis['orders_fulfilled_sum'] + 
            performance_analysis['orders_cancelled_sum']
        )
        
        performance_analysis['success_rate'] = (
            performance_analysis['orders_fulfilled_sum'] / 
            performance_analysis['total_orders']
        ).fillna(0)
        
        performance_analysis['on_time_delivery'] = (
            performance_analysis['delivery_time_minutes_mean'] <= 15
        ).astype(int)
        
        return performance_analysis
    
    def identify_traffic_patterns(self):
        """
        Identify traffic patterns and their impact on delivery times.
        
        Returns:
            dict: Traffic pattern analysis
        """
        if self.sample_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        # Analyze delivery times by hour
        hourly_patterns = self.sample_data.groupby('hour').agg({
            'delivery_time_minutes': ['mean', 'std'],
            'orders_fulfilled': 'sum'
        }).round(2)
        
        hourly_patterns.columns = ['avg_delivery_time', 'delivery_time_std', 'total_orders']
        hourly_patterns = hourly_patterns.reset_index()
        
        # Classify traffic conditions
        avg_delivery_time = hourly_patterns['avg_delivery_time'].mean()
        hourly_patterns['traffic_condition'] = hourly_patterns['avg_delivery_time'].apply(
            lambda x: 'Heavy' if x > avg_delivery_time * 1.2 
                     else 'Moderate' if x > avg_delivery_time * 0.8 
                     else 'Light'
        )
        
        # Identify peak traffic hours
        peak_hours = hourly_patterns[hourly_patterns['traffic_condition'] == 'Heavy']['hour'].tolist()
        
        # Calculate traffic impact
        traffic_patterns = {
            'hourly_analysis': hourly_patterns,
            'peak_traffic_hours': peak_hours,
            'avg_delivery_time': round(avg_delivery_time, 1),
            'traffic_impact': {
                'heavy_traffic_penalty': round(
                    hourly_patterns[hourly_patterns['traffic_condition'] == 'Heavy']['avg_delivery_time'].mean() - avg_delivery_time, 1
                ),
                'light_traffic_advantage': round(
                    avg_delivery_time - hourly_patterns[hourly_patterns['traffic_condition'] == 'Light']['avg_delivery_time'].mean(), 1
                )
            }
        }
        
        return traffic_patterns
    
    def calculate_zone_overlap(self):
        """
        Calculate overlap between delivery zones of different dark stores.
        
        Returns:
            pd.DataFrame: Zone overlap analysis
        """
        delivery_zones = self.generate_delivery_zones()
        overlap_analysis = []
        
        store_list = list(self.dark_stores.keys())
        
        for i, store1 in enumerate(store_list):
            for j, store2 in enumerate(store_list[i+1:], i+1):
                store1_info = self.dark_stores[store1]
                store2_info = self.dark_stores[store2]
                
                # Calculate distance between stores
                distance = self.calculate_distance(
                    store1_info['lat'], store1_info['lon'],
                    store2_info['lat'], store2_info['lon']
                )
                
                # Get average delivery radius for both stores
                avg_radius1 = delivery_zones[store1]['avg_radius']
                avg_radius2 = delivery_zones[store2]['avg_radius']
                
                # Calculate overlap
                if distance < (avg_radius1 + avg_radius2):
                    overlap_exists = True
                    overlap_distance = (avg_radius1 + avg_radius2) - distance
                    overlap_percentage = (overlap_distance / min(avg_radius1, avg_radius2)) * 100
                else:
                    overlap_exists = False
                    overlap_distance = 0
                    overlap_percentage = 0
                
                overlap_analysis.append({
                    'store1': store1,
                    'store2': store2,
                    'store1_name': store1_info['name'],
                    'store2_name': store2_info['name'],
                    'distance_km': round(distance, 2),
                    'store1_radius': avg_radius1,
                    'store2_radius': avg_radius2,
                    'overlap_exists': overlap_exists,
                    'overlap_distance_km': round(overlap_distance, 2),
                    'overlap_percentage': round(overlap_percentage, 1)
                })
        
        return pd.DataFrame(overlap_analysis)
    
    def recommend_zone_adjustments(self):
        """
        Recommend dynamic zone adjustments based on analysis.
        
        Returns:
            dict: Zone adjustment recommendations
        """
        # Get delivery performance and traffic patterns
        performance = self.analyze_delivery_performance()
        traffic_patterns = self.identify_traffic_patterns()
        delivery_zones = self.generate_delivery_zones()
        overlap_analysis = self.calculate_zone_overlap()
        
        recommendations = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'zone_adjustments': [],
            'operational_recommendations': [],
            'strategic_recommendations': []
        }
        
        # Analyze performance by store - only for stores with data
        store_performance = performance.groupby('dark_store_id').agg({
            'delivery_time_minutes_mean': 'mean',
            'success_rate': 'mean',
            'csat_score_mean': 'mean'
        }).round(2)
        
        # Only process stores that have performance data
        available_stores = store_performance.index.tolist()
        
        for store_id in self.dark_stores.keys():
            if store_id not in available_stores:
                print(f"⚠️ No performance data available for store {store_id} - skipping recommendations")
                continue
                
            store_perf = store_performance.loc[store_id]
            current_zones = delivery_zones[store_id]
            
            # Zone adjustment recommendations
            if store_perf['delivery_time_minutes_mean'] > 18:
                recommendations['zone_adjustments'].append({
                    'store_id': store_id,
                    'store_name': self.dark_stores[store_id]['name'],
                    'current_avg_radius': current_zones['avg_radius'],
                    'recommended_action': 'Reduce zone radius by 15%',
                    'new_radius': round(current_zones['avg_radius'] * 0.85, 2),
                    'reason': f"Average delivery time ({store_perf['delivery_time_minutes_mean']:.1f} min) exceeds target",
                    'priority': 'High'
                })
            elif store_perf['delivery_time_minutes_mean'] < 10 and store_perf['success_rate'] > 0.9:
                recommendations['zone_adjustments'].append({
                    'store_id': store_id,
                    'store_name': self.dark_stores[store_id]['name'],
                    'current_avg_radius': current_zones['avg_radius'],
                    'recommended_action': 'Expand zone radius by 20%',
                    'new_radius': round(current_zones['avg_radius'] * 1.2, 2),
                    'reason': f"Excellent performance allows for expansion",
                    'priority': 'Medium'
                })
        
        # Operational recommendations based on traffic patterns
        peak_hours = traffic_patterns['peak_traffic_hours']
        if peak_hours:
            recommendations['operational_recommendations'].append({
                'category': 'Traffic Management',
                'recommendation': f"Reduce delivery zones by 10-15% during peak hours: {peak_hours}",
                'impact': 'Improved on-time delivery rate',
                'implementation': 'Dynamic zone adjustment in delivery app'
            })
        
        # Strategic recommendations based on overlap analysis
        if len(overlap_analysis) > 0:
            high_overlap = overlap_analysis[overlap_analysis['overlap_percentage'] > 30]
            if len(high_overlap) > 0:
                recommendations['strategic_recommendations'].append({
                    'category': 'Zone Optimization',
                    'recommendation': 'Consider redistributing zones with high overlap',
                    'affected_stores': high_overlap[['store1', 'store2']].values.tolist(),
                    'potential_benefit': 'Reduced operational redundancy and improved efficiency'
                })
        
        return recommendations
    
    def create_zone_mapping_report(self):
        """
        Create a comprehensive delivery zone mapping report.
        
        Returns:
            dict: Complete zone mapping analysis
        """
        if not self.load_data():
            return None
        
        print("🗺️ Generating delivery zones...")
        delivery_zones = self.generate_delivery_zones()
        
        print("📊 Analyzing delivery performance...")
        performance_analysis = self.analyze_delivery_performance()
        
        print("🚦 Identifying traffic patterns...")
        traffic_patterns = self.identify_traffic_patterns()
        
        print("🔄 Calculating zone overlaps...")
        overlap_analysis = self.calculate_zone_overlap()
        
        print("💡 Generating recommendations...")
        recommendations = self.recommend_zone_adjustments()
        
        zone_report = {
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'delivery_zones': delivery_zones,
            'performance_analysis': performance_analysis,
            'traffic_patterns': traffic_patterns,
            'overlap_analysis': overlap_analysis,
            'recommendations': recommendations
        }
        
        return zone_report

def main():
    """
    Main function to run the delivery zone mapping analysis.
    """
    print("🚀 Starting Flipkart Minutes Delivery Zone Mapping...")
    print("=" * 52)
    
    # Initialize mapper
    mapper = DeliveryZoneMapper()
    
    # Generate complete zone mapping report
    report = mapper.create_zone_mapping_report()
    
    if report:
        print("\n🗺️ DELIVERY ZONE SUMMARY")
        print("-" * 30)
        
        # Display zone statistics
        zones = report['delivery_zones']
        if zones:
            avg_radius = np.mean([zone['avg_radius'] for zone in zones.values()])
            total_coverage = sum([zone['avg_coverage'] for zone in zones.values()])
            
            print(f"Average delivery radius: {avg_radius:.2f} km")
            print(f"Total coverage area: {total_coverage:.1f} km²")
            print(f"Number of active dark stores: {len(zones)}")
        
        # Display traffic insights
        traffic = report['traffic_patterns']
        print(f"\nPeak traffic hours: {traffic['peak_traffic_hours']}")
        print(f"Traffic impact on delivery: +{traffic['traffic_impact']['heavy_traffic_penalty']:.1f} min during peak hours")
        
        # Display recommendations
        recommendations = report['recommendations']
        zone_adjustments = len(recommendations['zone_adjustments'])
        if zone_adjustments > 0:
            print(f"\nZone adjustment recommendations: {zone_adjustments}")
            for adj in recommendations['zone_adjustments'][:2]:
                print(f"  - {adj['store_name']}: {adj['recommended_action']}")
        
        print("\n✅ Zone mapping analysis completed successfully!")
        return report
    else:
        print("❌ Zone mapping failed. Please check your data files.")
        return None

if __name__ == "__main__":
    # Run the zone mapping analysis
    results = main()