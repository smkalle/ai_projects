"""
Extraction Logger and Progress Tracking
Provides detailed logging and progress tracking for Dolphin's staged extraction process
"""

import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import threading
from queue import Queue
from enum import Enum
import colorama
from colorama import Fore, Back, Style
from tabulate import tabulate

colorama.init(autoreset=True)

class ExtractionStage(Enum):
    """Stages in the Dolphin extraction pipeline"""
    INITIALIZED = "initialized"
    LOADING = "loading"
    ANALYZING = "analyzing"
    PARSING = "parsing"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ExtractionEvent:
    """Event in the extraction process"""
    timestamp: str
    stage: str
    event_type: str  # info, warning, error, success
    message: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class StageMetrics:
    """Metrics for each processing stage"""
    stage_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    items_processed: int = 0
    items_failed: int = 0
    confidence_scores: List[float] = None
    
    def finalize(self):
        """Calculate final metrics"""
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        if self.confidence_scores:
            self.avg_confidence = sum(self.confidence_scores) / len(self.confidence_scores)
        else:
            self.avg_confidence = 0.0

class ExtractionLogger:
    """
    Comprehensive logger for Dolphin extraction process
    Tracks progress, events, and metrics for each stage
    """
    
    def __init__(self, 
                 log_dir: str = "./logs",
                 console_output: bool = True,
                 save_to_file: bool = True):
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.console_output = console_output
        self.save_to_file = save_to_file
        
        # Session info
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"extraction_{self.session_id}.json"
        
        # Current state
        self.current_stage = ExtractionStage.INITIALIZED
        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        
        # Events and metrics
        self.events: List[ExtractionEvent] = []
        self.stage_metrics: Dict[str, StageMetrics] = {}
        self.file_results: Dict[str, Any] = {}
        
        # Progress tracking
        self.progress_queue = Queue()
        self.progress_thread = None
        self.stop_progress = False
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure Python logging"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Console handler with color
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # File handler
        file_handler = logging.FileHandler(
            self.log_dir / f"extraction_{self.session_id}.log"
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure logger
        logger = logging.getLogger('dolphin_extraction')
        logger.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        self.logger = logger
    
    def start_extraction(self, file_path: str, total_pages: int = 1):
        """Start extraction for a new file"""
        self.current_file = file_path
        self.total_pages = total_pages
        self.current_page = 0
        
        self.log_event(
            ExtractionStage.INITIALIZED,
            "info",
            f"Starting extraction for: {Path(file_path).name}",
            {"file_path": file_path, "total_pages": total_pages}
        )
        
        if self.console_output:
            self._print_header(file_path)
    
    def log_event(self, 
                  stage: ExtractionStage,
                  event_type: str,
                  message: str,
                  details: Optional[Dict] = None):
        """Log an extraction event"""
        
        event = ExtractionEvent(
            timestamp=datetime.now().isoformat(),
            stage=stage.value,
            event_type=event_type,
            message=message,
            details=details
        )
        
        self.events.append(event)
        
        # Console output with colors
        if self.console_output:
            self._print_event(event)
        
        # Log to file
        if self.save_to_file:
            self._save_event(event)
        
        # Update current stage
        self.current_stage = stage
    
    def start_stage(self, stage_name: str):
        """Start tracking a processing stage"""
        self.stage_metrics[stage_name] = StageMetrics(
            stage_name=stage_name,
            start_time=time.time(),
            confidence_scores=[]
        )
        
        self.log_event(
            ExtractionStage[stage_name.upper()],
            "info",
            f"Starting {stage_name} stage"
        )
    
    def end_stage(self, stage_name: str, success: bool = True):
        """End tracking a processing stage"""
        if stage_name in self.stage_metrics:
            metrics = self.stage_metrics[stage_name]
            metrics.end_time = time.time()
            metrics.finalize()
            
            status = "success" if success else "error"
            self.log_event(
                ExtractionStage[stage_name.upper()],
                status,
                f"Completed {stage_name} stage",
                {
                    "duration": f"{metrics.duration:.2f}s",
                    "items_processed": metrics.items_processed,
                    "items_failed": metrics.items_failed
                }
            )
    
    def log_analysis_progress(self, 
                            page_num: int,
                            anchors_found: int,
                            confidence: float):
        """Log progress during analysis stage"""
        self.current_page = page_num
        
        if "analyzing" in self.stage_metrics:
            metrics = self.stage_metrics["analyzing"]
            metrics.items_processed += 1
            metrics.confidence_scores.append(confidence)
        
        self.log_event(
            ExtractionStage.ANALYZING,
            "info",
            f"Analyzed page {page_num}/{self.total_pages}",
            {
                "anchors_found": anchors_found,
                "confidence": f"{confidence:.2%}"
            }
        )
        
        if self.console_output:
            self._show_progress_bar(page_num, self.total_pages, "Analyzing")
    
    def log_parsing_progress(self,
                           anchor_type: str,
                           anchor_num: int,
                           total_anchors: int,
                           success: bool = True):
        """Log progress during parsing stage"""
        
        if "parsing" in self.stage_metrics:
            metrics = self.stage_metrics["parsing"]
            metrics.items_processed += 1
            if not success:
                metrics.items_failed += 1
        
        status = "success" if success else "warning"
        self.log_event(
            ExtractionStage.PARSING,
            status,
            f"Parsed {anchor_type} anchor {anchor_num}/{total_anchors}",
            {"anchor_type": anchor_type, "success": success}
        )
        
        if self.console_output:
            self._show_progress_bar(anchor_num, total_anchors, "Parsing")
    
    def log_extraction_result(self, 
                            file_path: str,
                            success: bool,
                            extracted_data: Dict[str, Any],
                            total_time: float):
        """Log final extraction results"""
        
        self.file_results[file_path] = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "total_time": total_time,
            "pages_processed": self.current_page,
            "data_extracted": len(extracted_data),
            "summary": self._generate_summary(extracted_data)
        }
        
        status = ExtractionStage.COMPLETED if success else ExtractionStage.FAILED
        event_type = "success" if success else "error"
        
        self.log_event(
            status,
            event_type,
            f"Extraction {'completed' if success else 'failed'} for {Path(file_path).name}",
            {
                "total_time": f"{total_time:.2f}s",
                "pages": self.current_page,
                "data_points": len(extracted_data)
            }
        )
        
        if self.console_output:
            self._print_summary(file_path, success, total_time)
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Generate summary statistics from extracted data"""
        summary = {
            "patient_records": 0,
            "medications": 0,
            "lab_results": 0,
            "diagnoses": 0,
            "clinical_notes": 0
        }
        
        if "aggregated_data" in data:
            agg = data["aggregated_data"]
            summary["patient_records"] = 1 if agg.get("patient_info") else 0
            summary["medications"] = len(agg.get("medications", []))
            summary["lab_results"] = len(agg.get("lab_results", []))
            summary["diagnoses"] = len(agg.get("diagnoses", []))
            summary["clinical_notes"] = len(agg.get("clinical_notes", []))
        
        return summary
    
    def _print_header(self, file_path: str):
        """Print extraction header"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}DOLPHIN EXTRACTION PIPELINE")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}File: {Fore.YELLOW}{Path(file_path).name}")
        print(f"{Fore.WHITE}Session: {Fore.GREEN}{self.session_id}")
        print(f"{Fore.CYAN}{'='*60}\n")
    
    def _print_event(self, event: ExtractionEvent):
        """Print colored event to console"""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED
        }
        
        color = colors.get(event.event_type, Fore.WHITE)
        timestamp = datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S")
        
        print(f"{Fore.WHITE}[{timestamp}] {color}[{event.stage.upper()}] {event.message}")
        
        if event.details:
            for key, value in event.details.items():
                print(f"  {Fore.WHITE}└─ {key}: {Fore.YELLOW}{value}")
    
    def _show_progress_bar(self, current: int, total: int, stage: str):
        """Display progress bar"""
        if total == 0:
            return
            
        percent = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\r{Fore.CYAN}{stage}: {Fore.GREEN}[{bar}] {percent:.1f}% ({current}/{total})", end='')
        
        if current == total:
            print()  # New line when complete
    
    def _print_summary(self, file_path: str, success: bool, total_time: float):
        """Print extraction summary"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}EXTRACTION SUMMARY")
        print(f"{Fore.CYAN}{'='*60}")
        
        status_color = Fore.GREEN if success else Fore.RED
        status_text = "SUCCESS" if success else "FAILED"
        
        print(f"{Fore.WHITE}Status: {status_color}{status_text}")
        print(f"{Fore.WHITE}Total Time: {Fore.YELLOW}{total_time:.2f} seconds")
        print(f"{Fore.WHITE}Pages Processed: {Fore.YELLOW}{self.current_page}")
        
        # Stage metrics table
        if self.stage_metrics:
            print(f"\n{Fore.CYAN}Stage Metrics:")
            
            table_data = []
            for stage_name, metrics in self.stage_metrics.items():
                if metrics.duration:
                    table_data.append([
                        stage_name.capitalize(),
                        f"{metrics.duration:.2f}s",
                        metrics.items_processed,
                        metrics.items_failed,
                        f"{getattr(metrics, 'avg_confidence', 0):.2%}"
                    ])
            
            if table_data:
                headers = ["Stage", "Duration", "Processed", "Failed", "Avg Confidence"]
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Results summary
        if file_path in self.file_results:
            summary = self.file_results[file_path].get("summary", {})
            if summary:
                print(f"\n{Fore.CYAN}Extracted Data:")
                for key, value in summary.items():
                    if value > 0:
                        print(f"  {Fore.WHITE}• {key.replace('_', ' ').title()}: {Fore.YELLOW}{value}")
        
        print(f"{Fore.CYAN}{'='*60}\n")
    
    def _save_event(self, event: ExtractionEvent):
        """Save event to JSON file"""
        if not self.save_to_file:
            return
            
        try:
            # Load existing events
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {
                    "session_id": self.session_id,
                    "start_time": datetime.now().isoformat(),
                    "events": [],
                    "file_results": {}
                }
            
            # Add new event
            data["events"].append(event.to_dict())
            data["file_results"] = self.file_results
            
            # Save back
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save event to file: {e}")
    
    def get_session_report(self) -> Dict[str, Any]:
        """Generate complete session report"""
        
        total_files = len(self.file_results)
        successful_files = sum(1 for r in self.file_results.values() if r["success"])
        
        total_time = sum(r.get("total_time", 0) for r in self.file_results.values())
        
        all_summaries = {}
        for file_path, result in self.file_results.items():
            summary = result.get("summary", {})
            for key, value in summary.items():
                all_summaries[key] = all_summaries.get(key, 0) + value
        
        report = {
            "session_id": self.session_id,
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": total_files - successful_files,
            "total_processing_time": total_time,
            "average_time_per_file": total_time / total_files if total_files > 0 else 0,
            "total_extracted": all_summaries,
            "stage_performance": {},
            "file_results": self.file_results
        }
        
        # Aggregate stage metrics
        for stage_name, metrics in self.stage_metrics.items():
            if metrics.duration:
                report["stage_performance"][stage_name] = {
                    "total_duration": metrics.duration,
                    "items_processed": metrics.items_processed,
                    "items_failed": metrics.items_failed,
                    "success_rate": (metrics.items_processed - metrics.items_failed) / metrics.items_processed if metrics.items_processed > 0 else 0
                }
        
        return report
    
    def save_session_report(self, output_path: Optional[str] = None):
        """Save complete session report to file"""
        
        report = self.get_session_report()
        
        if not output_path:
            output_path = self.log_dir / f"session_report_{self.session_id}.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Session report saved to: {output_path}")
        
        return output_path

class ProgressTracker:
    """Real-time progress tracking for Dolphin extraction"""
    
    def __init__(self, total_files: int):
        self.total_files = total_files
        self.processed_files = 0
        self.current_file = None
        self.file_progress = {}
        self.start_time = time.time()
        
    def start_file(self, file_name: str, total_pages: int):
        """Start tracking a new file"""
        self.current_file = file_name
        self.file_progress[file_name] = {
            "total_pages": total_pages,
            "processed_pages": 0,
            "stages": {
                "analyzing": {"current": 0, "total": total_pages},
                "parsing": {"current": 0, "total": 0}
            },
            "start_time": time.time()
        }
    
    def update_stage(self, stage: str, current: int, total: int):
        """Update progress for a specific stage"""
        if self.current_file and self.current_file in self.file_progress:
            self.file_progress[self.current_file]["stages"][stage] = {
                "current": current,
                "total": total
            }
    
    def complete_file(self, file_name: str):
        """Mark file as complete"""
        if file_name in self.file_progress:
            self.file_progress[file_name]["end_time"] = time.time()
            self.file_progress[file_name]["duration"] = (
                self.file_progress[file_name]["end_time"] - 
                self.file_progress[file_name]["start_time"]
            )
        self.processed_files += 1
    
    def get_overall_progress(self) -> float:
        """Get overall progress percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    def get_eta(self) -> str:
        """Estimate time remaining"""
        if self.processed_files == 0:
            return "Calculating..."
        
        elapsed = time.time() - self.start_time
        avg_time_per_file = elapsed / self.processed_files
        remaining_files = self.total_files - self.processed_files
        eta_seconds = avg_time_per_file * remaining_files
        
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s"
        elif eta_seconds < 3600:
            return f"{eta_seconds/60:.1f}m"
        else:
            return f"{eta_seconds/3600:.1f}h"