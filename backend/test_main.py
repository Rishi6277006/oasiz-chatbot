"""
Test suite for Oasiz Chatbot Backend

This module provides comprehensive testing for all API endpoints,
tool integrations, and MCP functionality as required by the assignment.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

class TestChatEndpoints:
    """Test chat-related endpoints"""
    
    def setup_method(self):
        """Setup test client for each test method"""
        self.client = TestClient(app)
    
    def test_send_message(self):
        """Test sending a message"""
        response = self.client.post("/chat/send", json={
            "message": "Hello, Oasiz!",
            "session_id": "test-session-123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["sender"] == "user"
        assert data["text"] == "Hello, Oasiz!"
    
    def test_get_chat_history(self):
        """Test retrieving chat history"""
        # First send a message
        self.client.post("/chat/send", json={
            "message": "Test message",
            "session_id": "test-session-456"
        })
        
        # Then get history
        response = self.client.get("/chat/history?session_id=test-session-456")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_ai_chat_response(self):
        """Test AI chat response"""
        with patch('main.get_ai_response', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = "Hello! I'm Oasiz, your AI assistant."
            
            response = self.client.post("/ai/chat", json={
                "message": "Hello",
                "session_id": "test-session-789"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert data["response"] == "Hello! I'm Oasiz, your AI assistant."

class TestToolIntegration:
    """Test tool integration endpoints"""
    
    def setup_method(self):
        """Setup test client for each test method"""
        self.client = TestClient(app)
    
    @patch('main.get_weather')
    def test_weather_tool(self, mock_weather):
        """Test weather tool execution"""
        mock_weather.return_value = "🌤️ Weather in New York: 72°F, Partly Cloudy"
        
        response = self.client.post("/tools/execute", json={
            "tool": "weather",
            "params": {"location": "New York"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "New York" in data["result"]
    
    @patch('main.search_web')
    def test_search_tool(self, mock_search):
        """Test web search tool execution"""
        mock_search.return_value = "Search results for 'Python programming'..."
        
        response = self.client.post("/tools/execute", json={
            "tool": "search",
            "params": {"query": "Python programming"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "Python programming" in data["result"]
    
    def test_code_execution_tool(self):
        """Test code execution tool"""
        response = self.client.post("/tools/execute", json={
            "tool": "code_execute",
            "params": {"code": "print('Hello, World!')"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "Hello, World!" in data["result"]
    
    def test_time_tool(self):
        """Test time tool execution"""
        response = self.client.post("/tools/execute", json={
            "tool": "time",
            "params": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "current time" in data["result"].lower()
    
    @patch('main.get_joke')
    def test_joke_tool(self, mock_joke):
        """Test joke tool execution"""
        mock_joke.return_value = "Why don't scientists trust atoms? Because they make up everything! 😄"
        
        response = self.client.post("/tools/execute", json={
            "tool": "joke",
            "params": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "atoms" in data["result"]
    
    @patch('main.get_quote')
    def test_quote_tool(self, mock_quote):
        """Test quote tool execution"""
        mock_quote.return_value = "The only way to do great work is to love what you do. - Steve Jobs ✨"
        
        response = self.client.post("/tools/execute", json={
            "tool": "quote",
            "params": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "Steve Jobs" in data["result"]

class TestMCPIntegration:
    """Test MCP (Model Context Protocol) integration"""
    
    def setup_method(self):
        """Setup test client for each test method"""
        self.client = TestClient(app)
    
    def test_get_mcp_servers(self):
        """Test getting available MCP servers"""
        response = self.client.get("/mcp/servers")
        assert response.status_code == 200
        data = response.json()
        assert "servers" in data
        assert isinstance(data["servers"], list)
        assert len(data["servers"]) > 0
    
    def test_connect_mcp_server(self):
        """Test connecting to MCP server"""
        response = self.client.post("/mcp/connect/filesystem")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Connected to MCP server" in data["message"]
    
    def test_execute_mcp_tool(self):
        """Test executing MCP tool"""
        response = self.client.post("/mcp/execute", json={
            "params": {
                "server_name": "filesystem",
                "tool_name": "file_read",
                "params": {"path": "/test/file.txt"}
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "server" in data
        assert "tool" in data
    
    def test_get_mcp_capabilities(self):
        """Test getting MCP server capabilities"""
        response = self.client.get("/mcp/capabilities/filesystem")
        assert response.status_code == 200
        data = response.json()
        assert "server" in data
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)

class TestStreamingEndpoints:
    """Test streaming response endpoints"""
    
    def setup_method(self):
        """Setup test client for each test method"""
        self.client = TestClient(app)
    
    def test_stream_ai_response(self):
        """Test streaming AI response"""
        with patch('main.get_ai_response', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = "Streaming response test"
            
            response = self.client.post("/ai/stream", json={
                "message": "Test streaming",
                "session_id": "test-stream-123"
            })
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def setup_method(self):
        """Setup test client for each test method"""
        self.client = TestClient(app)
    
    def test_invalid_session_id(self):
        """Test handling of invalid session ID"""
        response = self.client.get("/chat/history?session_id=")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_empty_message(self):
        """Test handling of empty message"""
        response = self.client.post("/chat/send", json={
            "message": "",
            "session_id": "test-empty-123"
        })
        assert response.status_code == 200
    
    def test_missing_parameters(self):
        """Test handling of missing parameters"""
        response = self.client.post("/chat/send", json={
            "session_id": "test-missing-123"
        })
        assert response.status_code == 422  # Validation error
    
    def test_invalid_tool(self):
        """Test handling of invalid tool"""
        response = self.client.post("/tools/execute", json={
            "tool": "invalid_tool",
            "params": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert "error" in data["result"]

class TestPerformance:
    """Test performance and response times"""
    
    def setup_method(self):
        """Setup test client for each test method"""
        self.client = TestClient(app)
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = self.client.post("/chat/send", json={
                "message": "Concurrent test",
                "session_id": f"concurrent-{threading.get_ident()}"
            })
            results.append(response.status_code)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert all(status == 200 for status in results)
    
    def test_response_time(self):
        """Test response time is reasonable"""
        import time
        
        start_time = time.time()
        response = self.client.get("/mcp/servers")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second

class TestSecurity:
    """Test security features"""
    
    def setup_method(self):
        """Setup test client for each test method"""
        self.client = TestClient(app)
    
    def test_code_execution_safety(self):
        """Test that code execution is safe"""
        dangerous_code = "import os; os.system('rm -rf /')"
        
        response = self.client.post("/tools/execute", json={
            "tool": "code_execute",
            "params": {"code": dangerous_code}
        })
        
        assert response.status_code == 200
        data = response.json()
        # Should not actually execute dangerous code
        assert "error" in data["result"] or "security" in data["result"].lower()
    
    def test_input_validation(self):
        """Test input validation"""
        # Test very long message
        long_message = "A" * 10000
        
        response = self.client.post("/chat/send", json={
            "message": long_message,
            "session_id": "test-long-123"
        })
        
        assert response.status_code == 200  # Should handle gracefully

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 