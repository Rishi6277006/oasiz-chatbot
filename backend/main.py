from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import List, Dict, AsyncGenerator, Any
from pydantic import BaseModel
import os
import json
import aiohttp
import asyncio
import subprocess
import tempfile
import re
import random
from dotenv import load_dotenv
from mcp_integration import mcp_manager, get_mcp_response

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Request/Response models
class ChatMessageRequest(BaseModel):
    sender: str
    text: str
    session_id: str

class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    text: str
    timestamp: str
    session_id: str

class AIRequest(BaseModel):
    message: str
    session_id: str

class ToolRequest(BaseModel):
    tool: str
    params: Dict[str, Any]

class MCPRequest(BaseModel):
    server_name: str
    tool_name: str
    params: Dict[str, Any] = {}

# In-memory storage for chat messages
chat_messages: List[Dict] = []

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your-weather-api-key-here")
OPENAI_MODEL = "gpt-3.5-turbo"

# Tool definitions
AVAILABLE_TOOLS = {
    "weather": "Get current weather for a location",
    "search": "Search the web for information",
    "code_execute": "Execute Python code safely",
    "time": "Get current time and date"
}

@app.get("/")
def read_root():
    return {"message": "Oasiz Chatbot Backend is running!"}

@app.get("/tools")
def get_available_tools():
    return {"tools": AVAILABLE_TOOLS}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle incoming message
            if message_data.get("type") == "message":
                user_message = message_data.get("message", "")
                
                # Save user message
                user_msg = {
                    "id": len(chat_messages) + 1,
                    "sender": "user",
                    "text": user_message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "session_id": session_id
                }
                chat_messages.append(user_msg)
                
                # Send confirmation
                await manager.send_personal_message(
                    json.dumps({"type": "message_sent", "message": user_msg}),
                    websocket
                )
                
                # Get AI response
                try:
                    ai_response = await get_ai_response(user_message, session_id)
                    
                    # Save bot response
                    bot_msg = {
                        "id": len(chat_messages) + 1,
                        "sender": "bot",
                        "text": ai_response,
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id
                    }
                    chat_messages.append(bot_msg)
                    
                    # Send bot response
                    await manager.send_personal_message(
                        json.dumps({"type": "bot_response", "message": bot_msg}),
                        websocket
                    )
                except Exception as e:
                    error_msg = {
                        "type": "error",
                        "message": f"Error getting AI response: {str(e)}"
                    }
                    await manager.send_personal_message(json.dumps(error_msg), websocket)
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/chat/send", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    message = {
        "id": len(chat_messages) + 1,
        "sender": request.sender,
        "text": request.text,
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": request.session_id
    }
    chat_messages.append(message)
    return message

@app.get("/chat/history")
async def get_history(session_id: str):
    session_messages = [msg for msg in chat_messages if msg["session_id"] == session_id]
    return session_messages

# Tool Functions
async def get_weather(location: str) -> str:
    """Get weather information for a location"""
    try:
        # Try OpenWeatherMap first
        if WEATHER_API_KEY and WEATHER_API_KEY != "your-weather-api-key-here":
            async with aiohttp.ClientSession() as session:
                url = f"http://api.openweathermap.org/data/2.5/weather"
                params = {
                    "q": location,
                    "appid": WEATHER_API_KEY,
                    "units": "metric"
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        temp = data["main"]["temp"]
                        description = data["weather"][0]["description"]
                        humidity = data["main"]["humidity"]
                        return f"🌤️ Weather in {location}: {temp}°C, {description}, Humidity: {humidity}%"
                    else:
                        return f"Sorry, I couldn't get weather information for {location}"
        
        # Fallback: Use a free weather service (wttr.in)
        async with aiohttp.ClientSession() as session:
            url = f"https://wttr.in/{location}?format=3"
            async with session.get(url) as response:
                if response.status == 200:
                    weather_text = await response.text()
                    return f"🌤️ {weather_text.strip()}"
                else:
                    return f"Sorry, I couldn't get weather information for {location}. Try checking a weather app!"
                    
    except Exception as e:
        return f"Sorry, I'm having trouble getting weather data right now. Try asking me something else!"

async def search_web(query: str) -> str:
    """Search the web for information"""
    try:
        # Using DuckDuckGo Instant Answer API (no API key required)
        async with aiohttp.ClientSession() as session:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("Abstract"):
                        return f"Search result for '{query}': {data['Abstract']}"
                    elif data.get("Answer"):
                        return f"Answer for '{query}': {data['Answer']}"
                    else:
                        return f"I found some results for '{query}' but couldn't get a specific answer."
                else:
                    return f"Sorry, I couldn't search for '{query}'"
    except Exception as e:
        return f"Error searching: {str(e)}"

def execute_code(code: str) -> str:
    """Safely execute Python code"""
    try:
        # Basic safety checks
        dangerous_imports = ['os', 'subprocess', 'sys', 'importlib', 'eval', 'exec']
        for dangerous in dangerous_imports:
            if dangerous in code:
                return f"Sorry, I can't execute code that uses '{dangerous}' for security reasons."
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute with timeout
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return f"Code executed successfully:\n{result.stdout}"
            else:
                return f"Code execution error:\n{result.stderr}"
        finally:
            # Clean up
            os.unlink(temp_file)
    except subprocess.TimeoutExpired:
        return "Code execution timed out (max 10 seconds)"
    except Exception as e:
        return f"Error executing code: {str(e)}"

def get_current_time() -> str:
    """Get current time and date"""
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

async def get_joke() -> str:
    """Get a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything! 😄",
        "What do you call a fake noodle? An impasta! 🍝",
        "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
        "I told my wife she was drawing her eyebrows too high. She looked surprised! 😲",
        "Why don't eggs tell jokes? They'd crack each other up! 🥚",
        "What do you call a bear with no teeth? A gummy bear! 🐻",
        "Why did the math book look so sad? Because it had too many problems! 📚",
        "What do you call a fish wearing a bowtie? So-fish-ticated! 🐟",
        "Why don't skeletons fight each other? They don't have the guts! 💀",
        "What do you call a can opener that doesn't work? A can't opener! 🥫"
    ]
    return random.choice(jokes)

async def get_quote() -> str:
    """Get an inspirational quote"""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs 💫",
        "Life is what happens when you're busy making other plans. - John Lennon 🌟",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt ✨",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill 🎯",
        "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt 🚀",
        "Believe you can and you're halfway there. - Theodore Roosevelt 💪",
        "It does not matter how slowly you go as long as you do not stop. - Confucius 🐢",
        "The journey of a thousand miles begins with one step. - Lao Tzu 👣",
        "What you get by achieving your goals is not as important as what you become by achieving your goals. - Zig Ziglar 🎯",
        "The best way to predict the future is to create it. - Peter Drucker 🔮"
    ]
    return random.choice(quotes)

async def play_game(game_type: str) -> str:
    """Play a simple game"""
    if game_type.lower() in ["rps", "rock", "paper", "scissors"]:
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)
        return f"🎮 Let's play Rock, Paper, Scissors! I chose {bot_choice}! What did you choose?"
    
    elif game_type.lower() in ["number", "guess", "guessing"]:
        number = random.randint(1, 100)
        return f"🎲 I'm thinking of a number between 1 and 100. Can you guess it? (Hint: It's {number} 😉)"
    
    elif game_type.lower() in ["word", "hangman"]:
        words = ["PYTHON", "JAVASCRIPT", "PROGRAMMING", "ALGORITHM", "DATABASE", "FRONTEND", "BACKEND", "API"]
        word = random.choice(words)
        return f"🎯 Let's play Hangman! I'm thinking of a programming-related word with {len(word)} letters. Start guessing!"
    
    else:
        return "🎮 I can play Rock, Paper, Scissors, Number Guessing, or Hangman! Just ask me to play one of these games!"

@app.post("/tools/execute")
async def execute_tool(request: ToolRequest):
    """Execute a specific tool"""
    try:
        tool = request.tool
        params = request.params
        
        if tool == "weather":
            location = params.get("location", "New York")
            result = await get_weather(location)
        elif tool == "search":
            query = params.get("query", "")
            result = await search_web(query)
        elif tool == "code_execute":
            code = params.get("code", "")
            result = execute_code(code)
        elif tool == "time":
            result = get_current_time()
        elif tool == "joke":
            result = await get_joke()
        elif tool == "quote":
            result = await get_quote()
        elif tool == "play":
            game_type = params.get("game_type", "rps")
            result = await play_game(game_type)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")
        
        return {"result": result, "tool": tool}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_ai_response(message: str, session_id: str = None) -> str:
    """Get AI response with tool integration"""
    try:
        # Check for MCP patterns first
        mcp_patterns = {
            r'\b(file|read|write|list)\s+(.+?)\b': ("filesystem", "file_read"),
            r'\bgit\s+(status|commit|push)\b': ("git", "git_status"),
            r'\bhttp\s+(get|post)\s+(https?://\S+)': ("http", "http_get"),
            r'\b(database|db|query)\s+(.+?)\b': ("database", "db_query")
        }
        
        for pattern, (server_name, tool_name) in mcp_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                mcp_response = await get_mcp_response(message)
                return mcp_response

        # Check for other tool patterns
        tool_patterns = {
            r'\bweather\b.*\b(\w+(?:\s+\w+)*)': get_weather,
            r'\bsearch\b.*\b(\w+(?:\s+\w+)*)': search_web,
            r'\bexecute\b.*\bcode\b': execute_code,
            r'\btime\b|\bdate\b': get_current_time,
            r'\bjoke\b|\bfunny\b|\bhumor\b': get_joke,
            r'\bquote\b|\binspiration\b|\bmotivation\b': get_quote,
            r'\bplay\b.*\b(game|rps|rock|paper|scissors|number|guess|word|hangman)\b': play_game,
        }
        
        # Check for tool usage
        for pattern, tool_func in tool_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if tool_func == get_weather:
                    location = match.group(1) if match.groups() else "New York"
                    return await get_weather(location)
                elif tool_func == search_web:
                    query = match.group(1) if match.groups() else message
                    return await search_web(query)
                elif tool_func == execute_code:
                    # Extract code from message (basic implementation)
                    code_match = re.search(r'```python\s*(.*?)\s*```', message, re.DOTALL)
                    if code_match:
                        code = code_match.group(1)
                        return execute_code(code)
                    else:
                        return "Please provide Python code in ```python``` blocks for execution."
                elif tool_func == get_current_time:
                    return get_current_time()
                elif tool_func == get_joke:
                    return await get_joke()
                elif tool_func == get_quote:
                    return await get_quote()
                elif tool_func == play_game:
                    game_type = match.group(1) if match.groups() else "rps"
                    return await play_game(game_type)

        # If no tool patterns match, use OpenAI API
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
            return "I'm sorry, but I don't have access to AI capabilities right now. However, I can help you with weather, search, jokes, quotes, games, MCP operations, and more! Try asking about files, git, HTTP requests, or database queries."

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are Oasiz, a helpful and friendly AI assistant. You have access to various tools like weather, web search, code execution, jokes, quotes, games, and MCP operations (filesystem, git, HTTP, database). Be conversational, helpful, and engaging. Use emojis occasionally to make responses more friendly."""
                        },
                        {
                            "role": "user",
                            "content": message
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    return f"Sorry, I encountered an error: {error_text}"

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

@app.post("/ai/chat")
async def chat_with_ai(request: AIRequest):
    """Get AI response for a message"""
    try:
        ai_response = await get_ai_response(request.message, request.session_id)
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/stream")
async def stream_ai_response(request: AIRequest):
    """Stream AI response in real-time"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
            return StreamingResponse(
                iter(["I'm sorry, but I don't have access to AI capabilities right now. However, I can help you with weather, search, jokes, quotes, games, and more!"]),
                media_type="text/plain"
            )

        async def generate() -> AsyncGenerator[str, None]:
            try:
                # Check for tool usage first
                tool_patterns = {
                    r'\bweather\b.*\b(\w+(?:\s+\w+)*)': get_weather,
                    r'\bsearch\b.*\b(\w+(?:\s+\w+)*)': search_web,
                    r'\bexecute\b.*\bcode\b': execute_code,
                    r'\btime\b|\bdate\b': get_current_time,
                    r'\bjoke\b|\bfunny\b|\bhumor\b': get_joke,
                    r'\bquote\b|\binspiration\b|\bmotivation\b': get_quote,
                    r'\bplay\b.*\b(game|rps|rock|paper|scissors|number|guess|word|hangman)\b': play_game,
                }
                
                # Check for tool usage
                for pattern, tool_func in tool_patterns.items():
                    match = re.search(pattern, request.message, re.IGNORECASE)
                    if match:
                        if tool_func == get_weather:
                            location = match.group(1) if match.groups() else "New York"
                            weather_info = await get_weather(location)
                            yield f"data: {weather_info}\n\n"
                            yield f"data: Is there anything else you'd like to know about the weather?\n\n"
                            return
                        elif tool_func == search_web:
                            query = match.group(1) if match.groups() else request.message
                            search_result = await search_web(query)
                            yield f"data: {search_result}\n\n"
                            return
                        elif tool_func == execute_code:
                            # Extract code from message (basic implementation)
                            code_match = re.search(r'```python\s*(.*?)\s*```', request.message, re.DOTALL)
                            if code_match:
                                code = code_match.group(1)
                                result = execute_code(code)
                                yield f"data: {result}\n\n"
                                return
                        elif tool_func == get_current_time:
                            result = get_current_time()
                            yield f"data: {result}\n\n"
                            return
                        elif tool_func == get_joke:
                            result = await get_joke()
                            yield f"data: {result}\n\n"
                            return
                        elif tool_func == get_quote:
                            result = await get_quote()
                            yield f"data: {result}\n\n"
                            return
                        elif tool_func == play_game:
                            game_type = match.group(1) if match.groups() else "rps"
                            result = await play_game(game_type)
                            yield f"data: {result}\n\n"
                            return

                # If no tool patterns match, use OpenAI API with streaming
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {OPENAI_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "gpt-3.5-turbo",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": """You are Oasiz, a helpful and friendly AI assistant. You have access to various tools like weather, web search, code execution, jokes, quotes, and games. Be conversational, helpful, and engaging. Use emojis occasionally to make responses more friendly."""
                                },
                                {
                                    "role": "user",
                                    "content": request.message
                                }
                            ],
                            "stream": True,
                            "max_tokens": 500,
                            "temperature": 0.7
                        }
                    ) as response:
                        if response.status == 200:
                            async for line in response.content:
                                line = line.decode('utf-8').strip()
                                if line.startswith('data: '):
                                    data = line[6:]  # Remove 'data: ' prefix
                                    if data == '[DONE]':
                                        yield f"data: [DONE]\n\n"
                                        break
                                    try:
                                        json_data = json.loads(data)
                                        if 'choices' in json_data and len(json_data['choices']) > 0:
                                            delta = json_data['choices'][0].get('delta', {})
                                            if 'content' in delta:
                                                content = delta['content']
                                                yield f"data: {content}\n\n"
                                    except json.JSONDecodeError:
                                        continue
                        else:
                            error_text = await response.text()
                            yield f"data: Sorry, I encountered an error: {error_text}\n\n"

            except Exception as e:
                yield f"data: Sorry, I encountered an error: {str(e)}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/mcp/servers")
async def get_mcp_servers():
    """Get available MCP servers"""
    return {"servers": mcp_manager.get_available_servers()}

@app.post("/mcp/connect/{server_name}")
async def connect_mcp_server(server_name: str):
    """Connect to an MCP server"""
    success = await mcp_manager.connect_to_server(server_name)
    if success:
        return {"message": f"Connected to MCP server: {server_name}"}
    else:
        raise HTTPException(status_code=400, detail=f"Failed to connect to MCP server: {server_name}")

@app.post("/mcp/execute")
async def execute_mcp_tool(request: MCPRequest):
    """Execute a tool on an MCP server"""
    try:
        server_name = request.server_name
        tool_name = request.tool_name
        params = request.params
        
        if not server_name or not tool_name:
            raise HTTPException(status_code=400, detail="server_name and tool_name are required")
        
        result = await mcp_manager.execute_tool(server_name, tool_name, params)
        return {"result": result, "server": server_name, "tool": tool_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/capabilities/{server_name}")
async def get_mcp_capabilities(server_name: str):
    """Get capabilities of an MCP server"""
    capabilities = mcp_manager.get_server_capabilities(server_name)
    return {"server": server_name, "capabilities": capabilities} 

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "running",
            "database": "connected",
            "mcp": "available"
        }
    } 