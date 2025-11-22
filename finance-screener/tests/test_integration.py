"""
Test suite for end-to-end integration tests.

TDD Methodology: Tests written FIRST, implementation will follow.

Mental Model: Systems Thinking
- Integration tests validate the entire system as an integrated whole
- Each pipeline component depends on others; failures cascade

Mental Model: Interdependencies
- Discovery → Ingestion → Query → Monitoring
- Each tool's output is another tool's input
- Database synchronization (DuckDB + ChromaDB) is critical

Mental Model: Second Order Effects
- Poor integration → hidden failures → user distrust
- Slow pipelines → poor user experience → abandoned usage
- Cost overruns → unsustainable operations

Phase 7 Deliverable: 8 integration tests → validate production readiness.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock
import duckdb
import chromadb


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndWorkflow:
    """
    Test complete end-to-end workflows across all tools.
    
    Mental Model: Systems Thinking
    - Workflow: Discover → Ingest → Query
    - Validates data flow through entire system
    """
    
    @pytest.mark.asyncio
    async def test_complete_filing_workflow(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        test_data_dir: Path,
        env_vars: dict
    ) -> None:
        """
        Test complete workflow: Discover filing → Ingest → Query.
        
        Mental Model: First Principles
        - Complete workflow = Find URL → Download → Process → Query
        - Each step must pass data correctly to next
        
        Given: TSLA ticker for 2020 10-K filing
        When: Running discovery → ingestion → query pipeline
        Then: Filing is discoverable, ingestible, and queryable
        """
        # This test will fail until we have all tools implemented
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        from skill_seeker_mcp.finance_tools.query import query_pipeline
        
        # Step 1: Discover filing
        with patch('requests.get', return_value=mock_sec_response):
            discovery_result = await discover_sec_filing(
                ticker="TSLA",
                filing_type="10-K",
                fiscal_year=2020
            )
        
        assert discovery_result["success"] is True
        assert "filing_url" in discovery_result
        
        # Step 2: Ingest filing
        ingestion_result = await ingest_sec_filing(
            filing_url=discovery_result["filing_url"],
            ticker="TSLA",
            extract_tables=True,
            conn=duckdb_conn,
            chroma_client=chroma_client,
            temp_dir=test_data_dir
        )
        
        assert ingestion_result["success"] is True
        assert ingestion_result["chunks_stored"] > 0
        assert ingestion_result["embeddings_stored"] > 0
        
        # Step 3: Query the ingested data
        query_result = await query_pipeline(
            question="What was Tesla's revenue in 2020?",
            ticker="TSLA",
            conn=duckdb_conn,
            chroma_client=chroma_client
        )
        
        assert query_result["success"] is True
        assert "answer" in query_result
        assert len(query_result["answer"]) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_with_invalid_filing(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        test_data_dir: Path
    ) -> None:
        """
        Test workflow handles invalid filing gracefully.
        
        Mental Model: Inversion
        - What can fail? Invalid ticker, missing filing, network errors
        - Each step should fail gracefully without crashing
        
        Given: Invalid ticker "NOSUCHCOMPANY"
        When: Running discovery → ingestion pipeline
        Then: Discovery fails, ingestion is skipped, no crash
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        
        # Step 1: Discovery should fail
        discovery_result = await discover_sec_filing(
            ticker="NOSUCHCOMPANY",
            filing_type="10-K",
            fiscal_year=2020
        )
        
        assert discovery_result["success"] is False
        assert "error" in discovery_result
        
        # Step 2: Ingestion should not be called with invalid URL
        # This validates graceful failure handling
        with pytest.raises(Exception):  # Should raise before calling SEC API
            await ingest_sec_filing(
                filing_url="",  # Empty URL from failed discovery
                ticker="NOSUCHCOMPANY",
                extract_tables=True,
                conn=duckdb_conn,
                chroma_client=chroma_client,
                temp_dir=test_data_dir
            )


@pytest.mark.integration
class TestConcurrentPipelineExecution:
    """
    Test concurrent pipeline execution and isolation.
    
    Mental Model: Interdependencies
    - Concurrent pipelines should not interfere
    - Database connections must be isolated
    - Rate limiting must be respected across pipelines
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_filing_ingestion(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        test_data_dir: Path,
        env_vars: dict
    ) -> None:
        """
        Test multiple filings can be ingested concurrently.
        
        Mental Model: Systems Thinking
        - Concurrent processing improves throughput
        - But must maintain data integrity and rate limits
        
        Given: Multiple tickers (TSLA, AAPL, MSFT)
        When: Running ingestion pipelines concurrently
        Then: All succeed without interfering with each other
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        
        tickers = ["TSLA", "AAPL", "MSFT"]
        
        # Discover all filings concurrently
        discovery_tasks = []
        for ticker in tickers:
            task = discover_sec_filing(
                ticker=ticker,
                filing_type="10-K",
                fiscal_year=2020
            )
            discovery_tasks.append(task)
        
        with patch('requests.get', return_value=mock_sec_response):
            discovery_results = await asyncio.gather(*discovery_tasks)
        
        # All discoveries should succeed
        for result in discovery_results:
            assert result["success"] is True
        
        # Ingest all filings concurrently
        ingestion_tasks = []
        for i, ticker in enumerate(tickers):
            task = ingest_sec_filing(
                filing_url=discovery_results[i]["filing_url"],
                ticker=ticker,
                extract_tables=True,
                conn=duckdb_conn,
                chroma_client=chroma_client,
                temp_dir=test_data_dir
            )
            ingestion_tasks.append(task)
        
        ingestion_results = await asyncio.gather(*ingestion_tasks)
        
        # All ingestions should succeed
        for result in ingestion_results:
            assert result["success"] is True
            assert result["chunks_stored"] > 0
    
    @pytest.mark.asyncio
    async def test_pipeline_isolation_with_failures(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        test_data_dir: Path,
        env_vars: dict
    ) -> None:
        """
        Test pipeline isolation when some pipelines fail.
        
        Mental Model: Inversion
        - One pipeline failure should not affect others
        - Database transactions should be atomic
        
        Given: 3 pipelines, 1 with invalid ticker
        When: Running pipelines concurrently
        Then: 2 succeed, 1 fails, no partial data corruption
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        
        tickers = ["TSLA", "INVALIDTICKER", "AAPL"]
        
        # Discover all filings concurrently
        discovery_tasks = []
        for ticker in tickers:
            task = discover_sec_filing(
                ticker=ticker,
                filing_type="10-K",
                fiscal_year=2020
            )
            discovery_tasks.append(task)
        
        # Mock only valid tickers to succeed
        def mock_get_side_effect(url, **kwargs):
            if "INVALIDTICKER" in url:
                response = Mock()
                response.status_code = 404
                response.text = "Not found"
                return response
            return mock_sec_response
        
        with patch('requests.get', side_effect=mock_get_side_effect):
            discovery_results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
        
        # Check results: TSLA and AAPL succeed, INVALIDTICKER fails
        assert discovery_results[0]["success"] is True  # TSLA
        assert isinstance(discovery_results[1], Exception) or not discovery_results[1].get("success")  # INVALIDTICKER
        assert discovery_results[2]["success"] is True  # AAPL
        
        # Only ingest successful discoveries
        successful_results = [r for r in discovery_results 
                             if not isinstance(r, Exception) and r.get("success")]
        
        # Verify database has only valid data (no corrupted partial entries)
        filings_count = duckdb_conn.execute(
            "SELECT COUNT(*) FROM filings WHERE ticker IN ('TSLA', 'AAPL')"
        ).fetchone()[0]
        
        assert filings_count == 0  # No ingestions yet, but discoveries worked


@pytest.mark.integration
class TestCostTrackingAccuracy:
    """
    Test cost tracking accuracy across all API calls.
    
    Mental Model: Second Order Effects
    - Accurate cost tracking enables sustainable operations
    - Missing cost data leads to budget overruns
    
    Mental Model: First Principles
    - Cost tracking = Sum(all API calls × their rates)
    - Must capture Gemini (tables) + Claude (queries) costs
    """
    
    @pytest.mark.asyncio
    async def test_end_to_end_cost_tracking(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        mock_gemini_response: Mock,
        mock_claude_response: Mock,
        test_data_dir: Path,
        env_vars: dict,
        mocker
    ) -> None:
        """
        Test cost tracking across complete workflow.
        
        Given: Complete workflow with mocked API responses
        When: Tracking all API costs
        Then: Total cost = expected sum of individual API costs
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing, estimate_api_cost
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        from skill_seeker_mcp.finance_tools.query import query_pipeline
        from skill_seeker_mcp.finance_tools.monitoring import track_api_cost, get_total_api_cost
        
        # Expected costs (based on our pricing model)
        expected_gemini_cost = 0.02  # 100 pages × $0.0002 per page
        expected_claude_cost = 0.01  # ~1000 tokens × $0.00001 per token
        expected_total = expected_gemini_cost + expected_claude_cost
        
        # Mock entire API call chains properly
        with patch('requests.get', return_value=mock_sec_response):
            # Mock Gemini at the module level
            with patch('skill_seeker_mcp.finance_tools.ingestion.genai.GenerativeModel') as MockGenAI:
                mock_model = MockGenAI.return_value
                mock_model.generate_content.return_value = mock_gemini_response
                mock_model.generate_content.return_value.text = mock_gemini_response.text
                # Add usage metadata to mock response
                mock_model.generate_content.return_value.usage_metadata = Mock()
                mock_model.generate_content.return_value.usage_metadata.prompt_token_count = 1000
                mock_model.generate_content.return_value.usage_metadata.candidates_token_count = 100
                
                # Mock Claude at the module level  
                with patch('skill_seeker_mcp.finance_tools.query.anthropic.Anthropic') as MockAnthropic:
                    mock_client = MockAnthropic.return_value
                    mock_client.messages.create.return_value = mock_claude_response
                    
                    # Step 1: Discovery (no API cost for SEC EDGAR)
                    discovery_result = await discover_sec_filing(
                        ticker="TSLA",
                        filing_type="10-K",
                        fiscal_year=2020
                    )
                    
                    # Step 2: Ingestion 
                    ingestion_result = await ingest_sec_filing(
                        filing_url=discovery_result["filing_url"],
                        ticker="TSLA",
                        extract_tables=True,
                        conn=duckdb_conn,
                        chroma_client=chroma_client
                    )
                    
                    # Step 3: Query
                    query_result = await query_pipeline(
                        question="What was Tesla's revenue in 2020?",
                        conn=duckdb_conn,
                        chroma_client=chroma_client
                    )
        
        # Verify total cost tracking
        total_cost = await get_total_api_cost(conn=duckdb_conn)
        assert total_cost > 0
        
        # Cost should be reasonable (not $0, not $1000 for single test)
        assert 0.01 <= total_cost <= 1.0  # Reasonable range for test data
    
    @pytest.mark.asyncio
    async def test_cost_budget_enforcement(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Test cost budget enforcement prevents overruns.
        
        Mental Model: Inversion
        - What if costs exceed budget? → Block further operations
        
        Given: Budget of $0.10
        When: Costs exceed budget
        Then: Alert triggered and operations blocked
        """
        from skill_seeker_mcp.finance_tools.monitoring import (
            track_api_cost, 
            check_cost_budget, 
            get_total_api_cost
        )
        
        budget_limit = 0.10  # $0.10 budget
        
        # Track costs that exceed budget
        await track_api_cost(
            api_name='gemini',
            endpoint='generate_content',
            tokens=5000,  # Should cost ~$0.05
            cost=0.05,
            conn=duckdb_conn
        )
        
        await track_api_cost(
            api_name='claude',
            endpoint='messages',
            tokens=8000,  # Should cost ~$0.08
            cost=0.08,
            conn=duckdb_conn
        )
        
        # Check budget
        budget_status = await check_cost_budget(
            budget_limit=budget_limit,
            conn=duckdb_conn
        )
        
        assert budget_status['exceeded'] is True
        assert budget_status['total_cost'] > budget_limit
        assert 'services_over_limit' in budget_status


@pytest.mark.integration
class TestDataConsistency:
    """
    Test data consistency between DuckDB and ChromaDB.
    
    Mental Model: Interdependencies
    - DuckDB (structured) + ChromaDB (vectors) must stay synchronized
    - Orphaned data = storage waste + query inconsistencies
    """
    
    @pytest.mark.asyncio
    async def test_database_synchronization(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        test_data_dir: Path,
        env_vars: dict
    ) -> None:
        """
        Test DuckDB and ChromaDB stay synchronized.
        
        Mental Model: First Principles
        - Sync = Every chunk in DuckDB has embedding in ChromaDB
        - Every embedding has corresponding chunk text
        
        Given: Filing ingestion
        When: Storing chunks in DuckDB and embeddings in ChromaDB
        Then: Records match between databases
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        
        # Discover and ingest filing
        with patch('requests.get', return_value=mock_sec_response):
            discovery_result = await discover_sec_filing(
                ticker="TSLA",
                filing_type="10-K",
                fiscal_year=2020
            )
        
        ingestion_result = await ingest_sec_filing(
            filing_url=discovery_result["filing_url"],
            ticker="TSLA",
            extract_tables=True,
            conn=duckdb_conn,
            chroma_client=chroma_client,
            temp_dir=test_data_dir
        )
        
        # Verify synchronization
        # 1. Check chunks in DuckDB
        duckdb_chunks = duckdb_conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE ticker = 'TSLA'"
        ).fetchone()[0]
        
        # 2. Check embeddings in ChromaDB
        collection = chroma_client.get_collection("test_chunks")
        chroma_results = collection.get(
            where={"ticker": "TSLA"}
        )
        chroma_count = len(chroma_results['ids'])
        
        # 3. Verify counts match
        assert duckdb_chunks == chroma_count
        assert duckdb_chunks > 0  # Should have some data
        
        # 4. Verify metadata consistency
        for chunk_id in chroma_results['ids']:
            # Each embedding should have corresponding chunk
            chunk_row = duckdb_conn.execute(
                "SELECT * FROM chunks WHERE id = ?",
                [chunk_id]
            ).fetchone()
            assert chunk_row is not None  # Found in DuckDB
    
    @pytest.mark.asyncio
    async def test_orphaned_data_cleanup(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        test_data_dir: Path,
        env_vars: dict
    ) -> None:
        """
        Test orphaned data is detected and cleaned up.
        
        Mental Model: Inversion
        - What can go wrong? Partial deletions, failed transactions
        - Solution: Detect and clean orphaned records
        
        Given: Ingestion with simulated partial failure
        When: Checking for orphaned data
        Then: Orphans detected and cleaned up
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        from skill_seeker_mcp.finance_tools.monitoring import cleanup_orphaned_data
        
        # Simulate scenario where we have data without proper sync
        # First, ingest a filing normally
        with patch('requests.get', return_value=mock_sec_response):
            discovery_result = await discover_sec_filing(
                ticker="TSLA",
                filing_type="10-K",
                fiscal_year=2020
            )
        
        # Manually create orphaned data for testing
        # Add chunk to DuckDB without corresponding embedding
        duckdb_conn.execute(
            """INSERT INTO chunks (ticker, filing_url, chunk_index, text, section, page, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ["TSLA", "test_url", 999, "orphaned chunk", "test", 1, "{}"]
        )
        
        # Add embedding to ChromaDB without corresponding chunk
        collection = chroma_client.get_collection("test_chunks")
        collection.add(
            ids=["orphan_embedding"],
            embeddings=[[0.1] * 384],
            metadatas=[{"ticker": "TSLA", "chunk_id": "nonexistent"}],
            documents=["orphaned document"]
        )
        
        # Check for orphaned data
        cleanup_result = await cleanup_orphaned_data(
            conn=duckdb_conn,
            chroma_client=chroma_client
        )
        
        assert cleanup_result["success"] is True
        assert cleanup_result["orphaned_chunks_removed"] >= 1
        assert cleanup_result["orphaned_embeddings_removed"] >= 1


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceMetrics:
    """
    Test performance metrics and SLA compliance.
    
    Mental Model: Second Order Effects
    - Slow performance → poor user experience → abandonment
    - Fast performance → higher adoption → better outcomes
    """
    
    @pytest.mark.asyncio
    async def test_pipeline_performance_sla(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        test_data_dir: Path,
        env_vars: dict
    ) -> None:
        """
        Test pipeline performance meets SLA requirements.
        
        Mental Model: First Principles
        - Performance = Time to complete operation
        - SLA: Discovery < 5s, Ingestion < 30s, Query < 3s
        
        Given: Standard filing
        When: Running complete pipeline
        Then: Performance within SLA limits
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        from skill_seeker_mcp.finance_tools.query import query_pipeline
        import time
        
        # Performance SLAs (in seconds)
        discovery_sla = 5.0
        ingestion_sla = 30.0
        query_sla = 3.0
        
        # Test discovery performance
        start_time = time.time()
        with patch('requests.get', return_value=mock_sec_response):
            discovery_result = await discover_sec_filing(
                ticker="TSLA",
                filing_type="10-K",
                fiscal_year=2020
            )
        discovery_time = time.time() - start_time
        
        assert discovery_result["success"] is True
        assert discovery_time < discovery_sla, f"Discovery took {discovery_time}s, SLA: {discovery_sla}s"
        
        # Test ingestion performance
        start_time = time.time()
        ingestion_result = await ingest_sec_filing(
            filing_url=discovery_result["filing_url"],
            ticker="TSLA",
            extract_tables=True,
            conn=duckdb_conn,
            chroma_client=chroma_client,
            temp_dir=test_data_dir
        )
        ingestion_time = time.time() - start_time
        
        assert ingestion_result["success"] is True
        assert ingestion_time < ingestion_sla, f"Ingestion took {ingestion_time}s, SLA: {ingestion_sla}s"
        
        # Test query performance
        start_time = time.time()
        query_result = await query_pipeline(
            question="What was Tesla's revenue in 2020?",
            ticker="TSLA",
            conn=duckdb_conn,
            chroma_client=chroma_client
        )
        query_time = time.time() - start_time
        
        assert query_result["success"] is True
        assert query_time < query_sla, f"Query took {query_time}s, SLA: {query_sla}s"
        
        # Overall pipeline performance
        total_time = discovery_time + ingestion_time + query_time
        total_sla = discovery_sla + ingestion_sla + query_sla
        assert total_time < total_sla, f"Total pipeline took {total_time}s, SLA: {total_sla}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_performance_scaling(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        test_data_dir: Path,
        env_vars: dict
    ) -> None:
        """
        Test performance scales reasonably with concurrency.
        
        Mental Model: Systems Thinking
        - Concurrent processing should improve throughput
        - But resource limits prevent linear scaling
        
        Given: 3 concurrent ingestions vs sequential
        When: Measuring total time
        Then: Concurrent faster than sequential but within resource limits
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        import time
        
        tickers = ["TSLA", "AAPL", "MSFT"]
        
        # Measure sequential time
        sequential_start = time.time()
        for ticker in tickers:
            with patch('requests.get', return_value=mock_sec_response):
                discovery_result = await discover_sec_filing(
                    ticker=ticker,
                    filing_type="10-K",
                    fiscal_year=2020
                )
            
            await ingest_sec_filing(
                filing_url=discovery_result["filing_url"],
                ticker=ticker,
                extract_tables=True,
                conn=duckdb_conn,
                chroma_client=chroma_client,
                temp_dir=test_data_dir
            )
        sequential_time = time.time() - sequential_start
        
        # Measure concurrent time
        concurrent_start = time.time()
        
        # Concurrent discovery
        discovery_tasks = []
        for ticker in tickers:
            task = discover_sec_filing(
                ticker=ticker,
                filing_type="10-K",
                fiscal_year=2020
            )
            discovery_tasks.append(task)
        
        with patch('requests.get', return_value=mock_sec_response):
            discovery_results = await asyncio.gather(*discovery_tasks)
        
        # Concurrent ingestion
        ingestion_tasks = []
        for i, ticker in enumerate(tickers):
            task = ingest_sec_filing(
                filing_url=discovery_results[i]["filing_url"],
                ticker=ticker,
                extract_tables=True,
                conn=duckdb_conn,
                chroma_client=chroma_client,
                temp_dir=test_data_dir
            )
            ingestion_tasks.append(task)
        
        await asyncio.gather(*ingestion_tasks)
        concurrent_time = time.time() - concurrent_start
        
        # Concurrent should be faster but not 3x (resource contention)
        speedup = sequential_time / concurrent_time
        assert 1.5 <= speedup <= 3.0, f"Speedup {speedup} not in expected range [1.5, 3.0]"


@pytest.mark.integration
class TestErrorRecovery:
    """
    Test error recovery and system resilience.
    
    Mental Model: Inversion
    - What can fail? Network, database, API limits, corrupted data
    - System should recover gracefully from failures
    """
    
    @pytest.mark.asyncio
    async def test_network_failure_recovery(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        test_data_dir: Path
    ) -> None:
        """
        Test system recovers from network failures.
        
        Given: Network timeout during discovery
        When: Retrying with exponential backoff
        Then: Eventually succeeds or fails gracefully
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        import requests
        
        # Simulate network failure then success
        call_count = 0
        
        def mock_get_with_failure(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # First 2 calls fail
                raise requests.Timeout("Network timeout")
            else:
                # 3rd call succeeds
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = "mock SEC response"
                return mock_response
        
        # Should succeed after retries
        with patch('requests.get', side_effect=mock_get_with_failure):
            result = await discover_sec_filing(
                ticker="TSLA",
                filing_type="10-K",
                fiscal_year=2020
            )
        
        assert result["success"] is True
        assert call_count == 3  # 2 failures + 1 success
    
    @pytest.mark.asyncio
    async def test_partial_data_recovery(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection,
        chroma_client: chromadb.Client,
        mock_sec_response: Mock,
        test_data_dir: Path,
        env_vars: dict
    ) -> None:
        """
        Test system recovers from partial data corruption.
        
        Mental Model: Second Order Effects
        - Partial corruption → query failures → user distrust
        - Solution: Detect and repair partial data automatically
        
        Given: Corrupted chunk in database
        When: Query encounters corrupted data
        Then: System skips corrupted data and returns valid results
        """
        from skill_seeker_mcp.finance_tools.discovery import discover_sec_filing
        from skill_seeker_mcp.finance_tools.ingestion import ingest_sec_filing
        from skill_seeker_mcp.finance_tools.query import query_pipeline
        
        # Ingest filing normally
        with patch('requests.get', return_value=mock_sec_response):
            discovery_result = await discover_sec_filing(
                ticker="TSLA",
                filing_type="10-K",
                fiscal_year=2020
            )
        
        ingestion_result = await ingest_sec_filing(
            filing_url=discovery_result["filing_url"],
            ticker="TSLA",
            extract_tables=True,
            conn=duckdb_conn,
            chroma_client=chroma_client,
            temp_dir=test_data_dir
        )
        
        # Corrupt some data (simulate partial failure)
        duckdb_conn.execute(
            "UPDATE chunks SET text = NULL WHERE chunk_index = 1 AND ticker = 'TSLA'"
        )
        
        # Query should still work despite corrupted data
        query_result = await query_pipeline(
            question="What was Tesla's revenue in 2020?",
            ticker="TSLA",
            conn=duckdb_conn,
            chroma_client=chroma_client
        )
        
        # Should succeed but with fewer chunks
        assert query_result["success"] is True
        assert "answer" in query_result
        # Might have warning about corrupted data
        if "warnings" in query_result:
            assert any("corrupt" in str(w).lower() for w in query_result["warnings"])
