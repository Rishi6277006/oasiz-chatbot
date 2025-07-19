<script lang="ts">
  import { afterUpdate, onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  let messages: { sender: 'user' | 'bot'; text: string; time: string }[] = [
    { sender: 'bot', text: 'Hello! I am Oasiz, your chatbot assistant. How can I help you today?', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  ];
  let input = '';
  let chatHistoryDiv: HTMLDivElement | null = null;
  let sessionId = crypto.randomUUID();
  let isLoading = false;
  let currentUser = null;
  let showUserMenu = false;
  let botMood = 'happy'; // Add bot mood tracking
  let showConfetti = false; // Add confetti for special moments
  let isListening = false; // Voice recognition state
  let recognition: any = null; // Speech recognition
  let currentTheme = 'light'; // Theme state
  let isThemeChanging = false; // Theme changing state

  onMount(() => {
    // Check if user is logged in
    const savedUser = localStorage.getItem('oasiz_user');
    if (!savedUser) {
      goto('/');
      return;
    }
    currentUser = JSON.parse(savedUser);
    
    // Load saved theme
    const savedTheme = localStorage.getItem('oasiz_theme');
    if (savedTheme) {
      currentTheme = savedTheme;
      applyTheme(savedTheme);
    } else {
      // Set default theme
      applyTheme('light');
    }
    
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        input = transcript;
        isListening = false;
        sendMessage();
      };
      
      recognition.onerror = () => {
        isListening = false;
      };
      
      recognition.onend = () => {
        isListening = false;
      };
    }
    
    // Load chat history
    loadChatHistory();
  });

  // Load chat history on page load
  async function loadChatHistory() {
    try {
      const response = await fetch(`http://127.0.0.1:8000/chat/history?session_id=${sessionId}`);
      if (response.ok) {
        const history = await response.json();
        if (history.length > 0) {
          messages = history.map((msg: any) => ({
            sender: msg.sender as 'user' | 'bot',
            text: msg.text,
            time: new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }));
        }
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  }

  async function sendMessage() {
    if (input.trim() && !isLoading) {
      isLoading = true;
      const userMessage = input.trim();
      input = '';
      
      // Play message sound
      playSound('message');
      
      // Update bot mood based on user message
      updateBotMood(userMessage);
      
      console.log('Sending message:', userMessage);
      
      // Add user message immediately
      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      messages = [...messages, { sender: 'user', text: userMessage, time: now }];
      
      try {
        // Send message to backend
        console.log('Sending to backend...');
        const response = await fetch('http://127.0.0.1:8000/chat/send', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            sender: 'user',
            text: userMessage,
            session_id: sessionId
          })
        });
        
        console.log('Backend response status:', response.status);
        
        if (response.ok) {
          console.log('Message sent successfully, getting AI response...');
          
          try {
            // Get AI response
            const aiResponse = await fetch('http://127.0.0.1:8000/ai/chat', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                message: userMessage,
                session_id: sessionId
              })
            });
            
            if (aiResponse.ok) {
              const aiData = await aiResponse.json();
              const botResponse = aiData.response;
              messages = [...messages, { sender: 'bot', text: botResponse, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }];
              
              // Play success sound for bot response
              playSound('success');
              
              // Trigger confetti for special responses
              if (botResponse.includes('😄') || botResponse.includes('🎉') || botResponse.includes('🎮')) {
                triggerConfetti();
              }
              
              // Save bot response to backend
              try {
                await fetch('http://127.0.0.1:8000/chat/send', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    sender: 'bot',
                    text: botResponse,
                    session_id: sessionId
                  })
                });
                console.log('AI response saved to backend');
              } catch (error) {
                console.error('Failed to save AI response:', error);
              }
            } else {
              // Fallback to demo response if AI fails
              console.log('AI failed, using demo response');
              const botResponse = "Thanks for your message! I'm a demo chatbot. In the full version, I'll have AI capabilities to help you with various tasks.";
              messages = [...messages, { sender: 'bot', text: botResponse, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }];
              
              // Save bot response to backend
              try {
                await fetch('http://127.0.0.1:8000/chat/send', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    sender: 'bot',
                    text: botResponse,
                    session_id: sessionId
                  })
                });
              } catch (error) {
                console.error('Failed to save bot response:', error);
              }
            }
          } catch (error) {
            console.error('Failed to get AI response:', error);
            // Fallback to demo response
            const botResponse = "Thanks for your message! I'm a demo chatbot. In the full version, I'll have AI capabilities to help you with various tasks.";
            messages = [...messages, { sender: 'bot', text: botResponse, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }];
          }
        } else {
          console.error('Backend returned error status:', response.status);
          messages = [...messages, { sender: 'bot', text: 'Sorry, I encountered an error. Please try again.', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }];
        }
      } catch (error) {
        console.error('Failed to send message:', error);
        messages = [...messages, { sender: 'bot', text: 'Sorry, I encountered an error. Please try again.', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }];
      } finally {
        isLoading = false;
      }
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function logout() {
    localStorage.removeItem('oasiz_user');
    goto('/');
  }

  function goHome() {
    goto('/');
  }

  afterUpdate(() => {
    if (chatHistoryDiv) {
      chatHistoryDiv.scrollTo({ top: chatHistoryDiv.scrollHeight, behavior: 'smooth' });
    }
  });

  // Function to determine bot mood based on message content
  function updateBotMood(message: string) {
    const happyWords = ['joke', 'funny', 'laugh', 'happy', 'great', 'awesome', 'love', 'thanks', 'thank you'];
    const excitedWords = ['play', 'game', 'win', 'cool', 'amazing', 'wow'];
    const thinkingWords = ['how', 'why', 'what', 'explain', 'help', 'problem'];
    const calmWords = ['weather', 'time', 'search', 'find'];
    
    const lowerMessage = message.toLowerCase();
    
    if (happyWords.some(word => lowerMessage.includes(word))) {
      botMood = 'happy';
    } else if (excitedWords.some(word => lowerMessage.includes(word))) {
      botMood = 'excited';
    } else if (thinkingWords.some(word => lowerMessage.includes(word))) {
      botMood = 'thinking';
    } else if (calmWords.some(word => lowerMessage.includes(word))) {
      botMood = 'calm';
    } else {
      botMood = 'neutral';
    }
  }

  // Function to trigger confetti for special moments
  function triggerConfetti() {
    showConfetti = true;
    setTimeout(() => showConfetti = false, 3000);
  }

  // Function to start voice recognition
  function startVoiceRecognition() {
    if (recognition && !isListening) {
      isListening = true;
      recognition.start();
    }
  }

  // Function to play sound effects
  function playSound(type: 'message' | 'notification' | 'success') {
    const audio = new Audio();
    audio.volume = 0.3;
    
    switch (type) {
      case 'message':
        // Create a simple beep sound
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
        break;
        
      case 'notification':
        // Higher pitch for notifications
        const audioContext2 = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator2 = audioContext2.createOscillator();
        const gainNode2 = audioContext2.createGain();
        
        oscillator2.connect(gainNode2);
        gainNode2.connect(audioContext2.destination);
        
        oscillator2.frequency.setValueAtTime(1200, audioContext2.currentTime);
        gainNode2.gain.setValueAtTime(0.1, audioContext2.currentTime);
        
        oscillator2.start(audioContext2.currentTime);
        oscillator2.stop(audioContext2.currentTime + 0.15);
        break;
        
      case 'success':
        // Success sound (ascending notes)
        const audioContext3 = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator3 = audioContext3.createOscillator();
        const gainNode3 = audioContext3.createGain();
        
        oscillator3.connect(gainNode3);
        gainNode3.connect(audioContext3.destination);
        
        oscillator3.frequency.setValueAtTime(523, audioContext3.currentTime);
        oscillator3.frequency.setValueAtTime(659, audioContext3.currentTime + 0.1);
        oscillator3.frequency.setValueAtTime(784, audioContext3.currentTime + 0.2);
        
        gainNode3.gain.setValueAtTime(0.1, audioContext3.currentTime);
        
        oscillator3.start(audioContext3.currentTime);
        oscillator3.stop(audioContext3.currentTime + 0.3);
        break;
    }
  }

  // Function to apply theme
  function applyTheme(theme: string) {
    const root = document.documentElement;
    
    switch (theme) {
      case 'light':
        root.style.setProperty('--bg-color', '#f7f6f3');
        root.style.setProperty('--text-color', '#2a2a2a');
        root.style.setProperty('--glass-bg', 'rgba(255,255,255,0.65)');
        root.style.setProperty('--primary-color', '#667eea');
        root.style.setProperty('--secondary-color', '#764ba2');
        root.style.setProperty('--accent-color', '#c9d6ff');
        root.style.setProperty('--border-color', 'rgba(0,0,0,0.05)');
        break;
      case 'dark':
        root.style.setProperty('--bg-color', '#1a1a2e');
        root.style.setProperty('--text-color', '#ffffff');
        root.style.setProperty('--glass-bg', 'rgba(255,255,255,0.1)');
        root.style.setProperty('--primary-color', '#8b5cf6');
        root.style.setProperty('--secondary-color', '#6366f1');
        root.style.setProperty('--accent-color', '#4c1d95');
        root.style.setProperty('--border-color', 'rgba(255,255,255,0.1)');
        break;
      default:
        root.style.setProperty('--bg-color', '#f7f6f3');
        root.style.setProperty('--text-color', '#2a2a2a');
        root.style.setProperty('--glass-bg', 'rgba(255,255,255,0.65)');
        root.style.setProperty('--primary-color', '#667eea');
        root.style.setProperty('--secondary-color', '#764ba2');
        root.style.setProperty('--accent-color', '#c9d6ff');
        root.style.setProperty('--border-color', 'rgba(0,0,0,0.05)');
    }
  }

  // Function to change theme
  function changeTheme(theme: string) {
    if (isThemeChanging) return; // Prevent rapid clicks
    isThemeChanging = true;
    currentTheme = theme;
    localStorage.setItem('oasiz_theme', theme);
    applyTheme(theme);
    setTimeout(() => {
      isThemeChanging = false;
    }, 500); // Prevent rapid clicks for 500ms
  }
</script>

<style>
  :global(body) {
    min-height: 100vh;
    margin: 0;
    font-family: 'Inter', 'Georgia', serif;
    color: var(--text-color, #222);
    background: var(--bg-color, #f7f6f3);
    position: relative;
    overflow-x: hidden;
    transition: background-color 0.3s ease, color 0.3s ease;
  }
  
  .chat-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    background: var(--glass-bg, rgba(255,255,255,0.65));
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-color, rgba(0,0,0,0.05));
    border-radius: 2rem 2rem 0 0;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
  }
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .logo {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary-color, #667eea) 0%, var(--secondary-color, #764ba2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    transition: transform 0.2s ease;
    cursor: default;
  }

  .logo:hover {
    transform: scale(1.05);
  }
  
  .subtitle {
    font-size: 0.9rem;
    color: #666;
    font-weight: 400;
    margin-top: 0.2rem;
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .user-avatar {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-color, #667eea) 0%, var(--secondary-color, #764ba2) 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    border: none;
    outline: none;
  }
  
  .user-avatar:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
  
  .user-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border-radius: 1rem;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    padding: 0.5rem;
    min-width: 150px;
    z-index: 1000;
    border: 1px solid rgba(0, 0, 0, 0.05);
  }
  
  .user-menu button {
    width: 100%;
    padding: 0.7rem 1rem;
    border: none;
    background: none;
    text-align: left;
    cursor: pointer;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    color: #333;
    transition: background 0.2s ease;
  }
  
  .user-menu button:hover {
    background: #f5f5f5;
  }
  
  .main-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }
  
  .bg-art {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: 0;
    background: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80') center center / cover no-repeat;
    filter: blur(10px) brightness(0.85);
    transition: filter 0.5s;
  }
  
  .bg-overlay {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: 1;
    background: linear-gradient(120deg, rgba(255,255,255,0.7) 0%, rgba(240,240,255,0.5) 100%);
    pointer-events: none;
  }
  
  .centered-container {
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 800px;
  }
  
  .chat-glass {
    backdrop-filter: blur(16px) saturate(1.2);
    background: var(--glass-bg, rgba(255,255,255,0.65));
    border-radius: 2rem;
    box-shadow: 0 8px 40px 0 rgba(60,60,90,0.13), 0 1.5px 8px 0 rgba(60,60,90,0.07);
    width: 100%;
    min-height: 70vh;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    padding: 2.2rem 1.5rem 1.2rem 1.5rem;
    animation: fadeIn 1.1s cubic-bezier(.4,0,.2,1);
  }
  
  .title {
    font-family: 'Georgia', serif;
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    margin-bottom: 0.2rem;
    text-align: center;
    color: #2d2d2d;
    text-shadow: 0 2px 8px rgba(255,255,255,0.3);
  }
  
  .subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1.08rem;
    color: #5a5a6e;
    text-align: center;
    margin-bottom: 1.5rem;
    letter-spacing: 0.01em;
  }
  
  .chat-history {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    margin-bottom: 1.2rem;
    padding-right: 0.2rem;
    scroll-behavior: smooth;
    padding-bottom: 0.5rem;
  }
  
  .msg-row {
    display: flex;
    align-items: flex-end;
    margin-bottom: 0.2rem;
  }
  
  .msg-row.user {
    flex-direction: row-reverse;
  }
  
  .avatar {
    width: 2.2rem;
    height: 2.2rem;
    border-radius: 50%;
    background: linear-gradient(135deg, #c9d6ff 0%, #e2e2e2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 0.7rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    font-family: 'Georgia', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #4a3c2b;
    overflow: hidden;
  }
  
  .avatar.bot {
    background: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=100&q=80') center center / cover no-repeat;
    color: transparent;
    border: 2px solid #f3e9e1;
    position: relative;
    overflow: hidden;
  }
  
  .avatar.bot::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60%;
    height: 60%;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    transition: all 0.3s ease;
  }
  
  .avatar.bot.happy::before {
    content: '😊';
    animation: bounce 0.6s ease;
  }
  
  .avatar.bot.excited::before {
    content: '🤩';
    animation: pulse 0.8s ease;
  }
  
  .avatar.bot.thinking::before {
    content: '🤔';
    animation: rotate 2s linear infinite;
  }
  
  .avatar.bot.calm::before {
    content: '😌';
    animation: float 3s ease-in-out infinite;
  }
  
  .avatar.bot.neutral::before {
    content: '😐';
  }
  
  .avatar.user {
    background: linear-gradient(135deg, #e0e7ef 0%, #c9d6ff 100%);
    color: #2a2a2a;
    border: 2px solid #c9d6ff;
  }
  
  .message.user {
    border-radius: 1.3rem 1.3rem 0.5rem 1.3rem;
    margin-left: 2.5rem;
    margin-right: 0;
    background: linear-gradient(90deg, var(--accent-color) 0%, var(--primary-color) 100%);
    color: var(--text-color);
  }
  
  .message.bot {
    margin-right: 2.5rem;
    margin-left: 0;
    background: linear-gradient(90deg, var(--glass-bg) 0%, rgba(255,255,255,0.8) 100%);
    color: var(--text-color);
  }
  
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translate(-50%, -50%) scale(1); }
    40% { transform: translate(-50%, -50%) scale(1.1); }
    60% { transform: translate(-50%, -50%) scale(1.05); }
  }
  
  @keyframes pulse {
    0% { transform: translate(-50%, -50%) scale(1); }
    50% { transform: translate(-50%, -50%) scale(1.2); }
    100% { transform: translate(-50%, -50%) scale(1); }
  }
  
  @keyframes rotate {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
  }
  
  @keyframes float {
    0%, 100% { transform: translate(-50%, -50%) translateY(0px); }
    50% { transform: translate(-50%, -50%) translateY(-5px); }
  }
  
  /* Confetti styles */
  .confetti-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1000;
  }
  
  .confetti {
    position: absolute;
    width: 10px;
    height: 10px;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
    animation: confetti-fall 3s linear forwards;
  }
  
  @keyframes confetti-fall {
    0% {
      transform: translateY(-100vh) rotate(0deg);
      opacity: 1;
    }
    100% {
      transform: translateY(100vh) rotate(720deg);
      opacity: 0;
    }
  }
  
  /* Enhanced message animations */
  .message {
    max-width: 80%;
    padding: 0.95rem 1.3rem;
    border-radius: 1.3rem 1.3rem 1.3rem 0.5rem;
    font-size: 1.08rem;
    line-height: 1.5;
    word-break: break-word;
    box-shadow: 0 2px 12px rgba(60,60,90,0.07);
    opacity: 0;
    animation: slideInMessage 0.6s forwards;
    position: relative;
    margin-bottom: 0.1rem;
    transition: box-shadow 0.2s, background 0.2s, transform 0.2s;
  }
  
  .message:hover {
    box-shadow: 0 4px 18px rgba(60,60,90,0.13);
    background: #f7f6f3;
    transform: translateY(-2px);
  }
  
  @keyframes slideInMessage {
    from { 
      opacity: 0; 
      transform: translateY(20px) scale(0.95); 
    }
    to { 
      opacity: 1; 
      transform: translateY(0) scale(1); 
    }
  }
  
  /* Interactive typing indicator */
  .typing-indicator {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.5rem 1rem;
    color: #666;
    font-style: italic;
    animation: typing-pulse 1.5s ease-in-out infinite;
  }
  
  @keyframes typing-pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
  }
  
  /* Quick Action Buttons */
  .quick-actions {
    position: fixed;
    bottom: 120px;
    right: 20px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    z-index: 100;
  }
  
  .quick-btn {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: 1rem;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
  }

  .quick-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    background: rgba(255, 255, 255, 0.8);
  }

  .quick-btn:active {
    transform: translateY(0);
  }
  
  .timestamp {
    font-size: 0.75rem;
    color: #aaa;
    margin-top: 0.2rem;
    text-align: right;
    padding-right: 0.2rem;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.01em;
  }
  
  .chat-input {
    display: flex;
    background: var(--glass-bg);
    border-radius: 1rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.03);
    padding: 0.5rem 0.5rem 0.5rem 1rem;
    align-items: center;
    border: 1.5px solid var(--border-color);
    transition: box-shadow 0.2s, border 0.2s;
  }
  
  .chat-input:focus-within {
    box-shadow: 0 2px 12px rgba(120,120,180,0.10);
    border: 1.5px solid var(--accent-color);
  }
  
  .chat-input input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 1.08rem;
    padding: 0.8rem;
    border-radius: 0.7rem;
    background: transparent;
    font-family: inherit;
    color: var(--text-color);
  }
  
  .chat-input input::placeholder {
    color: #aaa;
    opacity: 1;
  }
  
  .chat-input button {
    background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: white;
    border: none;
    border-radius: 0.7rem;
    padding: 0.8rem 1.3rem;
    font-size: 1.08rem;
    cursor: pointer;
    font-family: inherit;
    transition: background 0.2s, box-shadow 0.2s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    margin-left: 0.5rem;
  }
  
  .chat-input button:hover:not(:disabled) {
    background: linear-gradient(90deg, var(--secondary-color) 0%, var(--primary-color) 100%);
    box-shadow: 0 2px 8px rgba(120,120,180,0.10);
  }
  
  .chat-input button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .typing-dots {
    display: flex;
    gap: 0.2rem;
  }
  
  .typing-dot {
    width: 0.4rem;
    height: 0.4rem;
    border-radius: 50%;
    background: #999;
    animation: typing 1.4s infinite ease-in-out;
  }
  
  .typing-dot:nth-child(1) { animation-delay: -0.32s; }
  .typing-dot:nth-child(2) { animation-delay: -0.16s; }
  
  @keyframes typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: none; }
  }

  .voice-btn {
    background: linear-gradient(90deg, #c9d6ff 0%, #e2e2e2 100%);
    color: #333;
    border: none;
    border-radius: 0.7rem;
    padding: 0.8rem 1.3rem;
    font-size: 1.08rem;
    cursor: pointer;
    font-family: inherit;
    transition: background 0.2s, box-shadow 0.2s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    margin-left: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px; /* Fixed width for the button */
    height: 40px; /* Fixed height for the button */
    min-width: 40px; /* Ensure it doesn't shrink */
    min-height: 40px; /* Ensure it doesn't shrink */
    border-radius: 50%; /* Make it a circle */
    background-color: #e2e2e2; /* Default background */
    color: #666; /* Default color */
  }

  .voice-btn:hover:not(:disabled) {
    background: linear-gradient(90deg, #b7c6e6 0%, #e2e2e2 100%);
    box-shadow: 0 2px 8px rgba(120,120,180,0.10);
  }

  .voice-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Theme Switcher Styles */
  .theme-switcher {
    display: flex;
    gap: 0.2rem;
    background: var(--glass-bg);
    border-radius: 12px;
    padding: 0.3rem;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
  }

  .theme-btn {
    background: none;
    border: none;
    font-size: 0.8rem;
    cursor: pointer;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    color: var(--text-color);
    font-weight: 500;
    min-width: 60px;
    position: relative;
    overflow: hidden;
  }

  .theme-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    color: var(--text-color);
    transform: translateY(-1px);
  }

  .theme-btn.active {
    background: var(--primary-color);
    color: white;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    transform: translateY(-1px);
  }

  .theme-btn:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }

  .theme-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .theme-btn:disabled::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 12px;
    height: 12px;
    margin: -6px 0 0 -6px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .message-container {
    flex: 1;
  }
  
  .timestamp {
    font-size: 0.75rem;
    color: #aaa;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.01em;
    margin-top: 0.2rem;
    text-align: right;
    padding-right: 0.2rem;
  }
  
  @media (max-width: 768px) {
    .header {
      padding: 1rem;
    }
    
    .main-content {
      padding: 1rem;
    }
    
    .chat-glass {
      padding: 1.2rem 0.2rem 0.7rem 0.2rem;
    }
    
    .title {
      font-size: 1.4rem;
    }
    
    .subtitle {
      font-size: 0.98rem;
    }
    
    .avatar {
      width: 1.7rem;
      height: 1.7rem;
      font-size: 0.9rem;
      margin: 0 0.3rem;
    }
    
    .message {
      font-size: 0.98rem;
      padding: 0.7rem 1rem;
    }
    
    .msg-row {
      margin-bottom: 0.1rem;
    }

    .quick-actions {
      bottom: 100px;
      right: 10px;
    }
    
    .quick-btn {
      padding: 0.4rem 0.8rem;
      font-size: 0.8rem;
    }
  }
</style>

<div class="chat-page">
  <!-- Header -->
  <header class="header">
    <div class="header-left">
      <div>
        <div class="logo">Oasiz</div>
        <div class="subtitle">Your AI Companion</div>
      </div>
    </div>
    <div class="header-right">
      <div class="theme-switcher">
        <button class="theme-btn" on:click={() => changeTheme('light')} class:active={currentTheme === 'light'} disabled={isThemeChanging}>Light</button>
        <button class="theme-btn" on:click={() => changeTheme('dark')} class:active={currentTheme === 'dark'} disabled={isThemeChanging}>Dark</button>
      </div>
      <div class="user-info" style="position: relative;">
        <button 
          class="user-avatar" 
          on:click={() => showUserMenu = !showUserMenu}
          on:keydown={(e) => e.key === 'Enter' && (showUserMenu = !showUserMenu)}
          aria-label="User menu"
          aria-expanded={showUserMenu}
          aria-haspopup="true"
        >
          {currentUser?.name?.charAt(0)?.toUpperCase() || 'U'}
        </button>
        {#if showUserMenu}
          <div class="user-menu" role="menu">
            <button role="menuitem">Welcome, {currentUser?.name}!</button>
            <button role="menuitem" on:click={logout}>Logout</button>
          </div>
        {/if}
      </div>
    </div>
  </header>
  
  <!-- Main Content -->
  <main class="main-content">
    <div class="bg-art"></div>
    <div class="bg-overlay"></div>
    <div class="centered-container">
      <div class="chat-glass">
        <div class="title">Oasiz Chatbot</div>
        <div class="subtitle">A creative, conversational assistant</div>
        <div class="chat-history" bind:this={chatHistoryDiv}>
          {#each messages as msg, i (i)}
            <div class="msg-row {msg.sender}">
              <div class="avatar {msg.sender} {msg.sender === 'bot' ? botMood : ''}">{msg.sender === 'user' ? 'U' : ''}</div>
              <div class="message-container">
                <div class="message {msg.sender}">{msg.text}</div>
                <div class="timestamp">{msg.time}</div>
              </div>
            </div>
          {/each}
          {#if isLoading}
            <div class="msg-row bot">
              <div class="avatar bot thinking"></div>
              <div>
                <div class="typing-indicator">
                  Oasiz is typing
                  <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                  </div>
                </div>
              </div>
            </div>
          {/if}
        </div>
        <form class="chat-input" on:submit|preventDefault={sendMessage}>
          <input
            type="text"
            bind:value={input}
            placeholder="Type your message..."
            on:keydown={handleKeydown}
            autocomplete="off"
            disabled={isLoading}
          />
          <button 
            type="button" 
            class="voice-btn" 
            on:click={startVoiceRecognition}
            disabled={isLoading || !recognition}
            title="Voice input"
          >
            {isListening ? '🎤' : '🎙️'}
          </button>
          <button type="submit" aria-label="Send" disabled={isLoading || !input.trim()}>
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  </main>
</div>

<!-- Confetti Effect -->
{#if showConfetti}
  <div class="confetti-container">
    {#each Array(50) as _, i}
      <div 
        class="confetti" 
        style="
          left: {Math.random() * 100}%; 
          animation-delay: {Math.random() * 2}s;
          animation-duration: {2 + Math.random() * 2}s;
        "
      ></div>
    {/each}
  </div>
{/if}

<!-- Quick Action Buttons -->
<div class="quick-actions">
  <button class="quick-btn" on:click={() => { input = 'tell me a joke'; sendMessage(); }}>😄 Joke</button>
  <button class="quick-btn" on:click={() => { input = 'give me inspiration'; sendMessage(); }}>✨ Quote</button>
  <button class="quick-btn" on:click={() => { input = 'play a game'; sendMessage(); }}>🎮 Game</button>
  <button class="quick-btn" on:click={() => { input = 'what time is it'; sendMessage(); }}>⏰ Time</button>
</div> 