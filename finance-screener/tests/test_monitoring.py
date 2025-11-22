"""
Test suite for monitoring tool - Pipeline health, cost tracking, error logging.

Mental Model: Interdependencies
- Monitoring affects Discovery, Ingestion, Query
- Second Order Effects: Poor monitoring → hidden failures → user distrust

TDD Methodology: Tests written FIRST, implementation AFTER.
Phase 6 Deliverable: 13 tests → monitoring.py implementation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import duckdb
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any


@pytest.mark.unit
class TestPipelineHealthMonitoring:
    """
    Test pipeline execution tracking and metrics.
    
    Mental Model: Systems Thinking (pipeline stages interconnected)
    """
    
    @pytest.mark.asyncio
    async def test_track_pipeline_execution_success(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test successful pipeline execution tracking.
        
        Mental Model: First Principles (what to track: name, status, duration)
        
        Given: Pipeline completes successfully
        When: track_pipeline_execution is called
        Then: Logs success metrics to pipeline_executions table
        """
        from skill_seeker_mcp.finance_tools.monitoring import track_pipeline_execution
        
        # Arrange (Given)
        pipeline_name = "discovery"
        status = "success"
        duration_ms = 450.5
        metadata = {"ticker": "TSLA", "filing_type": "10-K"}
        
        # Act (When)
        result = await track_pipeline_execution(
            pipeline_name=pipeline_name,
            status=status,
            duration_ms=duration_ms,
            metadata=metadata,
            conn=duckdb_conn
        )
        
        # Assert (Then)
        assert result["success"] is True
        assert result["pipeline_name"] == pipeline_name
        
        # Verify database insert
        rows = duckdb_conn.execute(
            "SELECT * FROM pipeline_executions WHERE pipeline_name = ?",
            [pipeline_name]
        ).fetchall()
        
        assert len(rows) == 1
        assert rows[0][1] == pipeline_name      # pipeline_name column
        assert rows[0][2] == "success"          # status column
        assert abs(rows[0][5] - duration_ms) < 0.01  # duration_ms column (float comparison)
    
    @pytest.mark.asyncio
    async def test_track_pipeline_execution_failure(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test failed pipeline execution tracking.
        
        Mental Model: Inversion (what can fail: network, DB, API)
        
        Given: Pipeline fails with error
        When: track_pipeline_execution is called with status='failure'
        Then: Logs failure metrics with error details
        """
        from skill_seeker_mcp.finance_tools.monitoring import track_pipeline_execution
        
        # Arrange
        pipeline_name = "ingestion"
        status = "failure"
        duration_ms = 2500.0
        metadata = {
            "ticker": "AAPL",
            "error": "Network timeout downloading PDF",
            "retry_count": 3
        }
        
        # Act
        result = await track_pipeline_execution(
            pipeline_name=pipeline_name,
            status=status,
            duration_ms=duration_ms,
            metadata=metadata,
            conn=duckdb_conn
        )
        
        # Assert
        assert result["success"] is True
        
        # Verify failure logged
        rows = duckdb_conn.execute(
            "SELECT * FROM pipeline_executions WHERE pipeline_name = ? AND status = ?",
            [pipeline_name, "failure"]
        ).fetchall()
        
        assert len(rows) == 1
        assert rows[0][2] == "failure"
    
    @pytest.mark.asyncio
    async def test_calculate_pipeline_metrics(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test pipeline metrics calculation (latency, throughput, success rate).
        
        Mental Model: Systems Thinking (aggregate metrics reveal system health)
        
        Given: Multiple pipeline executions recorded
        When: calculate_pipeline_metrics is called
        Then: Returns aggregated metrics (avg latency, success rate, throughput)
        """
        from skill_seeker_mcp.finance_tools.monitoring import (
            track_pipeline_execution,
            calculate_pipeline_metrics
        )
        
        # Arrange: Log 10 executions (8 success, 2 failure)
        pipeline_name = "query"
        
        for i in range(8):
            await track_pipeline_execution(
                pipeline_name=pipeline_name,
                status="success",
                duration_ms=100.0 + (i * 10),
                metadata={"query_id": i},
                conn=duckdb_conn
            )
        
        for i in range(2):
            await track_pipeline_execution(
                pipeline_name=pipeline_name,
                status="failure",
                duration_ms=5000.0,
                metadata={"query_id": 8 + i, "error": "Timeout"},
                conn=duckdb_conn
            )
        
        # Act
        metrics = await calculate_pipeline_metrics(
            pipeline_name=pipeline_name,
            time_window_hours=24,
            conn=duckdb_conn
        )
        
        # Assert
        assert metrics["success"] is True
        assert metrics["total_executions"] == 10
        assert metrics["success_count"] == 8
        assert metrics["failure_count"] == 2
        assert abs(metrics["success_rate"] - 0.80) < 0.01  # 80% (float comparison)
        assert 100.0 < metrics["avg_latency_ms"] < 2000.0  # Average of successes and failures
    
    @pytest.mark.asyncio
    async def test_detect_pipeline_bottlenecks(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test bottleneck detection (slow pipelines).
        
        Mental Model: Inversion (what slows down the system?)
        
        Given: Some pipelines are consistently slow
        When: detect_pipeline_bottlenecks is called
        Then: Returns list of slow pipelines with recommendations
        """
        from skill_seeker_mcp.finance_tools.monitoring import (
            track_pipeline_execution,
            detect_pipeline_bottlenecks
        )
        
        # Arrange: Log fast and slow pipelines
        # Discovery: Fast (avg 100ms)
        for i in range(5):
            await track_pipeline_execution(
                pipeline_name="discovery",
                status="success",
                duration_ms=100.0,
                metadata={},
                conn=duckdb_conn
            )
        
        # Ingestion: Slow (avg 5000ms)
        for i in range(5):
            await track_pipeline_execution(
                pipeline_name="ingestion",
                status="success",
                duration_ms=5000.0,
                metadata={},
                conn=duckdb_conn
            )
        
        # Act
        bottlenecks = await detect_pipeline_bottlenecks(
            threshold_ms=1000.0,  # Pipelines avg >1s are bottlenecks
            conn=duckdb_conn
        )
        
        # Assert
        assert bottlenecks["success"] is True
        assert len(bottlenecks["bottlenecks"]) == 1
        assert bottlenecks["bottlenecks"][0]["pipeline_name"] == "ingestion"
        assert bottlenecks["bottlenecks"][0]["avg_latency_ms"] == 5000.0


@pytest.mark.unit
class TestCostTracking:
    """
    Test API cost tracking for Gemini and Claude.
    
    Mental Model: Second Order Effects (cost monitoring prevents budget overruns)
    """
    
    @pytest.mark.asyncio
    async def test_track_api_costs_gemini(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test Gemini Vision API cost tracking.
        
        Mental Model: First Principles (track: api_name, endpoint, tokens, cost)
        
        Given: Gemini Vision API called for table extraction
        When: track_api_cost is called
        Then: Logs cost to api_costs table
        """
        from skill_seeker_mcp.finance_tools.monitoring import track_api_cost
        
        # Arrange
        api_name = "gemini"
        endpoint = "models/gemini-1.5-pro:generateContent"
        tokens = 0  # Vision API doesn't use tokens
        cost_usd = 0.004  # $0.004 per table
        metadata = {"ticker": "TSLA", "num_tables": 1}
        
        # Act
        result = await track_api_cost(
            api_name=api_name,
            endpoint=endpoint,
            tokens=tokens,
            cost_usd=cost_usd,
            metadata=metadata,
            conn=duckdb_conn
        )
        
        # Assert
        assert result["success"] is True
        
        # Verify database insert
        rows = duckdb_conn.execute(
            "SELECT * FROM api_costs WHERE api_name = ?",
            [api_name]
        ).fetchall()
        
        assert len(rows) == 1
        assert rows[0][1] == "gemini"        # api_name
        assert abs(rows[0][5] - 0.004) < 0.0001  # cost_usd
    
    @pytest.mark.asyncio
    async def test_track_api_costs_claude(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test Claude API cost tracking.
        
        Mental Model: First Principles (track token usage for cost calculation)
        
        Given: Claude API called for text-to-SQL
        When: track_api_cost is called
        Then: Logs tokens and cost to api_costs table
        """
        from skill_seeker_mcp.finance_tools.monitoring import track_api_cost
        
        # Arrange
        api_name = "claude"
        endpoint = "messages"
        tokens = 1500  # Input + output tokens
        cost_usd = 0.015  # ~$0.01 per 1000 tokens
        metadata = {"query": "Show me TSLA revenue 2020"}
        
        # Act
        result = await track_api_cost(
            api_name=api_name,
            endpoint=endpoint,
            tokens=tokens,
            cost_usd=cost_usd,
            metadata=metadata,
            conn=duckdb_conn
        )
        
        # Assert
        assert result["success"] is True
        
        # Verify token tracking
        rows = duckdb_conn.execute(
            "SELECT * FROM api_costs WHERE api_name = ?",
            [api_name]
        ).fetchall()
        
        assert len(rows) == 1
        assert rows[0][4] == 1500  # tokens
    
    @pytest.mark.asyncio
    async def test_track_api_costs_total(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test total API cost calculation across all services.
        
        Mental Model: Systems Thinking (aggregate costs across services)
        
        Given: Multiple API calls to Gemini and Claude
        When: get_total_api_cost is called
        Then: Returns sum of all costs
        """
        from skill_seeker_mcp.finance_tools.monitoring import (
            track_api_cost,
            get_total_api_cost
        )
        
        # Arrange: Track multiple API calls
        await track_api_cost("gemini", "vision", 0, 0.004, {}, duckdb_conn)
        await track_api_cost("gemini", "vision", 0, 0.004, {}, duckdb_conn)
        await track_api_cost("claude", "messages", 1000, 0.010, {}, duckdb_conn)
        await track_api_cost("claude", "messages", 500, 0.005, {}, duckdb_conn)
        
        # Act
        total_cost = await get_total_api_cost(
            time_window_hours=24,
            conn=duckdb_conn
        )
        
        # Assert
        assert total_cost["success"] is True
        assert abs(total_cost["total_cost_usd"] - 0.023) < 0.001  # 0.004 + 0.004 + 0.010 + 0.005
        assert abs(total_cost["gemini_cost_usd"] - 0.008) < 0.001  # Float comparison
        assert abs(total_cost["claude_cost_usd"] - 0.015) < 0.001  # Float comparison
    
    @pytest.mark.asyncio
    async def test_cost_budget_alerts(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test cost budget alert system.
        
        Mental Model: Inversion (prevent cost overruns before they happen)
        
        Given: API costs exceed budget threshold
        When: check_cost_budget is called
        Then: Returns alert with exceeded services
        """
        from skill_seeker_mcp.finance_tools.monitoring import (
            track_api_cost,
            check_cost_budget
        )
        
        # Arrange: Exceed Gemini budget ($0.05)
        for i in range(20):  # 20 tables * $0.004 = $0.08
            await track_api_cost("gemini", "vision", 0, 0.004, {}, duckdb_conn)
        
        # Act
        alert = await check_cost_budget(
            budget_limits={"gemini": 0.05, "claude": 1.00},
            time_window_hours=24,
            conn=duckdb_conn
        )
        
        # Assert
        assert alert["success"] is True
        assert alert["budget_exceeded"] is True
        assert "gemini" in alert["exceeded_services"]
        assert abs(alert["exceeded_services"]["gemini"]["cost"] - 0.08) < 0.001  # Float comparison
        assert abs(alert["exceeded_services"]["gemini"]["budget"] - 0.05) < 0.001  # Float comparison


@pytest.mark.unit
class TestErrorLogging:
    """
    Test error logging to DuckDB error_log table.
    
    Mental Model: Inversion (track failures to prevent recurrence)
    """
    
    @pytest.mark.asyncio
    async def test_log_error_to_duckdb(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test error logging to database.
        
        Mental Model: First Principles (log: type, message, context, timestamp)
        
        Given: An error occurs in a pipeline
        When: log_error is called
        Then: Inserts error into error_log table
        """
        from skill_seeker_mcp.finance_tools.monitoring import log_error
        
        # Arrange
        error_type = "NetworkTimeout"
        error_message = "Failed to download PDF from SEC EDGAR after 3 retries"
        context = {
            "ticker": "AAPL",
            "filing_url": "https://www.sec.gov/...",
            "pipeline": "ingestion"
        }
        
        # Act
        result = await log_error(
            error_type=error_type,
            error_message=error_message,
            context=context,
            conn=duckdb_conn
        )
        
        # Assert
        assert result["success"] is True
        
        # Verify database insert
        rows = duckdb_conn.execute(
            "SELECT * FROM error_log WHERE error_type = ?",
            [error_type]
        ).fetchall()
        
        assert len(rows) == 1
        assert rows[0][2] == error_type
        assert rows[0][3] == error_message
    
    @pytest.mark.asyncio
    async def test_retrieve_error_history(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test error history retrieval.
        
        Mental Model: Systems Thinking (error patterns reveal systemic issues)
        
        Given: Multiple errors logged
        When: get_error_history is called
        Then: Returns errors sorted by timestamp
        """
        from skill_seeker_mcp.finance_tools.monitoring import (
            log_error,
            get_error_history
        )
        
        # Arrange: Log multiple errors
        await log_error("NetworkTimeout", "Error 1", {"id": 1}, duckdb_conn)
        await log_error("DatabaseLock", "Error 2", {"id": 2}, duckdb_conn)
        await log_error("APIRateLimit", "Error 3", {"id": 3}, duckdb_conn)
        
        # Act
        history = await get_error_history(
            limit=10,
            error_type=None,  # All error types
            conn=duckdb_conn
        )
        
        # Assert
        assert history["success"] is True
        assert len(history["errors"]) == 3
        assert history["errors"][0]["error_type"] in ["NetworkTimeout", "DatabaseLock", "APIRateLimit"]
    
    @pytest.mark.asyncio
    async def test_error_rate_calculation(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test error rate calculation per pipeline.
        
        Mental Model: Second Order Effects (high error rate → system unreliable)
        
        Given: Pipeline executions with some failures
        When: calculate_error_rate is called
        Then: Returns error rate percentage
        """
        from skill_seeker_mcp.finance_tools.monitoring import (
            track_pipeline_execution,
            calculate_error_rate
        )
        
        # Arrange: 7 success, 3 failures = 30% error rate
        for i in range(7):
            await track_pipeline_execution(
                "discovery", "success", 100.0, {}, duckdb_conn
            )
        
        for i in range(3):
            await track_pipeline_execution(
                "discovery", "failure", 5000.0, {"error": "Timeout"}, duckdb_conn
            )
        
        # Act
        error_rate = await calculate_error_rate(
            pipeline_name="discovery",
            time_window_hours=24,
            conn=duckdb_conn
        )
        
        # Assert
        assert error_rate["success"] is True
        assert error_rate["error_rate"] == 0.30  # 30%
        assert error_rate["total_executions"] == 10
        assert error_rate["failures"] == 3


@pytest.mark.unit
class TestMonitoringIntegration:
    """
    Test monitoring system integration with pipelines.
    
    Mental Model: Interdependencies (monitoring integrates with all pipelines)
    """
    
    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_workflow(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test complete monitoring workflow.
        
        Mental Model: Systems Thinking (integrated monitoring system)
        
        Given: A complete ingestion pipeline runs
        When: Monitoring functions are called throughout
        Then: All metrics, costs, and errors are tracked
        """
        from skill_seeker_mcp.finance_tools.monitoring import (
            track_pipeline_execution,
            track_api_cost,
            log_error,
            get_monitoring_summary
        )
        
        # Arrange & Act: Simulate full pipeline with monitoring
        
        # 1. Discovery succeeds
        await track_pipeline_execution(
            "discovery", "success", 150.0, {"ticker": "TSLA"}, duckdb_conn
        )
        
        # 2. Ingestion starts, uses Gemini
        await track_api_cost("gemini", "vision", 0, 0.016, {"num_tables": 4}, duckdb_conn)
        
        # 3. Ingestion fails (network timeout)
        await track_pipeline_execution(
            "ingestion", "failure", 5000.0, {"error": "Network timeout"}, duckdb_conn
        )
        await log_error(
            "NetworkTimeout", 
            "Failed to download PDF", 
            {"ticker": "TSLA", "pipeline": "ingestion"},
            duckdb_conn
        )
        
        # 4. Get monitoring summary
        summary = await get_monitoring_summary(
            time_window_hours=24,
            conn=duckdb_conn
        )
        
        # Assert
        assert summary["success"] is True
        assert summary["total_pipeline_executions"] == 2
        assert abs(summary["total_api_cost_usd"] - 0.016) < 0.001  # Float comparison
        assert summary["total_errors"] == 1
        assert abs(summary["pipelines"]["discovery"]["success_rate"] - 1.0) < 0.01  # Float comparison
        assert abs(summary["pipelines"]["ingestion"]["success_rate"] - 0.0) < 0.01  # Float comparison
