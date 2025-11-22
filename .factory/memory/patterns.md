# Code Patterns & Conventions

## Async Scraping Pattern

### Basic Async Scraping

```python
import asyncio
import aiohttp
from typing import List, Dict, Optional

async def scrape_all_async(self, urls: List[str]) -> List[Dict]:
    """Scrape multiple URLs with connection pooling.
    
    Uses aiohttp for async HTTP requests with proper connection
    pooling and error handling.
    """
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        connector=aiohttp.TCPConnector(limit=10)  # Max 10 concurrent connections
    ) as session:
        tasks = [self.scrape_page_async(url, session) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions, log errors
    successful = []
    for result in results:
        if isinstance(result, dict):
            successful.append(result)
        elif isinstance(result, Exception):
            self.logger.error(f"Scraping error: {result}")
    
    return successful
```

### Single Page Async Scraping

```python
async def scrape_page_async(
    self, 
    url: str, 
    session: aiohttp.ClientSession
) -> Optional[Dict]:
    """Scrape single page with rate limiting and error handling."""
    try:
        # Respect rate limiting
        await asyncio.sleep(self.rate_limit)
        
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                return self.extract_content(html, url)
            else:
                self.logger.warning(f"HTTP {response.status} for {url}")
                return None
                
    except asyncio.TimeoutError:
        self.logger.warning(f"Timeout scraping {url}")
        return None
    except aiohttp.ClientError as e:
        self.logger.error(f"Client error for {url}: {e}")
        return None
    except Exception as e:
        self.logger.error(f"Unexpected error scraping {url}: {e}")
        return None
```

## Error Handling Pattern

### Comprehensive Error Handling

```python
def risky_operation(self, config_path: str) -> Dict[str, Any]:
    """Perform operation with layered error handling."""
    try:
        # Validate inputs first
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config not found: {config_path}")
        
        # Load and validate
        with open(config_path) as f:
            config = json.load(f)
        
        if 'base_url' not in config:
            raise ValueError("Missing required field: base_url")
        
        # Perform operation
        result = self._process_config(config)
        return {"status": "success", "data": result}
        
    except FileNotFoundError as e:
        # Known issue - provide helpful message
        self.logger.warning(f"Configuration issue: {e}")
        return {
            "status": "error",
            "error_type": "FileNotFoundError",
            "message": str(e),
            "suggestion": "Check that the config file path is correct"
        }
        
    except json.JSONDecodeError as e:
        # Specific error type with recovery suggestion
        self.logger.error(f"Invalid JSON in config: {e}")
        return {
            "status": "error",
            "error_type": "JSONDecodeError",
            "message": f"Invalid JSON at line {e.lineno}: {e.msg}",
            "suggestion": "Validate JSON syntax with validate_config tool"
        }
        
    except ValueError as e:
        # Validation error
        self.logger.error(f"Validation error: {e}")
        return {
            "status": "error",
            "error_type": "ValueError",
            "message": str(e),
            "suggestion": "Check config against schema in docs"
        }
        
    except Exception as e:
        # Unexpected error - log full traceback
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
            "suggestion": "Check logs for detailed traceback"
        }
```

## Configuration Pattern

### Using Constants

```python
# Always use constants.py for magic numbers
from cli.constants import (
    DEFAULT_RATE_LIMIT,
    DEFAULT_MAX_PAGES,
    CONTENT_PREVIEW_LENGTH,
    MIN_CATEGORIZATION_SCORE
)

class DocToSkillConverter:
    """Documentation to skill converter with configurable parameters."""
    
    def __init__(
        self, 
        name: str,
        base_url: str,
        description: str,
        rate_limit: float = DEFAULT_RATE_LIMIT,
        max_pages: int = DEFAULT_MAX_PAGES
    ):
        self.name = name
        self.base_url = base_url
        self.description = description
        self.rate_limit = rate_limit
        self.max_pages = max_pages
        
        # Use constants for internal limits
        self.preview_length = CONTENT_PREVIEW_LENGTH
        self.min_score = MIN_CATEGORIZATION_SCORE
```

### Configuration Validation

```python
from typing import Dict, List, Any
from pathlib import Path

def validate_config(config: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate configuration structure and values.
    
    Returns:
        (is_valid, list of error messages)
    """
    errors = []
    
    # Required fields
    required = ['name', 'base_url', 'description']
    for field in required:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Type checking
    if 'max_pages' in config and not isinstance(config['max_pages'], int):
        errors.append(f"max_pages must be integer, got {type(config['max_pages'])}")
    
    if 'rate_limit' in config and not isinstance(config['rate_limit'], (int, float)):
        errors.append(f"rate_limit must be number, got {type(config['rate_limit'])}")
    
    # Value validation
    if 'max_pages' in config and config['max_pages'] < 1:
        errors.append("max_pages must be positive")
    
    if 'rate_limit' in config and config['rate_limit'] < 0:
        errors.append("rate_limit cannot be negative")
    
    # URL validation
    if 'base_url' in config:
        url = config['base_url']
        if not url.startswith(('http://', 'https://')):
            errors.append(f"base_url must start with http:// or https://: {url}")
    
    return len(errors) == 0, errors
```

## Logging Pattern

### Structured Logging

```python
import logging
from pathlib import Path

def setup_logging(
    name: str, 
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """Setup logger with consistent format."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler with colors (optional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter with timestamp and level
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Capture everything in file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Usage
logger = setup_logging(__name__, level=logging.INFO)

# Log at appropriate levels
logger.debug("Detailed debugging info")  # Development only
logger.info("Normal operation milestone")  # Progress updates
logger.warning("Something unexpected but recoverable")  # Issues
logger.error("Operation failed", exc_info=True)  # Errors with traceback
```

## Testing Pattern

### Fixture-Based Testing

```python
import pytest
from pathlib import Path
from cli.doc_scraper import DocToSkillConverter

@pytest.fixture
def mock_scraper(tmp_path):
    """Provide configured scraper instance with temp directory.
    
    Args:
        tmp_path: Pytest fixture for temporary directory
        
    Returns:
        DocToSkillConverter instance configured for testing
    """
    return DocToSkillConverter(
        name="test",
        base_url="https://example.com",
        description="Test scraper for unit tests",
        output_dir=str(tmp_path),
        max_pages=10  # Small for fast tests
    )

@pytest.fixture
def sample_html():
    """Provide sample HTML for parsing tests."""
    return """
    <html>
        <body>
            <article>
                <h1>Test Page</h1>
                <p>Sample content</p>
                <pre><code class="language-python">print("hello")</code></pre>
            </article>
        </body>
    </html>
    """

def test_content_extraction(mock_scraper, sample_html):
    """Test that content extraction works correctly.
    
    Uses Arrange-Act-Assert pattern for clarity.
    """
    # Arrange
    url = "https://example.com/test"
    
    # Act
    result = mock_scraper.extract_content(sample_html, url)
    
    # Assert
    assert result is not None, "Should extract content"
    assert result['title'] == "Test Page"
    assert "Sample content" in result['content']
    assert len(result['code_blocks']) == 1
    assert result['code_blocks'][0]['language'] == 'python'
```

### Async Test Pattern

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_scraping_concurrent(mock_scraper):
    """Test async scraper handles concurrent requests correctly."""
    # Arrange
    urls = [f"https://example.com/page{i}" for i in range(10)]
    
    # Mock async HTTP calls
    async def mock_fetch(url):
        await asyncio.sleep(0.1)  # Simulate network delay
        return {"url": url, "content": "Test", "title": "Page"}
    
    # Replace method temporarily
    original = mock_scraper.scrape_page_async
    mock_scraper.scrape_page_async = mock_fetch
    
    # Act
    start = asyncio.get_event_loop().time()
    results = await mock_scraper.scrape_all_async(urls)
    elapsed = asyncio.get_event_loop().time() - start
    
    # Restore original method
    mock_scraper.scrape_page_async = original
    
    # Assert
    assert len(results) == 10, "Should scrape all URLs"
    assert elapsed < 1.0, \
        f"Should complete in <1s due to concurrency (took {elapsed:.2f}s)"
```

## File Operations Pattern

### Safe File Operations

```python
from pathlib import Path
from typing import Optional
import json

def safe_write_json(
    data: dict, 
    file_path: Path,
    create_dirs: bool = True
) -> bool:
    """Write JSON file safely with error handling.
    
    Args:
        data: Dictionary to write as JSON
        file_path: Path to output file
        create_dirs: Whether to create parent directories
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create parent directories if needed
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write atomically (write to temp, then rename)
        temp_path = file_path.with_suffix('.tmp')
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic rename
        temp_path.replace(file_path)
        
        return True
        
    except IOError as e:
        logger.error(f"Failed to write {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error writing {file_path}: {e}")
        return False

def safe_read_json(file_path: Path) -> Optional[dict]:
    """Read JSON file safely with error handling."""
    try:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        with open(file_path, encoding='utf-8') as f:
            return json.load(f)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None
```

## Type Hints Pattern

### Comprehensive Type Annotations

```python
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path

def scrape_documentation(
    config_path: Path,
    async_mode: bool = False,
    max_workers: int = 4
) -> Dict[str, Any]:
    """Scrape documentation with full type hints.
    
    Args:
        config_path: Path to configuration file
        async_mode: Whether to use async scraping
        max_workers: Number of concurrent workers (async mode only)
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - pages: List of scraped pages (on success)
            - total_pages: Number of pages scraped (on success)
            - error: Error message (on error)
    """
    # Implementation...
    pass

# Complex return types
def categorize_pages(
    pages: List[Dict[str, str]]
) -> Tuple[Dict[str, List[Dict]], List[Dict]]:
    """Categorize pages into groups.
    
    Returns:
        Tuple of (categorized_pages, uncategorized_pages)
    """
    # Implementation...
    pass

# Union types for flexible inputs
def process_config(
    config: Union[str, Path, Dict]
) -> Dict[str, Any]:
    """Process configuration from various input types."""
    # Implementation...
    pass
```

## See Also

- **AGENTS.md:** Development guidelines and boundaries
- **CLAUDE.md:** Technical architecture
- **.droid.yaml:** Code conventions and review rules
- **tests/:** Test examples for all patterns
