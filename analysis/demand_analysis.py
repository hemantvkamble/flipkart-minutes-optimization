"""
Flipkart Minutes Optimization - Demand Analysis Module

This module provides comprehensive demand analysis for Flipkart's 10-15 minute delivery service.
It analyzes demand patterns, identifies bottlenecks, and calculates key performance metrics.

Author: Product Manager
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DemandAnalyzer:
    """
    A comprehensive demand analysis class for Flipkart Minutes optimization.
    
    This class provides methods to:
    - Load and clean demand data
    - Analyze demand patterns by time, product, and location
    - Identify peak hours and bottlenecks
    - Calculate out-of-stock frequency and impact
    - Generate actionable insights for inventory optimization
    """
    
    def __init__(self, data_path='../data/'):
        """
        Initialize the DemandAnalyzer with data path.
        
        Args:
            data_path (str): Path to the data directory
        """
        self.data_path = data_path
        self.sample_data = None
        self.demand_patterns = None
        self.inventory_data = None
        
    def load_data(self):
        """
        Load all required datasets for demand analysis.
        
        Returns:
            bool: True if all data loaded successfully, False otherwise
        """
        try:
            # Load sample transaction data
            self.sample_data = pd.read_csv(f'{self.data_path}sample_data.csv')
            self.sample_data['timestamp'] = pd.to_datetime(self.sample_data['timestamp'])
            self.sample_data['hour'] = self.sample_data['timestamp'].dt.hour
            self.sample_data['day_of_week'] = self.sample_data['timestamp'].dt.dayofweek
            
            # Load demand patterns
            self.demand_patterns = pd.read_csv(f'{self.data_path}demand_patterns.csv')
            
            # Load inventory data
            self.inventory_data = pd.read_csv(f'{self.data_path}inventory_data.csv')
            
            print("✅ All data loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def analyze_demand_patterns(self):
        """
        Analyze demand patterns across different dimensions.
        
        Returns:
            dict: Dictionary containing various demand analysis results
        """
        if self.sample_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        analysis_results = {}
        
        # 1. Hourly demand analysis
        hourly_demand = self.sample_data.groupby(['hour', 'category']).agg({
            'demand_quantity': 'sum',
            'orders_fulfilled': 'sum',
            'orders_cancelled': 'sum'
        }).reset_index()
        
        hourly_demand['fulfillment_rate'] = (
            hourly_demand['orders_fulfilled'] / 
            (hourly_demand['orders_fulfilled'] + hourly_demand['orders_cancelled'])
        ).fillna(0)
        
        analysis_results['hourly_demand'] = hourly_demand
        
        # 2. Product category analysis
        category_analysis = self.sample_data.groupby('category').agg({
            'demand_quantity': ['sum', 'mean', 'std'],
            'orders_fulfilled': 'sum',
            'orders_cancelled': 'sum',
            'delivery_time_minutes': 'mean',
            'csat_score': 'mean'
        }).round(2)
        
        category_analysis.columns = ['_'.join(col).strip() for col in category_analysis.columns.values]
        analysis_results['category_analysis'] = category_analysis
        
        # 3. Peak hours identification
        peak_hours = self.sample_data.groupby('hour')['demand_quantity'].sum().sort_values(ascending=False)
        analysis_results['peak_hours'] = peak_hours.head(5)
        
        # 4. Out-of-stock analysis
        self.sample_data['stock_shortage'] = np.maximum(
            0, self.sample_data['demand_quantity'] - self.sample_data['stock_available']
        )
        
        oos_analysis = self.sample_data.groupby(['category', 'hour']).agg({
            'stock_shortage': 'sum',
            'demand_quantity': 'sum'
        }).reset_index()
        
        oos_analysis['oos_rate'] = (oos_analysis['stock_shortage'] / oos_analysis['demand_quantity']).fillna(0)
        analysis_results['oos_analysis'] = oos_analysis
        
        # 5. Dark store performance comparison
        store_performance = self.sample_data.groupby('dark_store_id').agg({
            'orders_fulfilled': 'sum',
            'orders_cancelled': 'sum',
            'delivery_time_minutes': 'mean',
            'csat_score': 'mean'
        }).round(2)
        
        store_performance['total_orders'] = (
            store_performance['orders_fulfilled'] + store_performance['orders_cancelled']
        )
        store_performance['fulfillment_rate'] = (
            store_performance['orders_fulfilled'] / store_performance['total_orders']
        ).round(3)
        
        analysis_results['store_performance'] = store_performance
        
        return analysis_results
    
    def identify_bottlenecks(self):
        """
        Identify key bottlenecks in the system.
        
        Returns:
            dict: Dictionary containing bottleneck analysis
        """
        if self.sample_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        bottlenecks = {}
        
        # 1. High cancellation rate periods
        cancellation_analysis = self.sample_data.groupby(['hour', 'category']).agg({
            'orders_cancelled': 'sum',
            'orders_fulfilled': 'sum'
        }).reset_index()
        
        cancellation_analysis['total_orders'] = (
            cancellation_analysis['orders_cancelled'] + cancellation_analysis['orders_fulfilled']
        )
        cancellation_analysis['cancellation_rate'] = (
            cancellation_analysis['orders_cancelled'] / cancellation_analysis['total_orders']
        ).fillna(0)
        
        high_cancellation = cancellation_analysis[
            cancellation_analysis['cancellation_rate'] > 0.2
        ].sort_values('cancellation_rate', ascending=False)
        
        bottlenecks['high_cancellation_periods'] = high_cancellation
        
        # 2. Long delivery time periods
        delivery_time_analysis = self.sample_data.groupby(['hour', 'category']).agg({
            'delivery_time_minutes': 'mean'
        }).reset_index()
        
        slow_delivery = delivery_time_analysis[
            delivery_time_analysis['delivery_time_minutes'] > 20
        ].sort_values('delivery_time_minutes', ascending=False)
        
        bottlenecks['slow_delivery_periods'] = slow_delivery
        
        # 3. Low customer satisfaction periods
        low_csat = self.sample_data[
            self.sample_data['csat_score'] < 3.5
        ].groupby(['hour', 'category']).agg({
            'csat_score': 'mean',
            'orders_fulfilled': 'count'
        }).reset_index().sort_values('csat_score')
        
        bottlenecks['low_satisfaction_periods'] = low_csat
        
        return bottlenecks
    
    def calculate_key_metrics(self):
        """
        Calculate key performance metrics for the system.
        
        Returns:
            dict: Dictionary containing key metrics
        """
        if self.sample_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        metrics = {}
        
        # Overall metrics
        total_demand = self.sample_data['demand_quantity'].sum()
        total_fulfilled = self.sample_data['orders_fulfilled'].sum()
        total_cancelled = self.sample_data['orders_cancelled'].sum()
        
        metrics['total_demand'] = total_demand
        metrics['total_fulfilled'] = total_fulfilled
        metrics['total_cancelled'] = total_cancelled
        metrics['overall_fulfillment_rate'] = round(total_fulfilled / (total_fulfilled + total_cancelled), 3)
        metrics['overall_cancellation_rate'] = round(total_cancelled / (total_fulfilled + total_cancelled), 3)
        
        # Out-of-stock metrics
        if 'stock_shortage' in self.sample_data.columns:
            total_shortage = self.sample_data['stock_shortage'].sum()
        else:
            # Fallback: estimate from cancellations
            total_shortage = self.sample_data['orders_cancelled'].sum() * 0.6
            
        if 'demand_quantity' in self.sample_data.columns:
            total_demand = self.sample_data['demand_quantity'].sum()
        else:
            total_demand = self.sample_data['orders_fulfilled'].sum() + self.sample_data['orders_cancelled'].sum()

        metrics['out_of_stock_rate'] = total_shortage / total_demand if total_demand > 0 else 0.25
        
        # Delivery performance
        metrics['avg_delivery_time'] = round(self.sample_data['delivery_time_minutes'].mean(), 1)
        metrics['delivery_time_std'] = round(self.sample_data['delivery_time_minutes'].std(), 1)
        
        # Customer satisfaction
        metrics['avg_csat_score'] = round(self.sample_data['csat_score'].mean(), 2)
        metrics['csat_below_3'] = len(self.sample_data[self.sample_data['csat_score'] < 3]) / len(self.sample_data)
        
        # Performance by category
        category_metrics = self.sample_data.groupby('category').agg({
            'orders_fulfilled': 'sum',
            'orders_cancelled': 'sum',
            'delivery_time_minutes': 'mean',
            'csat_score': 'mean'
        }).round(2)
        
        category_metrics['fulfillment_rate'] = (
            category_metrics['orders_fulfilled'] / 
            (category_metrics['orders_fulfilled'] + category_metrics['orders_cancelled'])
        ).round(3)
        
        metrics['category_performance'] = category_metrics
        
        return metrics
    
    def generate_insights(self):
        """
        Generate actionable insights based on the analysis.
        
        Returns:
            list: List of actionable insights
        """
        if self.sample_data is None:
            print("❌ Please load data first using load_data()")
            return None
        
        insights = []
        
        # Analyze the data for insights
        analysis = self.analyze_demand_patterns()
        bottlenecks = self.identify_bottlenecks()
        metrics = self.calculate_key_metrics()
        
        # Generate insights based on analysis
        if metrics['out_of_stock_rate'] > 0.15:
            insights.append({
                'type': 'Critical',
                'category': 'Inventory',
                'insight': f"High out-of-stock rate of {metrics['out_of_stock_rate']:.1%} requires immediate attention",
                'recommendation': 'Implement dynamic inventory reordering based on demand patterns'
            })
        
        if metrics['avg_delivery_time'] > 15:
            insights.append({
                'type': 'Important',
                'category': 'Delivery',
                'insight': f"Average delivery time of {metrics['avg_delivery_time']} minutes exceeds target",
                'recommendation': 'Optimize delivery routes and consider additional dark stores'
            })
        
        if metrics['overall_cancellation_rate'] > 0.10:
            insights.append({
                'type': 'Critical',
                'category': 'Operations',
                'insight': f"High cancellation rate of {metrics['overall_cancellation_rate']:.1%}",
                'recommendation': 'Focus on improving stock availability during peak hours'
            })
        
        # Peak hour insights
        peak_hours = analysis['peak_hours']
        insights.append({
            'type': 'Opportunity',
            'category': 'Demand',
            'insight': f"Peak demand hours are {list(peak_hours.head(3).index)} with potential for optimization",
            'recommendation': 'Pre-position inventory and increase staffing during these hours'
        })
        
        # Category-specific insights
        category_performance = metrics['category_performance']
        worst_category = category_performance.loc[category_performance['fulfillment_rate'].idxmin()]
        insights.append({
            'type': 'Important',
            'category': 'Product',
            'insight': f"Lowest performing category is {worst_category.name} with {worst_category['fulfillment_rate']:.1%} fulfillment rate",
            'recommendation': f'Focus inventory optimization efforts on {worst_category.name} category'
        })
        
        return insights
    
    def create_summary_report(self):
        """
        Create a comprehensive summary report.
        
        Returns:
            dict: Complete analysis summary
        """
        if not self.load_data():
            return None
        
        print("🔍 Analyzing demand patterns...")
        analysis = self.analyze_demand_patterns()
        
        print("🚨 Identifying bottlenecks...")
        bottlenecks = self.identify_bottlenecks()
        
        print("📊 Calculating key metrics...")
        metrics = self.calculate_key_metrics()
        
        print("💡 Generating insights...")
        insights = self.generate_insights()
        
        summary_report = {
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'key_metrics': metrics,
            'demand_analysis': analysis,
            'bottlenecks': bottlenecks,
            'insights': insights
        }
        
        return summary_report

def main():
    """
    Main function to run the demand analysis.
    """
    print("🚀 Starting Flipkart Minutes Demand Analysis...")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = DemandAnalyzer()
    
    # Generate complete analysis
    report = analyzer.create_summary_report()
    
    if report:
        print("\n📈 KEY METRICS SUMMARY")
        print("-" * 30)
        metrics = report['key_metrics']
        print(f"Overall Fulfillment Rate: {metrics['overall_fulfillment_rate']:.1%}")
        print(f"Out-of-Stock Rate: {metrics['out_of_stock_rate']:.1%}")
        print(f"Average Delivery Time: {metrics['avg_delivery_time']} minutes")
        print(f"Customer Satisfaction: {metrics['avg_csat_score']}/5.0")
        
        print("\n💡 TOP INSIGHTS")
        print("-" * 30)
        for i, insight in enumerate(report['insights'][:3], 1):
            print(f"{i}. [{insight['type']}] {insight['insight']}")
            print(f"   Recommendation: {insight['recommendation']}\n")
        
        print("✅ Analysis completed successfully!")
        print("📊 Full report available in the returned dictionary")
        
        return report
    else:
        print("❌ Analysis failed. Please check your data files.")
        return None

if __name__ == "__main__":
    # Run the analysis
    results = main()
