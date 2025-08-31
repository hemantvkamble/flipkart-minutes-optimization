"""
Flipkart Minutes Optimization - Visualization Charts Module

This module provides comprehensive visualization capabilities for the Flipkart Minutes optimization project.
It creates interactive charts, graphs, and visual        if save_html:
            fig.write_html('visualizations/delivery_trends.html')
            print("✅ Delivery trends chart saved as HTML")alytics for stakeholder presentations.

Author: Product Manager
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class FlipkartVisualizationSuite:
    """
    Comprehensive visualization suite for Flipkart Minutes optimization analysis.
    
    This class provides methods to create:
    - Interactive time series charts
    - Heatmaps for demand patterns
    - Performance dashboards
    - Geographic delivery zone maps
    - Business metric visualizations
    """
    
    def __init__(self, data_path='data/'):
        """
        Initialize the visualization suite.
        
        Args:
            data_path (str): Path to the data directory
        """
        self.data_path = data_path
        self.sample_data = None
        self.demand_patterns = None
        self.colors = {
            'primary': '#FF6B35',      # Flipkart Orange
            'secondary': '#047BD2',     # Flipkart Blue
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545',
            'info': '#17A2B8'
        }
        
    def load_data(self):
        """Load all required datasets for visualization."""
        try:
            self.sample_data = pd.read_csv(f'{self.data_path}sample_data.csv')
            self.sample_data['timestamp'] = pd.to_datetime(self.sample_data['timestamp'])
            self.sample_data['hour'] = self.sample_data['timestamp'].dt.hour
            
            self.demand_patterns = pd.read_csv(f'{self.data_path}demand_patterns.csv')
            
            print("✅ Visualization data loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def create_demand_heatmap(self, save_html=True):
        """
        Create an interactive heatmap showing demand patterns by hour and category.
        
        Args:
            save_html (bool): Whether to save as HTML file
            
        Returns:
            plotly.graph_objects.Figure: Interactive heatmap
        """
        if self.sample_data is None:
            self.load_data()
        
        # Prepare data for heatmap
        heatmap_data = self.sample_data.groupby(['hour', 'category'])['demand_quantity'].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='category', columns='hour', values='demand_quantity')
        
        # Create interactive heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='RdYlBu_r',
            hovertemplate='<b>%{y}</b><br>Hour: %{x}<br>Demand: %{z}<extra></extra>',
            colorbar=dict(title="Demand Quantity")
        ))
        
        fig.update_layout(
            title={
                'text': 'Demand Patterns Heatmap - Hourly Demand by Product Category',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': self.colors['primary']}
            },
            xaxis_title='Hour of Day',
            yaxis_title='Product Category',
            font=dict(size=12),
            height=500,
            width=1000
        )
        
        if save_html:
            fig.write_html('visualizations/demand_heatmap.html')
            print("✅ Demand heatmap saved as HTML")
        
        return fig
    
    def create_delivery_time_trends(self, save_html=True):
        """
        Create delivery time trend analysis with multiple metrics.
        
        Args:
            save_html (bool): Whether to save as HTML file
            
        Returns:
            plotly.graph_objects.Figure: Multi-metric delivery trends
        """
        if self.sample_data is None:
            self.load_data()
        
        # Prepare data
        hourly_stats = self.sample_data.groupby('hour').agg({
            'delivery_time_minutes': ['mean', 'std'],
            'orders_fulfilled': 'sum',
            'orders_cancelled': 'sum',
            'csat_score': 'mean'
        }).round(2)
        
        hourly_stats.columns = ['avg_delivery_time', 'delivery_std', 'fulfilled', 'cancelled', 'avg_csat']
        hourly_stats = hourly_stats.reset_index()
        hourly_stats['total_orders'] = hourly_stats['fulfilled'] + hourly_stats['cancelled']
        hourly_stats['success_rate'] = (hourly_stats['fulfilled'] / hourly_stats['total_orders'] * 100).round(1)
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Average Delivery Time', 'Order Success Rate', 'Customer Satisfaction', 'Order Volume'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Delivery time trend
        fig.add_trace(
            go.Scatter(
                x=hourly_stats['hour'],
                y=hourly_stats['avg_delivery_time'],
                mode='lines+markers',
                name='Avg Delivery Time',
                line=dict(color=self.colors['primary'], width=3),
                hovertemplate='Hour: %{x}<br>Delivery Time: %{y:.1f} min<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add target line for delivery time
        fig.add_hline(y=12, line_dash="dash", line_color="red", 
                     annotation_text="Target: 12 min", row=1, col=1)
        
        # Success rate
        fig.add_trace(
            go.Scatter(
                x=hourly_stats['hour'],
                y=hourly_stats['success_rate'],
                mode='lines+markers',
                name='Success Rate',
                line=dict(color=self.colors['success'], width=3),
                hovertemplate='Hour: %{x}<br>Success Rate: %{y:.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Customer satisfaction
        fig.add_trace(
            go.Scatter(
                x=hourly_stats['hour'],
                y=hourly_stats['avg_csat'],
                mode='lines+markers',
                name='Customer Satisfaction',
                line=dict(color=self.colors['info'], width=3),
                hovertemplate='Hour: %{x}<br>CSAT: %{y:.1f}/5<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Order volume
        fig.add_trace(
            go.Bar(
                x=hourly_stats['hour'],
                y=hourly_stats['total_orders'],
                name='Total Orders',
                marker_color=self.colors['secondary'],
                hovertemplate='Hour: %{x}<br>Orders: %{y}<extra></extra>'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': 'Delivery Performance Dashboard - Hourly Trends',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': self.colors['primary']}
            },
            height=700,
            showlegend=False
        )
        
        # Update axis labels
        fig.update_xaxes(title_text="Hour of Day", row=2, col=1)
        fig.update_xaxes(title_text="Hour of Day", row=2, col=2)
        fig.update_yaxes(title_text="Minutes", row=1, col=1)
        fig.update_yaxes(title_text="Percentage", row=1, col=2)
        fig.update_yaxes(title_text="Score (1-5)", row=2, col=1)
        fig.update_yaxes(title_text="Number of Orders", row=2, col=2)
        
        if save_html:
            fig.write_html('visualizations/delivery_trends.html')
            print("✅ Delivery trends dashboard saved as HTML")
        
        return fig
    
    def create_performance_comparison(self, save_html=True):
        """
        Create dark store performance comparison charts.
        
        Args:
            save_html (bool): Whether to save as HTML file
            
        Returns:
            plotly.graph_objects.Figure: Performance comparison charts
        """
        if self.sample_data is None:
            self.load_data()
        
        # Calculate store performance metrics
        store_performance = self.sample_data.groupby('dark_store_id').agg({
            'orders_fulfilled': 'sum',
            'orders_cancelled': 'sum',
            'delivery_time_minutes': 'mean',
            'csat_score': 'mean'
        }).round(2)
        
        store_performance['total_orders'] = store_performance['orders_fulfilled'] + store_performance['orders_cancelled']
        store_performance['success_rate'] = (store_performance['orders_fulfilled'] / store_performance['total_orders'] * 100).round(1)
        store_performance = store_performance.reset_index()
        
        # Create comparison charts
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Order Success Rate by Store', 'Average Delivery Time', 
                           'Customer Satisfaction', 'Order Volume'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Success rate comparison
        fig.add_trace(
            go.Bar(
                x=store_performance['dark_store_id'],
                y=store_performance['success_rate'],
                name='Success Rate',
                marker_color=self.colors['success'],
                text=store_performance['success_rate'].astype(str) + '%',
                textposition='auto',
                hovertemplate='Store: %{x}<br>Success Rate: %{y:.1f}%<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Delivery time comparison
        colors = [self.colors['success'] if x <= 15 else self.colors['warning'] if x <= 20 else self.colors['danger'] 
                 for x in store_performance['delivery_time_minutes']]
        
        fig.add_trace(
            go.Bar(
                x=store_performance['dark_store_id'],
                y=store_performance['delivery_time_minutes'],
                name='Avg Delivery Time',
                marker_color=colors,
                text=store_performance['delivery_time_minutes'].astype(str) + ' min',
                textposition='auto',
                hovertemplate='Store: %{x}<br>Delivery Time: %{y:.1f} min<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Customer satisfaction
        fig.add_trace(
            go.Bar(
                x=store_performance['dark_store_id'],
                y=store_performance['csat_score'],
                name='CSAT Score',
                marker_color=self.colors['info'],
                text=store_performance['csat_score'].astype(str),
                textposition='auto',
                hovertemplate='Store: %{x}<br>CSAT: %{y:.1f}/5<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Order volume
        fig.add_trace(
            go.Bar(
                x=store_performance['dark_store_id'],
                y=store_performance['total_orders'],
                name='Total Orders',
                marker_color=self.colors['secondary'],
                text=store_performance['total_orders'].astype(str),
                textposition='auto',
                hovertemplate='Store: %{x}<br>Orders: %{y}<extra></extra>'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': 'Dark Store Performance Comparison',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': self.colors['primary']}
            },
            height=700,
            showlegend=False
        )
        
        # Add reference lines
        fig.add_hline(y=90, line_dash="dash", line_color="red", 
                     annotation_text="Target: 90%", row=1, col=1)
        fig.add_hline(y=15, line_dash="dash", line_color="red", 
                     annotation_text="Target: 15 min", row=1, col=2)
        fig.add_hline(y=4.0, line_dash="dash", line_color="red", 
                     annotation_text="Target: 4.0", row=2, col=1)
        
        if save_html:
            fig.write_html('visualizations/store_performance.html')
            print("✅ Store performance comparison saved as HTML")
        
        return fig
    
    def create_category_analysis(self, save_html=True):
        """
        Create product category performance analysis.
        
        Args:
            save_html (bool): Whether to save as HTML file
            
        Returns:
            plotly.graph_objects.Figure: Category analysis charts
        """
        if self.sample_data is None:
            self.load_data()
        
        # Calculate category metrics
        category_stats = self.sample_data.groupby('category').agg({
            'demand_quantity': 'sum',
            'orders_fulfilled': 'sum',
            'orders_cancelled': 'sum',
            'delivery_time_minutes': 'mean',
            'csat_score': 'mean'
        }).round(2)
        
        category_stats['total_orders'] = category_stats['orders_fulfilled'] + category_stats['orders_cancelled']
        category_stats['fulfillment_rate'] = (category_stats['orders_fulfilled'] / category_stats['total_orders'] * 100).round(1)
        category_stats['cancellation_rate'] = (category_stats['orders_cancelled'] / category_stats['total_orders'] * 100).round(1)
        category_stats = category_stats.reset_index()
        
        # Create visualizations
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Demand by Category', 'Fulfillment vs Cancellation Rate', 
                           'Average Delivery Time by Category', 'Customer Satisfaction by Category'),
            specs=[[{"type": "pie"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Demand distribution pie chart
        fig.add_trace(
            go.Pie(
                labels=category_stats['category'],
                values=category_stats['demand_quantity'],
                name="Demand Distribution",
                hovertemplate='<b>%{label}</b><br>Demand: %{value}<br>Percentage: %{percent}<extra></extra>',
                marker_colors=px.colors.qualitative.Set3[:len(category_stats)]
            ),
            row=1, col=1
        )
        
        # Fulfillment vs Cancellation scatter
        fig.add_trace(
            go.Scatter(
                x=category_stats['fulfillment_rate'],
                y=category_stats['cancellation_rate'],
                mode='markers+text',
                text=category_stats['category'],
                textposition="top center",
                name='Categories',
                marker=dict(
                    size=category_stats['demand_quantity']/5,
                    color=category_stats['csat_score'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="CSAT Score", x=1.1)
                ),
                hovertemplate='<b>%{text}</b><br>Fulfillment: %{x:.1f}%<br>Cancellation: %{y:.1f}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Delivery time by category
        fig.add_trace(
            go.Bar(
                x=category_stats['category'],
                y=category_stats['delivery_time_minutes'],
                name='Avg Delivery Time',
                marker_color=self.colors['warning'],
                text=category_stats['delivery_time_minutes'].astype(str) + ' min',
                textposition='auto',
                hovertemplate='Category: %{x}<br>Delivery Time: %{y:.1f} min<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Customer satisfaction by category
        fig.add_trace(
            go.Bar(
                x=category_stats['category'],
                y=category_stats['csat_score'],
                name='CSAT Score',
                marker_color=self.colors['info'],
                text=category_stats['csat_score'].astype(str),
                textposition='auto',
                hovertemplate='Category: %{x}<br>CSAT: %{y:.1f}/5<extra></extra>'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': 'Product Category Performance Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': self.colors['primary']}
            },
            height=800,
            showlegend=False
        )
        
        # Update axis labels
        fig.update_xaxes(title_text="Fulfillment Rate (%)", row=1, col=2)
        fig.update_yaxes(title_text="Cancellation Rate (%)", row=1, col=2)
        fig.update_xaxes(title_text="Category", row=2, col=1)
        fig.update_yaxes(title_text="Minutes", row=2, col=1)
        fig.update_xaxes(title_text="Category", row=2, col=2)
        fig.update_yaxes(title_text="Score (1-5)", row=2, col=2)
        
        if save_html:
            fig.write_html('visualizations/category_analysis.html')
            print("✅ Category analysis saved as HTML")
        
        return fig
    
    def create_kpi_dashboard(self, save_html=True):
        """
        Create a comprehensive KPI dashboard.
        
        Args:
            save_html (bool): Whether to save as HTML file
            
        Returns:
            plotly.graph_objects.Figure: KPI dashboard
        """
        if self.sample_data is None:
            self.load_data()
        
        # Calculate key metrics
        total_orders = len(self.sample_data)
        total_fulfilled = self.sample_data['orders_fulfilled'].sum()
        total_cancelled = self.sample_data['orders_cancelled'].sum()
        avg_delivery_time = self.sample_data['delivery_time_minutes'].mean()
        avg_csat = self.sample_data['csat_score'].mean()
        
        fulfillment_rate = (total_fulfilled / (total_fulfilled + total_cancelled)) * 100
        on_time_rate = (self.sample_data['delivery_time_minutes'] <= 15).sum() / len(self.sample_data) * 100
        
        # Create KPI cards
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=('Fulfillment Rate', 'Average Delivery Time', 'Customer Satisfaction',
                           'On-Time Delivery Rate', 'Total Orders Processed', 'Order Cancellation Rate',
                           'Peak Hour Performance', 'Category Performance', 'Store Efficiency'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "bar"}, {"type": "pie"}, {"type": "bar"}]]
        )
        
        # KPI Indicators
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = fulfillment_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Fulfillment Rate (%)"},
            delta = {'reference': 95},
            gauge = {'axis': {'range': [None, 100]},
                    'bar': {'color': self.colors['success']},
                    'steps': [{'range': [0, 90], 'color': "lightgray"},
                             {'range': [90, 95], 'color': "gray"}],
                    'threshold': {'line': {'color': "red", 'width': 4},
                                 'thickness': 0.75, 'value': 95}}),
            row=1, col=1)
        
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = avg_delivery_time,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Avg Delivery Time (min)"},
            delta = {'reference': 12},
            gauge = {'axis': {'range': [0, 30]},
                    'bar': {'color': self.colors['warning']},
                    'steps': [{'range': [0, 12], 'color': "lightgreen"},
                             {'range': [12, 20], 'color': "yellow"},
                             {'range': [20, 30], 'color': "lightcoral"}],
                    'threshold': {'line': {'color': "red", 'width': 4},
                                 'thickness': 0.75, 'value': 15}}),
            row=1, col=2)
        
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = avg_csat,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Customer Satisfaction"},
            delta = {'reference': 4.2},
            gauge = {'axis': {'range': [1, 5]},
                    'bar': {'color': self.colors['info']},
                    'steps': [{'range': [1, 3], 'color': "lightcoral"},
                             {'range': [3, 4], 'color': "yellow"},
                             {'range': [4, 5], 'color': "lightgreen"}],
                    'threshold': {'line': {'color': "red", 'width': 4},
                                 'thickness': 0.75, 'value': 4.0}}),
            row=1, col=3)
        
        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = on_time_rate,
            title = {"text": "On-Time Delivery (%)"},
            delta = {'reference': 85, 'valueformat': '.1f'},
            number = {'valueformat': '.1f'}),
            row=2, col=1)
        
        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = total_orders,
            title = {"text": "Total Orders"},
            delta = {'reference': 500, 'relative': True},
            number = {'valueformat': '.0f'}),
            row=2, col=2)
        
        cancellation_rate = (total_cancelled / (total_fulfilled + total_cancelled)) * 100
        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = cancellation_rate,
            title = {"text": "Cancellation Rate (%)"},
            delta = {'reference': 10, 'valueformat': '.1f'},
            number = {'valueformat': '.1f'}),
            row=2, col=3)
        
        # Peak hour performance
        peak_hours_data = self.sample_data[self.sample_data['hour'].isin([8, 18, 19])]
        peak_performance = peak_hours_data['delivery_time_minutes'].mean()
        off_peak_data = self.sample_data[~self.sample_data['hour'].isin([7, 8, 9, 17, 18, 19, 20])]
        off_peak_performance = off_peak_data['delivery_time_minutes'].mean()
        
        fig.add_trace(go.Bar(
            x=['Peak Hours', 'Off-Peak Hours'],
            y=[peak_performance, off_peak_performance],
            marker_color=[self.colors['danger'], self.colors['success']],
            text=[f'{peak_performance:.1f} min', f'{off_peak_performance:.1f} min'],
            textposition='auto'),
            row=3, col=1)
        
        # Category performance pie chart
        category_fulfillment = self.sample_data.groupby('category')['orders_fulfilled'].sum()
        fig.add_trace(go.Pie(
            labels=category_fulfillment.index,
            values=category_fulfillment.values,
            name="Category Performance"),
            row=3, col=2)
        
        # Store efficiency
        store_efficiency = self.sample_data.groupby('dark_store_id')['delivery_time_minutes'].mean()
        fig.add_trace(go.Bar(
            x=store_efficiency.index,
            y=store_efficiency.values,
            marker_color=self.colors['secondary'],
            text=[f'{x:.1f} min' for x in store_efficiency.values],
            textposition='auto'),
            row=3, col=3)
        
        fig.update_layout(
            title={
                'text': 'Flipkart Minutes - Executive KPI Dashboard',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': self.colors['primary']}
            },
            height=1000,
            showlegend=False
        )
        
        if save_html:
            fig.write_html('visualizations/kpi_dashboard.html')
            print("✅ KPI dashboard saved as HTML")
        
        return fig
    
    def generate_all_visualizations(self):
        """
        Generate all visualization charts and save them.
        
        Returns:
            dict: Dictionary containing all generated figures
        """
        if not self.load_data():
            return None
        
        print("📊 Generating all visualizations...")
        print("=" * 40)
        
        visualizations = {}
        
        print("1. Creating demand heatmap...")
        visualizations['demand_heatmap'] = self.create_demand_heatmap()
        
        print("2. Creating delivery trends dashboard...")
        visualizations['delivery_trends'] = self.create_delivery_time_trends()
        
        print("3. Creating store performance comparison...")
        visualizations['store_performance'] = self.create_performance_comparison()
        
        print("4. Creating category analysis...")
        visualizations['category_analysis'] = self.create_category_analysis()
        
        print("5. Creating KPI dashboard...")
        visualizations['kpi_dashboard'] = self.create_kpi_dashboard()
        
        print("\n✅ All visualizations generated successfully!")
        print("📁 Files saved in 'visualizations/' directory")
        
        return visualizations

def main():
    """
    Main function to generate all visualizations.
    """
    print("🚀 Starting Flipkart Minutes Visualization Suite...")
    print("=" * 50)
    
    # Initialize visualization suite
    viz_suite = FlipkartVisualizationSuite()
    
    # Generate all visualizations
    charts = viz_suite.generate_all_visualizations()
    
    if charts:
        print(f"\n📈 VISUALIZATION SUMMARY")
        print("-" * 30)
        print(f"Total charts generated: {len(charts)}")
        print("Available visualizations:")
        for name in charts.keys():
            print(f"  - {name}")
        
        print("\n🎨 All charts are interactive and ready for presentations!")
        return charts
    else:
        print("❌ Visualization generation failed.")
        return None

if __name__ == "__main__":
    # Run the visualization generation
    results = main()
