#!/usr/bin/env python3
"""
Advanced Analytics Engine for LLM Stack
Provides comprehensive analytics, insights, and business intelligence from RAG index data.

Usage:
    python analytics-engine.py [--index-dir rag-index/] [--output-dir analytics-output/]
"""

import json
import jsonlines
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMStackAnalytics:
    def __init__(self, index_dir: str = "rag-index", output_dir: str = "analytics-output"):
        self.index_dir = Path(index_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data containers
        self.documents_df = None
        self.analytics_data = {}
        
        logger.info(f"Initialized analytics engine with index: {index_dir}")
    
    def load_rag_data(self) -> bool:
        """Load data from RAG index and JSONL files"""
        try:
            # Load index statistics
            stats_file = self.index_dir / "index-statistics.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    self.index_stats = json.load(f)
                logger.info("Loaded index statistics")
            else:
                logger.warning("Index statistics not found")
                self.index_stats = {}
            
            # Load original JSONL data if available
            jsonl_files = list(self.index_dir.parent.parent / "export" / "exports").glob("*.jsonl")
            if jsonl_files:
                latest_file = max(jsonl_files, key=lambda x: x.stat().st_mtime)
                logger.info(f"Loading data from: {latest_file}")
                
                documents = []
                with jsonlines.open(latest_file) as reader:
                    for obj in reader:
                        documents.append(obj)
                
                self.documents_df = pd.DataFrame(documents)
                logger.info(f"Loaded {len(self.documents_df)} documents for analysis")
                return True
            else:
                logger.warning("No JSONL export files found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load RAG data: {e}")
            return False
    
    def generate_basic_analytics(self) -> Dict[str, Any]:
        """Generate basic analytics and statistics"""
        logger.info("Generating basic analytics...")
        
        if self.documents_df is None or self.documents_df.empty:
            logger.warning("No data available for analysis")
            return {}
        
        analytics = {
            "total_documents": len(self.documents_df),
            "generated_at": datetime.utcnow().isoformat(),
            "data_sources": {},
            "document_types": {},
            "content_analysis": {},
            "temporal_analysis": {},
            "tag_analysis": {},
            "quality_metrics": {}
        }
        
        # Source analysis
        if 'source' in self.documents_df.columns:
            source_counts = self.documents_df['source'].value_counts().to_dict()
            analytics["data_sources"] = source_counts
        
        # Type analysis
        if 'type' in self.documents_df.columns:
            type_counts = self.documents_df['type'].value_counts().to_dict()
            analytics["document_types"] = type_counts
        
        # Content analysis
        if 'content' in self.documents_df.columns:
            content_lengths = self.documents_df['content'].str.len()
            analytics["content_analysis"] = {
                "avg_length": int(content_lengths.mean()),
                "min_length": int(content_lengths.min()),
                "max_length": int(content_lengths.max()),
                "total_characters": int(content_lengths.sum())
            }
        
        # Tag analysis
        if 'metadata' in self.documents_df.columns:
            all_tags = []
            for metadata in self.documents_df['metadata']:
                if isinstance(metadata, dict) and 'tags' in metadata:
                    tags = metadata['tags']
                    if isinstance(tags, list):
                        all_tags.extend(tags)
                    elif isinstance(tags, str):
                        all_tags.extend([t.strip() for t in tags.split(',')])
            
            if all_tags:
                tag_counts = Counter(all_tags)
                analytics["tag_analysis"] = {
                    "total_tags": len(all_tags),
                    "unique_tags": len(tag_counts),
                    "top_tags": dict(tag_counts.most_common(10))
                }
        
        # Quality metrics
        analytics["quality_metrics"] = {
            "completeness": self._calculate_completeness(),
            "consistency": self._calculate_consistency(),
            "richness": self._calculate_richness()
        }
        
        self.analytics_data = analytics
        return analytics
    
    def _calculate_completeness(self) -> float:
        """Calculate data completeness score"""
        if self.documents_df is None:
            return 0.0
        
        required_fields = ['id', 'title', 'content', 'source', 'type']
        total_fields = len(required_fields) * len(self.documents_df)
        filled_fields = sum(
            sum(1 for field in required_fields if pd.notna(self.documents_df[field].iloc[i]))
            for i in range(len(self.documents_df))
        )
        
        return round(filled_fields / total_fields * 100, 2) if total_fields > 0 else 0.0
    
    def _calculate_consistency(self) -> float:
        """Calculate data consistency score"""
        if self.documents_df is None:
            return 0.0
        
        # Check for consistent data types and formats
        consistency_score = 0.0
        checks = 0
        
        # Check ID format consistency
        if 'id' in self.documents_df.columns:
            id_consistency = self.documents_df['id'].apply(lambda x: isinstance(x, (str, int))).mean()
            consistency_score += id_consistency
            checks += 1
        
        # Check source consistency
        if 'source' in self.documents_df.columns:
            source_consistency = self.documents_df['source'].apply(lambda x: isinstance(x, str)).mean()
            consistency_score += source_consistency
            checks += 1
        
        # Check type consistency
        if 'type' in self.documents_df.columns:
            type_consistency = self.documents_df['type'].apply(lambda x: isinstance(x, str)).mean()
            consistency_score += type_consistency
            checks += 1
        
        return round(consistency_score / checks * 100, 2) if checks > 0 else 0.0
    
    def _calculate_richness(self) -> float:
        """Calculate data richness score"""
        if self.documents_df is None:
            return 0.0
        
        richness_score = 0.0
        checks = 0
        
        # Check content richness
        if 'content' in self.documents_df.columns:
            avg_content_length = self.documents_df['content'].str.len().mean()
            content_richness = min(avg_content_length / 100, 1.0)  # Normalize to 0-1
            richness_score += content_richness
            checks += 1
        
        # Check metadata richness
        if 'metadata' in self.documents_df.columns:
            metadata_richness = self.documents_df['metadata'].apply(
                lambda x: len(x) if isinstance(x, dict) else 0
            ).mean() / 5  # Normalize to 0-1 (assuming 5 is good)
            richness_score += metadata_richness
            checks += 1
        
        return round(richness_score / checks * 100, 2) if checks > 0 else 0.0
    
    def generate_advanced_insights(self) -> Dict[str, Any]:
        """Generate advanced insights and patterns"""
        logger.info("Generating advanced insights...")
        
        if self.documents_df is None or self.documents_df.empty:
            return {}
        
        insights = {
            "patterns": {},
            "trends": {},
            "anomalies": {},
            "recommendations": {}
        }
        
        # Pattern analysis
        insights["patterns"] = self._analyze_patterns()
        
        # Trend analysis
        insights["trends"] = self._analyze_trends()
        
        # Anomaly detection
        insights["anomalies"] = self._detect_anomalies()
        
        # Recommendations
        insights["recommendations"] = self._generate_recommendations()
        
        return insights
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the data"""
        patterns = {}
        
        # Source-type patterns
        if 'source' in self.documents_df.columns and 'type' in self.documents_df.columns:
            source_type_pattern = self.documents_df.groupby(['source', 'type']).size().unstack(fill_value=0)
            patterns["source_type_distribution"] = source_type_pattern.to_dict()
        
        # Content patterns
        if 'content' in self.documents_df.columns:
            # Word frequency analysis
            all_words = ' '.join(self.documents_df['content'].astype(str)).lower().split()
            word_freq = Counter(all_words)
            # Remove common stop words
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            filtered_words = {word: count for word, count in word_freq.items() 
                            if word not in stop_words and len(word) > 3}
            patterns["top_keywords"] = dict(Counter(filtered_words).most_common(20))
        
        return patterns
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze temporal trends"""
        trends = {}
        
        # Extract dates if available
        if 'extracted_at' in self.documents_df.columns:
            try:
                self.documents_df['date'] = pd.to_datetime(self.documents_df['extracted_at'])
                date_counts = self.documents_df['date'].dt.date.value_counts().sort_index()
                trends["daily_volume"] = date_counts.to_dict()
                
                # Weekly trends
                weekly_counts = self.documents_df.groupby(
                    self.documents_df['date'].dt.isocalendar().week
                ).size()
                trends["weekly_volume"] = weekly_counts.to_dict()
                
            except Exception as e:
                logger.warning(f"Date analysis failed: {e}")
        
        return trends
    
    def _detect_anomalies(self) -> Dict[str, Any]:
        """Detect anomalies in the data"""
        anomalies = {}
        
        # Content length anomalies
        if 'content' in self.documents_df.columns:
            content_lengths = self.documents_df['content'].str.len()
            Q1 = content_lengths.quantile(0.25)
            Q3 = content_lengths.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = content_lengths[(content_lengths < lower_bound) | (content_lengths > upper_bound)]
            if not outliers.empty:
                anomalies["content_length_outliers"] = {
                    "count": len(outliers),
                    "indices": outliers.index.tolist(),
                    "values": outliers.tolist()
                }
        
        # Missing data anomalies
        missing_data = self.documents_df.isnull().sum()
        if missing_data.sum() > 0:
            anomalies["missing_data"] = missing_data[missing_data > 0].to_dict()
        
        return anomalies
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data quality recommendations
        if self.analytics_data.get("quality_metrics"):
            completeness = self.analytics_data["quality_metrics"]["completeness"]
            if completeness < 90:
                recommendations.append(f"Improve data completeness (currently {completeness}%)")
            
            consistency = self.analytics_data["quality_metrics"]["consistency"]
            if consistency < 95:
                recommendations.append(f"Enhance data consistency (currently {consistency}%)")
        
        # Content recommendations
        if self.documents_df is not None and 'content' in self.documents_df.columns:
            avg_length = self.documents_df['content'].str.len().mean()
            if avg_length < 100:
                recommendations.append("Consider enriching document content for better searchability")
        
        # Tag recommendations
        if self.analytics_data.get("tag_analysis"):
            tag_coverage = self.analytics_data["tag_analysis"]["total_tags"] / len(self.documents_df)
            if tag_coverage < 2:
                recommendations.append("Increase tagging coverage for better content organization")
        
        if not recommendations:
            recommendations.append("Data quality is excellent! Consider advanced analytics features.")
        
        return recommendations
    
    def create_visualizations(self) -> bool:
        """Create comprehensive visualizations"""
        logger.info("Creating visualizations...")
        
        try:
            # Set style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # Create subplots
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle('LLM Stack Analytics Dashboard', fontsize=16, fontweight='bold')
            
            # 1. Source Distribution
            if self.analytics_data.get("data_sources"):
                sources = list(self.analytics_data["data_sources"].keys())
                counts = list(self.analytics_data["data_sources"].values())
                axes[0, 0].pie(counts, labels=sources, autopct='%1.1f%%', startangle=90)
                axes[0, 0].set_title('Data Source Distribution')
            
            # 2. Document Type Distribution
            if self.analytics_data.get("document_types"):
                types = list(self.analytics_data["document_types"].keys())
                type_counts = list(self.analytics_data["document_types"].values())
                axes[0, 1].bar(types, type_counts, color='skyblue')
                axes[0, 1].set_title('Document Type Distribution')
                axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. Content Length Distribution
            if self.documents_df is not None and 'content' in self.documents_df.columns:
                content_lengths = self.documents_df['content'].str.len()
                axes[0, 2].hist(content_lengths, bins=20, color='lightgreen', alpha=0.7)
                axes[0, 2].set_title('Content Length Distribution')
                axes[0, 2].set_xlabel('Content Length (characters)')
                axes[0, 2].set_ylabel('Frequency')
            
            # 4. Quality Metrics
            if self.analytics_data.get("quality_metrics"):
                metrics = ['Completeness', 'Consistency', 'Richness']
                values = [
                    self.analytics_data["quality_metrics"]["completeness"],
                    self.analytics_data["quality_metrics"]["consistency"],
                    self.analytics_data["quality_metrics"]["richness"]
                ]
                bars = axes[1, 0].bar(metrics, values, color=['#ff6b6b', '#4ecdc4', '#45b7d1'])
                axes[1, 0].set_title('Data Quality Metrics')
                axes[1, 0].set_ylabel('Score (%)')
                axes[1, 0].set_ylim(0, 100)
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 1,
                                   f'{value:.1f}%', ha='center', va='bottom')
            
            # 5. Top Tags
            if self.analytics_data.get("tag_analysis", {}).get("top_tags"):
                top_tags = dict(list(self.analytics_data["tag_analysis"]["top_tags"].items())[:10])
                tag_names = list(top_tags.keys())
                tag_counts = list(top_tags.values())
                axes[1, 1].barh(tag_names, tag_counts, color='gold')
                axes[1, 1].set_title('Top 10 Tags')
                axes[1, 1].set_xlabel('Count')
            
            # 6. Content Analysis
            if self.analytics_data.get("content_analysis"):
                content_stats = self.analytics_data["content_analysis"]
                stats_labels = ['Avg Length', 'Min Length', 'Max Length']
                stats_values = [content_stats["avg_length"], content_stats["min_length"], content_stats["max_length"]]
                axes[1, 2].bar(stats_labels, stats_values, color=['#ff9ff3', '#54a0ff', '#5f27cd'])
                axes[1, 2].set_title('Content Statistics')
                axes[1, 2].set_ylabel('Characters')
            
            plt.tight_layout()
            
            # Save visualization
            viz_file = self.output_dir / "analytics-dashboard.png"
            plt.savefig(viz_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Visualizations saved to: {viz_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create visualizations: {e}")
            return False
    
    def create_interactive_dashboard(self) -> bool:
        """Create an interactive Plotly dashboard"""
        logger.info("Creating interactive dashboard...")
        
        try:
            if self.documents_df is None or self.documents_df.empty:
                logger.warning("No data available for interactive dashboard")
                return False
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Data Source Distribution', 'Document Type Distribution',
                              'Content Length Analysis', 'Quality Metrics'),
                specs=[[{"type": "pie"}, {"type": "bar"}],
                       [{"type": "histogram"}, {"type": "bar"}]]
            )
            
            # 1. Source Distribution (Pie Chart)
            if self.analytics_data.get("data_sources"):
                sources = list(self.analytics_data["data_sources"].keys())
                counts = list(self.analytics_data["data_sources"].values())
                fig.add_trace(
                    go.Pie(labels=sources, values=counts, name="Sources"),
                    row=1, col=1
                )
            
            # 2. Document Type Distribution (Bar Chart)
            if self.analytics_data.get("document_types"):
                types = list(self.analytics_data["document_types"].keys())
                type_counts = list(self.analytics_data["document_types"].values())
                fig.add_trace(
                    go.Bar(x=types, y=type_counts, name="Types", marker_color='skyblue'),
                    row=1, col=2
                )
            
            # 3. Content Length Distribution (Histogram)
            if 'content' in self.documents_df.columns:
                content_lengths = self.documents_df['content'].str.len()
                fig.add_trace(
                    go.Histogram(x=content_lengths, name="Content Length", marker_color='lightgreen'),
                    row=2, col=1
                )
            
            # 4. Quality Metrics (Bar Chart)
            if self.analytics_data.get("quality_metrics"):
                metrics = ['Completeness', 'Consistency', 'Richness']
                values = [
                    self.analytics_data["quality_metrics"]["completeness"],
                    self.analytics_data["quality_metrics"]["consistency"],
                    self.analytics_data["quality_metrics"]["richness"]
                ]
                fig.add_trace(
                    go.Bar(x=metrics, y=values, name="Quality", marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1']),
                    row=2, col=2
                )
            
            # Update layout
            fig.update_layout(
                title_text="LLM Stack Analytics Dashboard",
                showlegend=False,
                height=800
            )
            
            # Save interactive dashboard
            dashboard_file = self.output_dir / "interactive-dashboard.html"
            fig.write_html(str(dashboard_file))
            
            logger.info(f"Interactive dashboard saved to: {dashboard_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create interactive dashboard: {e}")
            return False
    
    def generate_report(self) -> bool:
        """Generate comprehensive analytics report"""
        logger.info("Generating analytics report...")
        
        try:
            report = {
                "summary": {
                    "total_documents": self.analytics_data.get("total_documents", 0),
                    "data_sources": len(self.analytics_data.get("data_sources", {})),
                    "document_types": len(self.analytics_data.get("document_types", {})),
                    "analysis_date": datetime.utcnow().isoformat()
                },
                "analytics": self.analytics_data,
                "insights": self.generate_advanced_insights(),
                "recommendations": [],
                "files_generated": []
            }
            
            # Add recommendations
            if self.analytics_data.get("quality_metrics"):
                recommendations = self._generate_recommendations()
                report["recommendations"] = recommendations
            
            # List generated files
            generated_files = list(self.output_dir.glob("*"))
            report["files_generated"] = [str(f.name) for f in generated_files]
            
            # Save report
            report_file = self.output_dir / "analytics-report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Save summary report
            summary_file = self.output_dir / "analytics-summary.md"
            with open(summary_file, 'w') as f:
                f.write(self._generate_markdown_summary(report))
            
            logger.info(f"Analytics report saved to: {report_file}")
            logger.info(f"Summary report saved to: {summary_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return False
    
    def _generate_markdown_summary(self, report: Dict[str, Any]) -> str:
        """Generate markdown summary of analytics"""
        summary = f"""# LLM Stack Analytics Report

## 📊 Executive Summary
- **Total Documents**: {report['summary']['total_documents']}
- **Data Sources**: {report['summary']['data_sources']}
- **Document Types**: {report['summary']['document_types']}
- **Analysis Date**: {report['summary']['analysis_date']}

## 🔍 Key Insights

### Data Quality Metrics
"""
        
        if report['analytics'].get('quality_metrics'):
            metrics = report['analytics']['quality_metrics']
            summary += f"""
- **Completeness**: {metrics['completeness']}%
- **Consistency**: {metrics['consistency']}%
- **Richness**: {metrics['richness']}%
"""
        
        summary += f"""
### Data Distribution
"""
        
        if report['analytics'].get('data_sources'):
            summary += "\n**By Source:**\n"
            for source, count in report['analytics']['data_sources'].items():
                summary += f"- {source}: {count} documents\n"
        
        if report['analytics'].get('document_types'):
            summary += "\n**By Type:**\n"
            for doc_type, count in report['analytics']['document_types'].items():
                summary += f"- {doc_type}: {count} documents\n"
        
        summary += f"""
## 🚀 Recommendations
"""
        
        for rec in report.get('recommendations', []):
            summary += f"- {rec}\n"
        
        summary += f"""
## 📁 Generated Files
"""
        
        for file in report.get('files_generated', []):
            summary += f"- {file}\n"
        
        summary += f"""
---
*Report generated by LLM Stack Analytics Engine*
"""
        
        return summary
    
    def run_full_analysis(self) -> bool:
        """Run complete analytics pipeline"""
        logger.info("Starting full analytics pipeline...")
        
        try:
            # Load data
            if not self.load_rag_data():
                logger.error("Failed to load RAG data")
                return False
            
            # Generate basic analytics
            self.generate_basic_analytics()
            
            # Create visualizations
            self.create_visualizations()
            
            # Create interactive dashboard
            self.create_interactive_dashboard()
            
            # Generate report
            self.generate_report()
            
            logger.info("✅ Analytics pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Analytics pipeline failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='LLM Stack Analytics Engine')
    parser.add_argument('--index-dir', default='rag-index',
                       help='RAG index directory')
    parser.add_argument('--output-dir', default='analytics-output',
                       help='Output directory for analytics')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick analysis only')
    
    args = parser.parse_args()
    
    try:
        # Initialize analytics engine
        analytics = LLMStackAnalytics(args.index_dir, args.output_dir)
        
        if args.quick:
            # Quick analysis
            if analytics.load_rag_data():
                analytics.generate_basic_analytics()
                analytics.generate_report()
                print("✅ Quick analysis completed!")
            else:
                print("❌ Quick analysis failed!")
                return 1
        else:
            # Full analysis
            success = analytics.run_full_analysis()
            if success:
                print("✅ Full analytics pipeline completed!")
                return 0
            else:
                print("❌ Full analytics pipeline failed!")
                return 1
                
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
