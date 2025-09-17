import pytest
import time
from unittest.mock import patch

from app.core.cache import GroupsCache


class TestGroupsCache:
    
    def setup_method(self):
        self.cache = GroupsCache(default_ttl=60)

    def test_init_default_ttl(self):
        """Test cache initialization with default TTL."""
        cache = GroupsCache()
        assert cache.default_ttl == 900  # 15 minutes

    def test_init_custom_ttl(self):
        """Test cache initialization with custom TTL."""
        cache = GroupsCache(default_ttl=120)
        assert cache.default_ttl == 120

    def test_generate_key(self):
        """Test cache key generation."""
        key = self.cache._generate_key("test-token", "search-query")
        
        # Key should contain hash of token and the query
        assert "groups_" in key
        assert "search-query" in key
        assert len(key.split('_')) == 3  # groups_{hash}_{query}

    def test_generate_key_case_insensitive(self):
        """Test cache key generation is case insensitive for query."""
        key1 = self.cache._generate_key("token", "Search")
        key2 = self.cache._generate_key("token", "SEARCH")
        key3 = self.cache._generate_key("token", "search")
        
        # All should generate the same key
        assert key1 == key2 == key3

    def test_set_and_get(self):
        """Test setting and getting cache values."""
        test_data = {"groups": [{"id": 1, "name": "Test Group"}]}
        
        self.cache.set("test-token", "query", test_data)
        result = self.cache.get("test-token", "query")
        
        assert result == test_data

    def test_get_nonexistent(self):
        """Test getting non-existent cache entry."""
        result = self.cache.get("nonexistent-token", "query")
        assert result is None

    def test_get_expired(self):
        """Test getting expired cache entry."""
        test_data = {"groups": [{"id": 1, "name": "Test Group"}]}
        
        # Set with very short TTL
        self.cache.default_ttl = 0.1  # 0.1 seconds
        self.cache.set("test-token", "query", test_data)
        
        # Wait for expiration
        time.sleep(0.2)
        
        result = self.cache.get("test-token", "query")
        assert result is None

    def test_clear_expired(self):
        """Test clearing expired entries."""
        # Add some entries
        self.cache.set("token1", "query1", {"data": "1"})
        self.cache.set("token2", "query2", {"data": "2"})
        
        # Make one expire
        with patch('time.time', return_value=time.time() + 3700):  # 1 hour later
            expired_count = self.cache.clear_expired()
        
        assert expired_count == 2
        assert len(self.cache.cache) == 0

    def test_clear_expired_no_expired_entries(self):
        """Test clearing expired entries when none are expired."""
        self.cache.set("token", "query", {"data": "test"})
        
        expired_count = self.cache.clear_expired()
        assert expired_count == 0
        assert len(self.cache.cache) == 1

    def test_clear_expired_mixed_entries(self):
        """Test clearing expired entries with mix of expired and valid entries."""
        # Add entries at different times
        current_time = time.time()
        
        # Recent entry (not expired)
        with patch('time.time', return_value=current_time):
            self.cache.set("token1", "query1", {"data": "recent"})
        
        # Old entry (expired) 
        with patch('time.time', return_value=current_time - 3700):  # 1 hour ago
            self.cache.set("token2", "query2", {"data": "old"})
        
        # Clear expired
        with patch('time.time', return_value=current_time):
            expired_count = self.cache.clear_expired()
        
        assert expired_count == 1
        assert len(self.cache.cache) == 1
        
        # Recent entry should still be there
        result = self.cache.get("token1", "query1")
        assert result == {"data": "recent"}

    def test_cache_size_tracking(self):
        """Test cache size tracking in set method."""
        with patch('app.core.cache.logger') as mock_logger:
            self.cache.set("token", "query", {"data": "test"})
            
            # Should log cache size
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "cache size: 1" in log_message

    def test_token_security(self):
        """Test that tokens are hashed for security."""
        # Two different tokens should generate different keys even with same query
        key1 = self.cache._generate_key("token1", "query")
        key2 = self.cache._generate_key("token2", "query")
        
        assert key1 != key2
        
        # Neither key should contain the original token
        assert "token1" not in key1
        assert "token2" not in key2

    def test_multiple_queries_same_token(self):
        """Test multiple queries for the same token."""
        token = "test-token"
        
        self.cache.set(token, "query1", {"data": "result1"})
        self.cache.set(token, "query2", {"data": "result2"})
        
        assert self.cache.get(token, "query1") == {"data": "result1"}
        assert self.cache.get(token, "query2") == {"data": "result2"}
        assert len(self.cache.cache) == 2