"""
Flipkart Minutes Optimization - Inventory Optimization Module

This module provides advanced inventory optimization algorithms for Flipkart's 10-15 minute delivery service.
It includes demand forecasting, optimal stock level calculations, and restocking schedule recommendations.

Author: Product Manager
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class InventoryOptimizer:
    """
    Advanced inventory optimization class for Flipkart Minutes.
    
    This class provides methods to:
    - Forecast demand using machine learning
    - Calculate optimal stock levels
    - Generate restocking schedules
    - Implement safety stock calculations
    - Optimize inventory costs
    """
    
    def __init__(self, data_path='../data/'):
        """
        Initialize the InventoryOptimizer with data path.
        
        Args:
            data_path (str): Path to the data directory
        """
        self.data_path = data_path
        self.sample_data = None
        self.demand_patterns = None
        self.inventory_data = None
        self.forecast_models = {}
        
    def load_data(self):
        """
        Load all required datasets for inventory optimization.
        
        Returns:
            bool: True if all data loaded successfully, False otherwise
        """
        try:
            # Load datasets
            self.sample_data = pd.read_csv(f'{self.data_path}sample_data.csv')
            self.sample_data['timestamp'] = pd.to_datetime(self.sample_data['timestamp'])
            self.sample_data['hour'] = self.sample_data['timestamp'].dt.hour
            self.sample_data['day_of_week'] = self.sample_data['timestamp'].dt.dayofweek
            
            self.demand_patterns = pd.read_csv(f'{self.data_path}demand_patterns.csv')
            self.inventory_data = pd.read_csv(f'{self.data_path}inventory_data.csv')
            
            print("✅ All data loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def create_demand_features(self, data):
        """
        Create features for demand forecasting.
        
        Args:
            data (pd.DataFrame): Input data
            
        Returns:
            pd.DataFrame: Data with additional features
        """
        # Time-based features
        data['hour_sin'] = np.sin(2 * np.pi * data['hour'] / 24)
        data['hour_cos'] = np.cos(2 * np.pi * data['hour'] / 24)
        data['day_sin'] = np.sin(2 * np.pi * data['day_of_week'] / 7)
        data['day_cos'] = np.cos(2 * np.pi * data['day_of_week'] / 7)
        
        # Lag features
        for category in data['category'].unique():
            category_data = data[data['category'] == category].copy()
            category_data = category_data.sort_values('timestamp')
            
            # Create lag features
            category_data['demand_lag_1'] = category_data['demand_quantity'].shift(1)
            category_data['demand_lag_2'] = category_data['demand_quantity'].shift(2)
            category_data['demand_ma_3'] = category_data['demand_quantity'].rolling(window=3).mean()
            
            # Update main dataframe
            data.loc[data['category'] == category, 'demand_lag_1'] = category_data['demand_lag_1']
            data.loc[data['category'] == category, 'demand_lag_2'] = category_data['demand_lag_2']
            data.loc[data['category'] == category, 'demand_ma_3'] = category_data['demand_ma_3']
        
        # Fill missing values
        data = data.fillna(method='bfill').fillna(method='ffill')
        
        return data
    
    def train_demand_forecasting_models(self):
        """
        Train demand forecasting models for each product category.
        
        Returns:
            dict: Dictionary containing trained models and performance metrics
        """
        if self.sample_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        # Prepare data with features
        data_with_features = self.create_demand_features(self.sample_data.copy())
        
        models_performance = {}
        
        # Train model for each category
        for category in data_with_features['category'].unique():
            print(f"🤖 Training model for {category}...")
            
            category_data = data_with_features[data_with_features['category'] == category].copy()
            category_data = category_data.sort_values('timestamp')
            
            # Prepare features and target
            feature_columns = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 
                             'demand_lag_1', 'demand_lag_2', 'demand_ma_3']
            
            X = category_data[feature_columns].dropna()
            y = category_data.loc[X.index, 'demand_quantity']
            
            # Split data (80% train, 20% test)
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = LinearRegression()
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            
            # Store model and performance
            self.forecast_models[category] = {
                'model': model,
                'scaler': scaler,
                'features': feature_columns,
                'performance': {
                    'MAE': round(mae, 2),
                    'RMSE': round(rmse, 2),
                    'MAPE': round(mape, 2)
                }
            }
            
            models_performance[category] = {
                'MAE': round(mae, 2),
                'RMSE': round(rmse, 2),
                'MAPE': round(mape, 2)
            }
        
        print("✅ All forecasting models trained successfully!")
        return models_performance
    
    def forecast_demand(self, hours_ahead=24):
        """
        Forecast demand for the next specified hours.
        
        Args:
            hours_ahead (int): Number of hours to forecast ahead
            
        Returns:
            pd.DataFrame: Forecasted demand for each category and hour
        """
        if not self.forecast_models:
            print("❌ Please train models first using train_demand_forecasting_models()")
            return None
        
        forecasts = []
        
        # Create future timestamps
        last_timestamp = self.sample_data['timestamp'].max()
        future_timestamps = [last_timestamp + timedelta(hours=i) for i in range(1, hours_ahead + 1)]
        
        for category in self.forecast_models.keys():
            model_info = self.forecast_models[category]
            model = model_info['model']
            scaler = model_info['scaler']
            features = model_info['features']
            
            # Get recent data for lag features
            recent_data = self.sample_data[self.sample_data['category'] == category].tail(5)
            
            for timestamp in future_timestamps:
                hour = timestamp.hour
                day_of_week = timestamp.weekday()
                
                # Create features
                feature_values = {
                    'hour_sin': np.sin(2 * np.pi * hour / 24),
                    'hour_cos': np.cos(2 * np.pi * hour / 24),
                    'day_sin': np.sin(2 * np.pi * day_of_week / 7),
                    'day_cos': np.cos(2 * np.pi * day_of_week / 7),
                    'demand_lag_1': recent_data['demand_quantity'].iloc[-1] if len(recent_data) > 0 else 10,
                    'demand_lag_2': recent_data['demand_quantity'].iloc[-2] if len(recent_data) > 1 else 10,
                    'demand_ma_3': recent_data['demand_quantity'].tail(3).mean() if len(recent_data) >= 3 else 10
                }
                
                # Prepare feature vector
                X_future = np.array([[feature_values[f] for f in features]])
                X_future_scaled = scaler.transform(X_future)
                
                # Make prediction
                predicted_demand = max(0, model.predict(X_future_scaled)[0])
                
                forecasts.append({
                    'timestamp': timestamp,
                    'hour': hour,
                    'category': category,
                    'predicted_demand': round(predicted_demand, 1)
                })
        
        forecast_df = pd.DataFrame(forecasts)
        return forecast_df
    
    def calculate_optimal_stock_levels(self, service_level=0.95):
        """
        Calculate optimal stock levels for each product.
        
        Args:
            service_level (float): Target service level (0.95 = 95%)
            
        Returns:
            pd.DataFrame: Optimal stock levels for each product
        """
        if self.inventory_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        # Calculate demand statistics by category
        demand_stats = self.sample_data.groupby('category')['demand_quantity'].agg([
            'mean', 'std', 'max'
        ]).reset_index()
        
        # Z-score for service level
        z_score = {
            0.90: 1.28,
            0.95: 1.65,
            0.99: 2.33
        }.get(service_level, 1.65)
        
        optimal_levels = []
        
        for _, row in self.inventory_data.iterrows():
            category = row['category']
            dark_store = row['dark_store_id']
            
            # Get demand statistics for this category
            cat_stats = demand_stats[demand_stats['category'] == category].iloc[0]
            
            # Calculate optimal stock levels
            avg_demand = cat_stats['mean']
            demand_std = cat_stats['std'] if cat_stats['std'] > 0 else avg_demand * 0.2
            lead_time = row['lead_time_hours']
            
            # Calculate components
            avg_demand_during_lead_time = avg_demand * (lead_time / 24)  # Convert to daily
            safety_stock = z_score * demand_std * np.sqrt(lead_time / 24)
            
            # Optimal order quantity (Economic Order Quantity approximation)
            holding_cost = row['storage_cost_per_unit'] * 0.2  # 20% holding cost
            order_cost = 50  # Assumed fixed ordering cost
            annual_demand = avg_demand * 365
            
            eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost) if holding_cost > 0 else avg_demand * 7
            
            # Calculate final recommendations
            reorder_point = avg_demand_during_lead_time + safety_stock
            max_stock = reorder_point + eoq
            
            optimal_levels.append({
                'dark_store_id': dark_store,
                'product_name': row['product_name'],
                'category': category,
                'current_stock': row['current_stock'],
                'avg_daily_demand': round(avg_demand, 1),
                'safety_stock': round(safety_stock, 1),
                'reorder_point': round(reorder_point, 1),
                'optimal_max_stock': round(max_stock, 1),
                'eoq': round(eoq, 1),
                'lead_time_hours': lead_time,
                'service_level': service_level
            })
        
        return pd.DataFrame(optimal_levels)
    
    def generate_restocking_schedule(self, forecast_horizon=72):
        """
        Generate restocking schedule based on demand forecasts and current inventory.
        
        Args:
            forecast_horizon (int): Hours to look ahead for restocking needs
            
        Returns:
            pd.DataFrame: Restocking schedule with priorities
        """
        # Get demand forecasts
        forecasts = self.forecast_demand(forecast_horizon)
        if forecasts is None:
            return None
        
        # Get optimal stock levels
        optimal_levels = self.calculate_optimal_stock_levels()
        if optimal_levels is None:
            return None
        
        restocking_schedule = []
        
        # Aggregate forecast by category for next 24 hours
        next_24h_demand = forecasts[forecasts['timestamp'] <= forecasts['timestamp'].min() + timedelta(hours=24)]
        demand_summary = next_24h_demand.groupby('category')['predicted_demand'].sum().reset_index()
        
        for _, inventory_row in self.inventory_data.iterrows():
            category = inventory_row['category']
            dark_store = inventory_row['dark_store_id']
            current_stock = inventory_row['current_stock']
            
            # Get optimal levels for this item
            optimal_row = optimal_levels[
                (optimal_levels['category'] == category) & 
                (optimal_levels['dark_store_id'] == dark_store)
            ]
            
            if len(optimal_row) == 0:
                continue
                
            optimal_data = optimal_row.iloc[0]
            reorder_point = optimal_data['reorder_point']
            max_stock = optimal_data['optimal_max_stock']
            
            # Get predicted demand for this category
            predicted_demand_24h = demand_summary[
                demand_summary['category'] == category
            ]['predicted_demand'].iloc[0] if len(demand_summary[demand_summary['category'] == category]) > 0 else 0
            
            # Calculate stock projection
            projected_stock_24h = current_stock - predicted_demand_24h
            
            # Determine if restocking is needed
            needs_restock = projected_stock_24h <= reorder_point
            urgency = 'Low'
            
            if projected_stock_24h <= 0:
                urgency = 'Critical'
            elif projected_stock_24h <= reorder_point * 0.5:
                urgency = 'High'
            elif projected_stock_24h <= reorder_point:
                urgency = 'Medium'
            
            # Calculate suggested order quantity
            if needs_restock:
                suggested_order = max_stock - current_stock
            else:
                suggested_order = 0
            
            restocking_schedule.append({
                'dark_store_id': dark_store,
                'product_name': inventory_row['product_name'],
                'category': category,
                'current_stock': current_stock,
                'predicted_demand_24h': round(predicted_demand_24h, 1),
                'projected_stock_24h': round(projected_stock_24h, 1),
                'reorder_point': round(reorder_point, 1),
                'needs_restock': needs_restock,
                'urgency': urgency,
                'suggested_order_qty': round(suggested_order, 1),
                'lead_time_hours': inventory_row['lead_time_hours'],
                'supplier_reliability': inventory_row['supplier_reliability']
            })
        
        schedule_df = pd.DataFrame(restocking_schedule)
        
        # Sort by urgency and projected stock
        urgency_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        schedule_df['urgency_score'] = schedule_df['urgency'].map(urgency_order)
        schedule_df = schedule_df.sort_values(['urgency_score', 'projected_stock_24h'], ascending=[False, True])
        
        return schedule_df
    
    def calculate_inventory_costs(self):
        """
        Calculate current inventory costs and optimization potential.
        
        Returns:
            dict: Inventory cost analysis
        """
        if self.inventory_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        # Calculate current costs
        self.inventory_data['holding_cost'] = (
            self.inventory_data['current_stock'] * 
            self.inventory_data['storage_cost_per_unit'] * 
            0.2  # Annual holding cost rate
        ) / 365  # Daily holding cost
        
        # Calculate stockout costs (estimated)
        demand_stats = self.sample_data.groupby('category')['demand_quantity'].mean().reset_index()
        demand_dict = dict(zip(demand_stats['category'], demand_stats['demand_quantity']))
        
        stockout_costs = []
        for _, row in self.inventory_data.iterrows():
            avg_demand = demand_dict.get(row['category'], 10)
            stockout_probability = max(0, (avg_demand - row['current_stock']) / avg_demand) if avg_demand > 0 else 0
            stockout_cost = stockout_probability * avg_demand * 5  # $5 per lost sale
            stockout_costs.append(stockout_cost)
        
        self.inventory_data['stockout_cost'] = stockout_costs
        self.inventory_data['total_cost'] = self.inventory_data['holding_cost'] + self.inventory_data['stockout_cost']
        
        # Aggregate costs
        cost_analysis = {
            'total_holding_cost_daily': round(self.inventory_data['holding_cost'].sum(), 2),
            'total_stockout_cost_daily': round(self.inventory_data['stockout_cost'].sum(), 2),
            'total_inventory_cost_daily': round(self.inventory_data['total_cost'].sum(), 2),
            'cost_by_category': self.inventory_data.groupby('category')['total_cost'].sum().round(2).to_dict(),
            'cost_by_store': self.inventory_data.groupby('dark_store_id')['total_cost'].sum().round(2).to_dict()
        }
        
        return cost_analysis
    
    def create_optimization_report(self):
        """
        Create a comprehensive inventory optimization report.
        
        Returns:
            dict: Complete optimization analysis
        """
        if not self.load_data():
            return None
        
        print("🤖 Training demand forecasting models...")
        model_performance = self.train_demand_forecasting_models()
        
        print("📈 Generating demand forecasts...")
        forecasts = self.forecast_demand(24)
        
        print("📊 Calculating optimal stock levels...")
        optimal_levels = self.calculate_optimal_stock_levels()
        
        print("📋 Generating restocking schedule...")
        restocking_schedule = self.generate_restocking_schedule()
        
        print("💰 Calculating inventory costs...")
        cost_analysis = self.calculate_inventory_costs()
        
        optimization_report = {
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_performance': model_performance,
            'demand_forecasts': forecasts,
            'optimal_stock_levels': optimal_levels,
            'restocking_schedule': restocking_schedule,
            'cost_analysis': cost_analysis
        }
        
        return optimization_report

def main():
    """
    Main function to run the inventory optimization.
    """
    print("🚀 Starting Flipkart Minutes Inventory Optimization...")
    print("=" * 55)
    
    # Initialize optimizer
    optimizer = InventoryOptimizer()
    
    # Generate complete optimization report
    report = optimizer.create_optimization_report()
    
    if report:
        print("\n📊 OPTIMIZATION SUMMARY")
        print("-" * 30)
        
        # Display cost analysis
        costs = report['cost_analysis']
        print(f"Total Daily Inventory Cost: ${costs['total_inventory_cost_daily']:.2f}")
        print(f"  - Holding Costs: ${costs['total_holding_cost_daily']:.2f}")
        print(f"  - Stockout Costs: ${costs['total_stockout_cost_daily']:.2f}")
        
        # Display restocking priorities
        urgent_items = report['restocking_schedule'][
            report['restocking_schedule']['urgency'].isin(['Critical', 'High'])
        ]
        print(f"\nItems needing urgent restocking: {len(urgent_items)}")
        
        if len(urgent_items) > 0:
            print("\nTOP RESTOCKING PRIORITIES:")
            for _, item in urgent_items.head(3).iterrows():
                print(f"  - {item['product_name']} at {item['dark_store_id']}: {item['urgency']} priority")
        
        # Display model performance
        print("\n🤖 MODEL PERFORMANCE")
        print("-" * 30)
        for category, perf in report['model_performance'].items():
            print(f"{category}: MAPE {perf['MAPE']:.1f}%")
        
        print("\n✅ Optimization completed successfully!")
        return report
    else:
        print("❌ Optimization failed. Please check your data files.")
        return None

if __name__ == "__main__":
    # Run the optimization
    results = main()
