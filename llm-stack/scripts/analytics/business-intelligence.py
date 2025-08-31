#!/usr/bin/env python3
"""
Business Intelligence Dashboard for LLM Stack
Provides executive insights, KPIs, and strategic recommendations.

Usage:
    python business-intelligence.py [--analytics-dir analytics-output/] [--port 5002]
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BusinessIntelligence:
    def __init__(self, analytics_dir: str = "analytics-output"):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_data = {}
        self.bi_metrics = {}
        
        logger.info(f"Initialized Business Intelligence with analytics directory: {analytics_dir}")
    
    def load_analytics_data(self) -> bool:
        """Load analytics data for BI processing"""
        try:
            # Load analytics report
            report_file = self.analytics_dir / "analytics-report.json"
            if report_file.exists():
                with open(report_file, 'r') as f:
                    self.analytics_data = json.load(f)
                logger.info("Loaded analytics data for BI processing")
                return True
            else:
                logger.error("Analytics report not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load analytics data: {e}")
            return False
    
    def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate Key Performance Indicators"""
        logger.info("Calculating KPIs...")
        
        if not self.analytics_data:
            return {}
        
        kpis = {
            "data_volume": {},
            "data_quality": {},
            "content_richness": {},
            "operational_efficiency": {},
            "strategic_insights": {}
        }
        
        # Data Volume KPIs
        total_docs = self.analytics_data.get("summary", {}).get("total_documents", 0)
        kpis["data_volume"] = {
            "total_documents": total_docs,
            "documents_per_source": self.analytics_data.get("analytics", {}).get("data_sources", {}),
            "documents_per_type": self.analytics_data.get("analytics", {}).get("document_types", {}),
            "growth_rate": self._calculate_growth_rate()
        }
        
        # Data Quality KPIs
        quality_metrics = self.analytics_data.get("analytics", {}).get("quality_metrics", {})
        kpis["data_quality"] = {
            "overall_score": self._calculate_overall_quality_score(quality_metrics),
            "completeness": quality_metrics.get("completeness", 0),
            "consistency": quality_metrics.get("consistency", 0),
            "richness": quality_metrics.get("richness", 0),
            "data_health_index": self._calculate_data_health_index(quality_metrics)
        }
        
        # Content Richness KPIs
        content_analysis = self.analytics_data.get("analytics", {}).get("content_analysis", {})
        kpis["content_richness"] = {
            "average_content_length": content_analysis.get("avg_length", 0),
            "content_diversity": self._calculate_content_diversity(),
            "tag_coverage": self._calculate_tag_coverage(),
            "metadata_completeness": self._calculate_metadata_completeness()
        }
        
        # Operational Efficiency KPIs
        kpis["operational_efficiency"] = {
            "processing_efficiency": self._calculate_processing_efficiency(),
            "storage_optimization": self._calculate_storage_optimization(),
            "search_performance": self._calculate_search_performance()
        }
        
        # Strategic Insights
        kpis["strategic_insights"] = {
            "data_maturity_level": self._assess_data_maturity(),
            "improvement_opportunities": self._identify_improvement_opportunities(),
            "roi_metrics": self._calculate_roi_metrics()
        }
        
        self.bi_metrics = kpis
        return kpis
    
    def _calculate_growth_rate(self) -> float:
        """Calculate data growth rate (placeholder for future implementation)"""
        # This would typically compare current vs previous period
        return 0.0  # Placeholder
    
    def _calculate_overall_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall data quality score"""
        if not quality_metrics:
            return 0.0
        
        weights = {"completeness": 0.4, "consistency": 0.35, "richness": 0.25}
        score = 0.0
        
        for metric, weight in weights.items():
            if metric in quality_metrics:
                score += quality_metrics[metric] * weight
        
        return round(score, 2)
    
    def _calculate_data_health_index(self, quality_metrics: Dict[str, Any]) -> str:
        """Calculate data health index"""
        overall_score = self._calculate_overall_quality_score(quality_metrics)
        
        if overall_score >= 90:
            return "Excellent"
        elif overall_score >= 80:
            return "Good"
        elif overall_score >= 70:
            return "Fair"
        elif overall_score >= 60:
            return "Poor"
        else:
            return "Critical"
    
    def _calculate_content_diversity(self) -> float:
        """Calculate content diversity score"""
        if not self.analytics_data:
            return 0.0
        
        # Analyze content variety and uniqueness
        content_lengths = self.analytics_data.get("analytics", {}).get("content_analysis", {})
        if not content_lengths:
            return 0.0
        
        # Simple diversity based on content length variance
        avg_length = content_lengths.get("avg_length", 0)
        if avg_length == 0:
            return 0.0
        
        # Normalize to 0-100 scale
        diversity_score = min(avg_length / 200, 1.0) * 100
        return round(diversity_score, 2)
    
    def _calculate_tag_coverage(self) -> float:
        """Calculate tag coverage percentage"""
        if not self.analytics_data:
            return 0.0
        
        tag_analysis = self.analytics_data.get("analytics", {}).get("tag_analysis", {})
        if not tag_analysis:
            return 0.0
        
        total_docs = self.analytics_data.get("summary", {}).get("total_documents", 1)
        total_tags = tag_analysis.get("total_tags", 0)
        
        coverage = (total_tags / total_docs) * 100
        return round(min(coverage, 100), 2)
    
    def _calculate_metadata_completeness(self) -> float:
        """Calculate metadata completeness percentage"""
        if not self.analytics_data:
            return 0.0
        
        # This would analyze metadata field completion
        # For now, return a placeholder based on quality metrics
        quality_metrics = self.analytics_data.get("analytics", {}).get("quality_metrics", {})
        return quality_metrics.get("completeness", 0)
    
    def _calculate_processing_efficiency(self) -> float:
        """Calculate processing efficiency score"""
        # Placeholder for processing efficiency metrics
        return 85.0  # Placeholder
    
    def _calculate_storage_optimization(self) -> float:
        """Calculate storage optimization score"""
        # Placeholder for storage optimization metrics
        return 78.0  # Placeholder
    
    def _calculate_search_performance(self) -> float:
        """Calculate search performance score"""
        # Placeholder for search performance metrics
        return 92.0  # Placeholder
    
    def _assess_data_maturity(self) -> str:
        """Assess overall data maturity level"""
        overall_score = self.bi_metrics.get("data_quality", {}).get("overall_score", 0)
        
        if overall_score >= 90:
            return "Advanced"
        elif overall_score >= 80:
            return "Mature"
        elif overall_score >= 70:
            return "Developing"
        elif overall_score >= 60:
            return "Basic"
        else:
            return "Initial"
    
    def _identify_improvement_opportunities(self) -> List[str]:
        """Identify key improvement opportunities"""
        opportunities = []
        
        quality_metrics = self.bi_metrics.get("data_quality", {})
        
        if quality_metrics.get("completeness", 100) < 90:
            opportunities.append("Improve data completeness through better extraction processes")
        
        if quality_metrics.get("consistency", 100) < 95:
            opportunities.append("Enhance data consistency with standardized formats")
        
        if quality_metrics.get("richness", 100) < 80:
            opportunities.append("Enrich content with additional metadata and tags")
        
        content_richness = self.bi_metrics.get("content_richness", {})
        if content_richness.get("tag_coverage", 100) < 2:
            opportunities.append("Increase tagging coverage for better content organization")
        
        if not opportunities:
            opportunities.append("Data quality is excellent! Focus on advanced analytics features.")
        
        return opportunities
    
    def _calculate_roi_metrics(self) -> Dict[str, Any]:
        """Calculate ROI and business value metrics"""
        # Placeholder for ROI calculations
        return {
            "data_quality_roi": "High",
            "search_efficiency_gain": "25%",
            "content_discovery_improvement": "40%",
            "operational_cost_reduction": "15%"
        }
    
    def create_executive_dashboard(self) -> go.Figure:
        """Create executive-level dashboard"""
        logger.info("Creating executive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Data Quality Overview', 'Content Distribution',
                          'Operational KPIs', 'Strategic Insights',
                          'Quality Metrics Trend', 'Improvement Roadmap'),
            specs=[[{"type": "indicator"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # 1. Data Quality Overview (Gauge Chart)
        overall_quality = self.bi_metrics.get("data_quality", {}).get("overall_score", 0)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=overall_quality,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Data Quality"},
                delta={'reference': 80},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
        
        # 2. Content Distribution (Pie Chart)
        if self.bi_metrics.get("data_volume", {}).get("documents_per_type"):
            doc_types = self.bi_metrics["data_volume"]["documents_per_type"]
            types = list(doc_types.keys())
            counts = list(doc_types.values())
            fig.add_trace(
                go.Pie(labels=types, values=counts, name="Document Types"),
                row=1, col=2
            )
        
        # 3. Operational KPIs (Bar Chart)
        operational_kpis = self.bi_metrics.get("operational_efficiency", {})
        if operational_kpis:
            kpi_names = list(operational_kpis.keys())
            kpi_values = list(operational_kpis.values())
            fig.add_trace(
                go.Bar(x=kpi_names, y=kpi_values, name="Operational KPIs", marker_color='skyblue'),
                row=2, col=1
            )
        
        # 4. Strategic Insights (Bar Chart)
        strategic_insights = self.bi_metrics.get("strategic_insights", {})
        if strategic_insights:
            insight_names = list(strategic_insights.keys())
            insight_values = [1 if v else 0 for v in strategic_insights.values()]  # Binary for now
            fig.add_trace(
                go.Bar(x=insight_names, y=insight_values, name="Strategic Insights", marker_color='gold'),
                row=2, col=2
            )
        
        # 5. Quality Metrics Trend (Bar Chart)
        quality_metrics = self.bi_metrics.get("data_quality", {})
        if quality_metrics:
            metric_names = ['Completeness', 'Consistency', 'Richness']
            metric_values = [
                quality_metrics.get("completeness", 0),
                quality_metrics.get("consistency", 0),
                quality_metrics.get("richness", 0)
            ]
            fig.add_trace(
                go.Bar(x=metric_names, y=metric_values, name="Quality Metrics", 
                      marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1']),
                row=3, col=1
            )
        
        # 6. Improvement Roadmap (Scatter Plot)
        # Placeholder for improvement roadmap visualization
        fig.add_trace(
            go.Scatter(x=[1, 2, 3, 4], y=[60, 75, 85, 95], mode='lines+markers',
                      name="Quality Improvement", line=dict(color='red', width=3)),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="LLM Stack Business Intelligence Dashboard",
            showlegend=False,
            height=1000,
            template="plotly_white"
        )
        
        return fig
    
    def generate_bi_report(self) -> Dict[str, Any]:
        """Generate comprehensive BI report"""
        logger.info("Generating BI report...")
        
        if not self.bi_metrics:
            self.calculate_kpis()
        
        report = {
            "executive_summary": {
                "overall_quality_score": self.bi_metrics.get("data_quality", {}).get("overall_score", 0),
                "data_maturity_level": self.bi_metrics.get("strategic_insights", {}).get("data_maturity_level", "Unknown"),
                "total_documents": self.bi_metrics.get("data_volume", {}).get("total_documents", 0),
                "data_health_status": self.bi_metrics.get("data_quality", {}).get("data_health_index", "Unknown")
            },
            "kpi_analysis": self.bi_metrics,
            "strategic_recommendations": self._generate_strategic_recommendations(),
            "action_items": self._generate_action_items(),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report
    
    def _generate_strategic_recommendations(self) -> List[Dict[str, Any]]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Data Quality Recommendations
        quality_score = self.bi_metrics.get("data_quality", {}).get("overall_score", 0)
        if quality_score < 80:
            recommendations.append({
                "category": "Data Quality",
                "priority": "High",
                "recommendation": "Implement comprehensive data quality monitoring and improvement processes",
                "expected_impact": "20-30% improvement in data reliability",
                "timeline": "3-6 months"
            })
        
        # Content Enrichment Recommendations
        tag_coverage = self.bi_metrics.get("content_richness", {}).get("tag_coverage", 0)
        if tag_coverage < 2:
            recommendations.append({
                "category": "Content Management",
                "priority": "Medium",
                "recommendation": "Develop automated tagging and classification systems",
                "expected_impact": "Improved content discoverability and organization",
                "timeline": "2-4 months"
            })
        
        # Operational Efficiency Recommendations
        processing_efficiency = self.bi_metrics.get("operational_efficiency", {}).get("processing_efficiency", 0)
        if processing_efficiency < 90:
            recommendations.append({
                "category": "Operations",
                "priority": "Medium",
                "recommendation": "Optimize data processing pipelines and workflows",
                "expected_impact": "15-25% improvement in processing speed",
                "timeline": "1-3 months"
            })
        
        if not recommendations:
            recommendations.append({
                "category": "Innovation",
                "priority": "Low",
                "recommendation": "Explore advanced analytics and AI-powered insights",
                "expected_impact": "Enhanced decision-making capabilities",
                "timeline": "6-12 months"
            })
        
        return recommendations
    
    def _generate_action_items(self) -> List[Dict[str, Any]]:
        """Generate actionable items"""
        action_items = []
        
        # Immediate actions (next 30 days)
        action_items.append({
            "timeline": "Immediate (30 days)",
            "actions": [
                "Review and validate current data quality metrics",
                "Identify critical data quality issues",
                "Establish baseline performance metrics"
            ]
        })
        
        # Short-term actions (1-3 months)
        action_items.append({
            "timeline": "Short-term (1-3 months)",
            "actions": [
                "Implement data quality monitoring dashboards",
                "Develop data enrichment processes",
                "Create user training materials"
            ]
        })
        
        # Long-term actions (3-12 months)
        action_items.append({
            "timeline": "Long-term (3-12 months)",
            "actions": [
                "Deploy advanced analytics capabilities",
                "Integrate with business intelligence tools",
                "Establish data governance framework"
            ]
        })
        
        return action_items

def main():
    parser = argparse.ArgumentParser(description='LLM Stack Business Intelligence')
    parser.add_argument('--analytics-dir', default='analytics-output',
                       help='Analytics output directory')
    parser.add_argument('--output-dir', default='bi-output',
                       help='BI output directory')
    
    args = parser.parse_args()
    
    try:
        # Initialize BI engine
        bi = BusinessIntelligence(args.analytics_dir)
        
        # Load analytics data
        if not bi.load_analytics_data():
            print("❌ Failed to load analytics data")
            return 1
        
        # Calculate KPIs
        bi.calculate_kpis()
        
        # Generate report
        report = bi.generate_bi_report()
        
        # Save report
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / "bi-report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create dashboard
        dashboard = bi.create_executive_dashboard()
        dashboard_file = output_dir / "executive-dashboard.html"
        dashboard.write_html(str(dashboard_file))
        
        print("✅ Business Intelligence report generated successfully!")
        print(f"📊 Report: {report_file}")
        print(f"📈 Dashboard: {dashboard_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Business Intelligence failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
