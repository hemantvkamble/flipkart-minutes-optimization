"""
Flipkart Minutes Optimization - Main Streamlit Dashboard

This is the main interactive dashboard for the Flipkart Minutes optimization project.
It provides a comprehensive view of demand analysis, inventory optimization, and delivery zone mapping.

Author: Product Manager
Date: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add analysis modules to path
sys.path.append('./analysis')

try:
    from demand_analysis import DemandAnalyzer
    from inventory_optimization import InventoryOptimizer
    from delivery_zone_mapping import DeliveryZoneMapper
except ImportError as e:
    st.error(f"Error importing analysis modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Flipkart Minutes Optimization",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FF6B35;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #047BD2;
        margin: 1rem 0;
    }
    .stSelectbox > div > div > select {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

class FlipkartDashboard:
    """Main dashboard class for Flipkart Minutes optimization."""
    
    def __init__(self):
        self.demand_analyzer = DemandAnalyzer(data_path='./data/')
        self.inventory_optimizer = InventoryOptimizer(data_path='./data/')
        self.zone_mapper = DeliveryZoneMapper(data_path='./data/')
        
    def load_data(self):
        """Load data for all analyzers."""
        try:
            success = all([
                self.demand_analyzer.load_data(),
                self.inventory_optimizer.load_data(),
                self.zone_mapper.load_data()
            ])
            return success
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return False
    
    def render_homepage(self):
        """Render the homepage with project overview."""
        st.markdown('<h1 class="main-header">🚀 Flipkart Minutes Optimization Strategy</h1>', unsafe_allow_html=True)
        
        # Project overview
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 📊 Project Overview
            
            This comprehensive optimization strategy addresses key challenges in Flipkart's 10-15 minute delivery service:
            
            - **Delivery Delays**: Currently averaging 18 minutes, targeting 12 minutes
            - **Out-of-Stock Issues**: 25% out-of-stock rate, targeting 10%
            - **Customer Satisfaction**: 3.2/5 score, targeting 4.2/5
            - **Order Cancellations**: 15% cancellation rate, targeting 5%
            """)
        
        # Key metrics section
        st.markdown("### 📈 Current Performance Metrics")
        
        if self.load_data():
            metrics = self.demand_analyzer.calculate_key_metrics()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    label="Fulfillment Rate",
                    value=f"{metrics['overall_fulfillment_rate']:.1%}",
                    delta=f"{metrics['overall_fulfillment_rate'] - 0.85:.1%}",
                    delta_color="normal"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    label="Avg Delivery Time",
                    value=f"{metrics['avg_delivery_time']:.1f} min",
                    delta=f"{metrics['avg_delivery_time'] - 12:.1f} min",
                    delta_color="inverse"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    label="Out-of-Stock Rate",
                    value=f"{metrics['out_of_stock_rate']:.1%}",
                    delta=f"{metrics['out_of_stock_rate'] - 0.10:.1%}",
                    delta_color="inverse"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    label="Customer Satisfaction",
                    value=f"{metrics['avg_csat_score']:.1f}/5",
                    delta=f"{metrics['avg_csat_score'] - 4.2:.1f}",
                    delta_color="normal"
                )
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Solution overview
        st.markdown("### 🎯 Optimization Strategy")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 📊 Demand Analysis
            - Hourly demand pattern analysis
            - Peak hour identification
            - Category-wise demand forecasting
            - Bottleneck identification
            """)
        
        with col2:
            st.markdown("""
            #### 📦 Inventory Optimization
            - ML-based demand forecasting
            - Optimal stock level calculations
            - Dynamic restocking schedules
            - Cost optimization algorithms
            """)
        
        with col3:
            st.markdown("""
            #### 🗺️ Delivery Zone Mapping
            - Traffic pattern analysis
            - Dynamic zone adjustments
            - Route optimization
            - Coverage area maximization
            """)
    
    def render_demand_analysis(self):
        """Render the demand analysis page."""
        st.markdown('<h1 class="main-header">📊 Demand Analysis</h1>', unsafe_allow_html=True)
        
        if not self.load_data():
            st.error("Failed to load data. Please check your data files.")
            return
        
        # Get analysis results
        analysis = self.demand_analyzer.analyze_demand_patterns()
        insights = self.demand_analyzer.generate_insights()
        
        # Key insights
        st.markdown("### 💡 Key Insights")
        for insight in insights[:3]:
            st.markdown(f"""
            <div class="insight-box">
                <strong>[{insight['type']}] {insight['category']}:</strong> {insight['insight']}<br>
                <em>Recommendation:</em> {insight['recommendation']}
            </div>
            """, unsafe_allow_html=True)
        
        # Demand heatmap
        st.markdown("### 🔥 Demand Patterns Heatmap")
        
        # Prepare heatmap data
        sample_data = self.demand_analyzer.sample_data
        heatmap_data = sample_data.groupby(['hour', 'category'])['demand_quantity'].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='category', columns='hour', values='demand_quantity')
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='RdYlBu_r',
            hovertemplate='<b>%{y}</b><br>Hour: %{x}<br>Demand: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Hourly Demand Patterns by Product Category",
            xaxis_title="Hour of Day",
            yaxis_title="Product Category",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Peak hours analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⏰ Peak Hours Analysis")
            peak_hours = analysis['peak_hours']
            
            fig = go.Figure(data=[
                go.Bar(x=peak_hours.index, y=peak_hours.values, 
                      marker_color='#FF6B35')
            ])
            fig.update_layout(
                title="Peak Demand Hours",
                xaxis_title="Hour of Day",
                yaxis_title="Total Demand",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📦 Category Performance")
            category_analysis = analysis['category_analysis']
            
            fig = go.Figure(data=[
                go.Bar(x=category_analysis.index, y=category_analysis['demand_quantity_sum'],
                      marker_color='#047BD2')
            ])
            fig.update_layout(
                title="Total Demand by Category",
                xaxis_title="Category",
                yaxis_title="Total Demand",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed metrics table
        st.markdown("### 📋 Detailed Performance Metrics")
        st.dataframe(analysis['category_analysis'], use_container_width=True)
    
    def render_inventory_optimization(self):
        """Render the inventory optimization page."""
        st.markdown('<h1 class="main-header">📦 Inventory Optimization</h1>', unsafe_allow_html=True)
        
        if not self.load_data():
            st.error("Failed to load data. Please check your data files.")
            return
        
        # Train models and get optimization results
        with st.spinner("Training demand forecasting models..."):
            model_performance = self.inventory_optimizer.train_demand_forecasting_models()
        
        with st.spinner("Generating optimization recommendations..."):
            forecasts = self.inventory_optimizer.forecast_demand(24)
            optimal_levels = self.inventory_optimizer.calculate_optimal_stock_levels()
            restocking_schedule = self.inventory_optimizer.generate_restocking_schedule()
            cost_analysis = self.inventory_optimizer.calculate_inventory_costs()
        
        # Model performance
        st.markdown("### 🤖 Forecasting Model Performance")
        
        col1, col2, col3 = st.columns(3)
        
        for i, (category, perf) in enumerate(model_performance.items()):
            col = [col1, col2, col3][i % 3]
            with col:
                st.metric(
                    label=f"{category} MAPE",
                    value=f"{perf['MAPE']:.1f}%",
                    delta=f"{perf['MAPE'] - 15:.1f}%",
                    delta_color="inverse"
                )
        
        # Cost analysis
        st.markdown("### 💰 Inventory Cost Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Daily Holding Cost",
                value=f"${cost_analysis['total_holding_cost_daily']:.2f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Daily Stockout Cost",
                value=f"${cost_analysis['total_stockout_cost_daily']:.2f}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Total Daily Cost",
                value=f"${cost_analysis['total_inventory_cost_daily']:.2f}",
                delta=None
            )
        
        # Demand forecasts visualization
        st.markdown("### 📈 24-Hour Demand Forecast")
        
        forecast_summary = forecasts.groupby(['hour', 'category'])['predicted_demand'].sum().reset_index()
        
        fig = px.line(forecast_summary, x='hour', y='predicted_demand', color='category',
                     title="Predicted Demand for Next 24 Hours")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Restocking priorities
        st.markdown("### 🚨 Restocking Priorities")
        
        urgent_items = restocking_schedule[restocking_schedule['urgency'].isin(['Critical', 'High'])]
        
        if len(urgent_items) > 0:
            st.warning(f"⚠️ {len(urgent_items)} items need urgent restocking!")
            st.dataframe(urgent_items[['product_name', 'dark_store_id', 'urgency', 
                                     'current_stock', 'projected_stock_24h', 'suggested_order_qty']], 
                        use_container_width=True)
        else:
            st.success("✅ No urgent restocking needed!")
        
        # Optimal stock levels
        st.markdown("### 📊 Optimal Stock Levels")
        st.dataframe(optimal_levels, use_container_width=True)
    
    def render_delivery_zones(self):
        """Render the delivery zone mapping page."""
        st.markdown('<h1 class="main-header">🗺️ Delivery Zone Mapping</h1>', unsafe_allow_html=True)
        
        if not self.load_data():
            st.error("Failed to load data. Please check your data files.")
            return
        
        # Get zone mapping results
        with st.spinner("Analyzing delivery zones..."):
            zone_report = self.zone_mapper.create_zone_mapping_report()
        
        delivery_zones = zone_report['delivery_zones']
        performance_analysis = zone_report['performance_analysis']
        traffic_patterns = zone_report['traffic_patterns']
        recommendations = zone_report['recommendations']
        
        # Zone statistics
        st.markdown("### 📊 Delivery Zone Statistics")
        
        avg_radius = np.mean([zone['avg_radius'] for zone in delivery_zones.values()])
        total_coverage = sum([zone['avg_coverage'] for zone in delivery_zones.values()])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Average Delivery Radius",
                value=f"{avg_radius:.2f} km",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Coverage Area",
                value=f"{total_coverage:.1f} km²",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Number of Dark Stores",
                value=f"{len(delivery_zones)}",
                delta=None
            )
        
        # Traffic patterns
        st.markdown("### 🚦 Traffic Pattern Analysis")
        
        hourly_traffic = traffic_patterns['hourly_analysis']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_traffic['hour'],
            y=hourly_traffic['avg_delivery_time'],
            mode='lines+markers',
            name='Average Delivery Time',
            line=dict(color='#FF6B35', width=3)
        ))
        
        fig.add_hline(y=15, line_dash="dash", line_color="red", 
                     annotation_text="Target: 15 min")
        
        fig.update_layout(
            title="Average Delivery Time by Hour",
            xaxis_title="Hour of Day",
            yaxis_title="Delivery Time (minutes)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Peak traffic hours
        peak_hours = traffic_patterns['peak_traffic_hours']
        if peak_hours:
            st.warning(f"🚦 Peak traffic hours: {', '.join(map(str, peak_hours))}")
        
        # Zone recommendations
        st.markdown("### 💡 Zone Optimization Recommendations")
        
        zone_adjustments = recommendations['zone_adjustments']
        if zone_adjustments:
            for adj in zone_adjustments:
                priority_color = {"High": "error", "Medium": "warning", "Low": "info"}
                st_func = getattr(st, priority_color.get(adj['priority'], 'info'))
                st_func(f"""
                **{adj['store_name']} ({adj['store_id']})**  
                {adj['recommended_action']}  
                Reason: {adj['reason']}
                """)
        
        # Store performance comparison
        st.markdown("### 🏪 Store Performance Comparison")
        
        store_perf = performance_analysis.groupby('dark_store_id').agg({
            'delivery_time_minutes_mean': 'mean',
            'success_rate': 'mean'
        }).round(2)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=store_perf['delivery_time_minutes_mean'],
            y=store_perf['success_rate'],
            mode='markers+text',
            text=store_perf.index,
            textposition="top center",
            marker=dict(size=15, color='#047BD2'),
            name='Stores'
        ))
        
        fig.update_layout(
            title="Store Performance: Delivery Time vs Success Rate",
            xaxis_title="Average Delivery Time (minutes)",
            yaxis_title="Success Rate",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_impact_analysis(self):
        """Render the impact analysis page."""
        st.markdown('<h1 class="main-header">📈 Impact Analysis</h1>', unsafe_allow_html=True)
        
        # Current vs Target metrics
        st.markdown("### 🎯 Current vs Target Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Current Metrics")
            current_metrics = {
                "Out-of-Stock Rate": "25%",
                "Average Delivery Time": "18 minutes",
                "Cancellation Rate": "15%",
                "Customer Satisfaction": "3.2/5"
            }
            
            for metric, value in current_metrics.items():
                st.metric(label=metric, value=value)
        
        with col2:
            st.markdown("#### Target Metrics")
            target_metrics = {
                "Out-of-Stock Rate": "10%",
                "Average Delivery Time": "12 minutes",
                "Cancellation Rate": "5%",
                "Customer Satisfaction": "4.2/5"
            }
            
            for metric, value in target_metrics.items():
                st.metric(label=metric, value=value)
        
        # Projected impact
        st.markdown("### 🚀 Projected Business Impact")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### Revenue Impact
            - **15% increase** in order fulfillment
            - **20% reduction** in cancellations
            - **₹2.5M monthly** additional revenue
            """)
        
        with col2:
            st.markdown("""
            #### Operational Efficiency
            - **30% reduction** in stockouts
            - **25% improvement** in delivery time
            - **40% reduction** in inventory costs
            """)
        
        with col3:
            st.markdown("""
            #### Customer Experience
            - **31% improvement** in CSAT scores
            - **50% reduction** in complaints
            - **25% increase** in repeat orders
            """)
        
        # Implementation timeline
        st.markdown("### 📅 Implementation Timeline")
        
        timeline_data = [
            {"Phase": "Phase 1 (Weeks 1-4)", "Focus": "Demand Analysis & Quick Wins", "Impact": "10% improvement"},
            {"Phase": "Phase 2 (Weeks 5-8)", "Focus": "Inventory Optimization", "Impact": "20% improvement"},
            {"Phase": "Phase 3 (Weeks 9-12)", "Focus": "Zone Optimization & Scaling", "Impact": "30% improvement"}
        ]
        
        st.table(pd.DataFrame(timeline_data))
        
        # ROI calculation
        st.markdown("### 💰 Return on Investment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### Investment Required
            - Technology Infrastructure: ₹50L
            - Implementation Team: ₹30L
            - Training & Change Management: ₹20L
            - **Total Investment: ₹1Cr**
            """)
        
        with col2:
            st.markdown("""
            #### Expected Returns (Annual)
            - Increased Revenue: ₹30Cr
            - Cost Savings: ₹15Cr
            - **Total Returns: ₹45Cr**
            - **ROI: 450%**
            """)

def main():
    """Main function to run the Streamlit dashboard."""
    
    # Initialize dashboard
    dashboard = FlipkartDashboard()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Homepage", "📊 Demand Analysis", "📦 Inventory Optimization", 
         "🗺️ Delivery Zones", "📈 Impact Analysis"]
    )
    
    # Add some spacing
    st.sidebar.markdown("---")
    
    # Project info
    st.sidebar.markdown("""
    ### 📋 Project Info
    **Created by:** Hemant Kamble  
    **Date:** August 2024  
    **Purpose:** Flipkart Minutes Optimization
    """)
    
    # Page routing
    if page == "🏠 Homepage":
        dashboard.render_homepage()
    elif page == "📊 Demand Analysis":
        dashboard.render_demand_analysis()
    elif page == "📦 Inventory Optimization":
        dashboard.render_inventory_optimization()
    elif page == "🗺️ Delivery Zones":
        dashboard.render_delivery_zones()
    elif page == "📈 Impact Analysis":
        dashboard.render_impact_analysis()
    
    # Footer
    st.markdown("---")
    st.markdown("*This dashboard provides comprehensive insights for optimizing Flipkart's 10-15 minute delivery service.*")

if __name__ == "__main__":
    main()

