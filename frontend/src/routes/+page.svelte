<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  
  let isLoggedIn = false;
  let showLogin = false;
  let showSignup = false;
  let currentUser = null;
  
  // Form data
  let loginData = { email: '', password: '' };
  let signupData = { name: '', email: '', password: '', confirmPassword: '' };
  
  // Animation states
  let animateIn = false;
  
  onMount(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('oasiz_user');
    if (savedUser) {
      currentUser = JSON.parse(savedUser);
      isLoggedIn = true;
    }
    
    // Start animations
    setTimeout(() => animateIn = true, 100);
  });
  
  function handleLogin() {
    // Simple validation
    if (!loginData.email || !loginData.password) {
      alert('Please fill in all fields');
      return;
    }
    
    // Simulate login (in real app, this would call your backend)
    currentUser = {
      name: loginData.email.split('@')[0],
      email: loginData.email
    };
    localStorage.setItem('oasiz_user', JSON.stringify(currentUser));
    isLoggedIn = true;
    showLogin = false;
  }
  
  function handleSignup() {
    // Simple validation
    if (!signupData.name || !signupData.email || !signupData.password) {
      alert('Please fill in all fields');
      return;
    }
    
    if (signupData.password !== signupData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    
    // Simulate signup (in real app, this would call your backend)
    currentUser = {
      name: signupData.name,
      email: signupData.email
    };
    localStorage.setItem('oasiz_user', JSON.stringify(currentUser));
    isLoggedIn = true;
    showSignup = false;
  }
  
  function logout() {
    localStorage.removeItem('oasiz_user');
    currentUser = null;
    isLoggedIn = false;
  }
  
  function goToChat() {
    goto('/chat');
  }
</script>

<style>
  :global(body) {
    min-height: 100vh;
    margin: 0;
    font-family: 'Inter', 'Georgia', serif;
    color: #222;
    background: #f7f6f3;
    position: relative;
    overflow-x: hidden;
  }
  
  .landing-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
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
    max-width: 900px;
    padding: 2rem;
  }
  
  .hero-glass {
    backdrop-filter: blur(16px) saturate(1.2);
    background: rgba(255,255,255,0.65);
    border-radius: 2rem;
    box-shadow: 0 8px 40px 0 rgba(60,60,90,0.13), 0 1.5px 8px 0 rgba(60,60,90,0.07);
    width: 100%;
    padding: 3rem 2rem;
    text-align: center;
    animation: fadeIn 1.1s cubic-bezier(.4,0,.2,1);
  }
  
  .hero-title {
    font-family: 'Georgia', serif;
    font-size: 3.5rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    margin-bottom: 0.5rem;
    color: #2d2d2d;
    text-shadow: 0 2px 8px rgba(255,255,255,0.3);
  }
  
  .hero-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1.3rem;
    color: #5a5a6e;
    margin-bottom: 2.5rem;
    letter-spacing: 0.01em;
  }
  
  .cta-buttons {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    margin-bottom: 3rem;
  }
  
  .btn {
    padding: 1rem 2.5rem;
    border: none;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
    font-family: inherit;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }
  
  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  }
  
  .btn-secondary {
    background: rgba(255, 255, 255, 0.9);
    color: #667eea;
    border: 2px solid #667eea;
  }
  
  .btn-secondary:hover {
    background: #667eea;
    color: white;
    transform: translateY(-2px);
  }
  
  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
  }
  
  .feature-card {
    backdrop-filter: blur(16px) saturate(1.2);
    background: rgba(255,255,255,0.45);
    padding: 2rem;
    border-radius: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px 0 rgba(60,60,90,0.08), 0 1px 4px 0 rgba(60,60,90,0.04);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid rgba(255,255,255,0.2);
  }
  
  .feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px 0 rgba(60,60,90,0.15), 0 2px 8px 0 rgba(60,60,90,0.08);
  }
  
  .feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .feature-title {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #333;
    font-family: 'Georgia', serif;
  }
  
  .feature-description {
    color: #666;
    line-height: 1.6;
    font-size: 1rem;
  }
  
  .user-welcome {
    backdrop-filter: blur(16px) saturate(1.2);
    background: rgba(255,255,255,0.65);
    padding: 2rem;
    border-radius: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px 0 rgba(60,60,90,0.08), 0 1px 4px 0 rgba(60,60,90,0.04);
    border: 1px solid rgba(255,255,255,0.2);
  }
  
  .welcome-text {
    font-size: 1.3rem;
    color: #333;
    margin-bottom: 1rem;
    font-weight: 600;
  }
  
  .user-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }
  
  /* Modal styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(5px);
  }
  
  .modal {
    backdrop-filter: blur(16px) saturate(1.2);
    background: rgba(255,255,255,0.9);
    padding: 2.5rem;
    border-radius: 1.5rem;
    width: 90%;
    max-width: 450px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255,255,255,0.2);
  }
  
  .modal-title {
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 2rem;
    text-align: center;
    color: #333;
    font-family: 'Georgia', serif;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
  }
  
  .form-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid rgba(102, 126, 234, 0.2);
    border-radius: 10px;
    font-size: 1rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
    background: rgba(255, 255, 255, 0.8);
    font-family: inherit;
  }
  
  .form-input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  .form-submit {
    width: 100%;
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    font-family: inherit;
  }
  
  .form-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }
  
  .modal-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s ease;
  }
  
  .modal-close:hover {
    background: rgba(0, 0, 0, 0.1);
  }
  
  .modal-link {
    background: none;
    border: none;
    color: #667eea;
    cursor: pointer;
    text-decoration: underline;
    font-family: inherit;
    font-size: inherit;
  }
  
  .modal-link:hover {
    color: #764ba2;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: none; }
  }
  
  @media (max-width: 768px) {
    .hero-title {
      font-size: 2.5rem;
    }
    
    .hero-subtitle {
      font-size: 1.1rem;
    }
    
    .cta-buttons {
      flex-direction: column;
      align-items: center;
    }
    
    .features {
      grid-template-columns: 1fr;
    }
    
    .user-actions {
      flex-direction: column;
      align-items: center;
    }
    
    .centered-container {
      padding: 1rem;
    }
    
    .hero-glass {
      padding: 2rem 1.5rem;
    }
  }
</style>

<div class="landing-container">
  <div class="bg-art"></div>
  <div class="bg-overlay"></div>
  
  <div class="centered-container">
    <div class="hero-glass">
      <h1 class="hero-title">Oasiz Chatbot</h1>
      <p class="hero-subtitle">Your intelligent AI companion with powerful tools</p>
      
      {#if isLoggedIn}
        <div class="user-welcome">
          <div class="welcome-text">Welcome back, {currentUser?.name}! 👋</div>
          <div class="user-actions">
            <button class="btn btn-primary" on:click={goToChat}>Start Chatting</button>
            <button class="btn btn-secondary" on:click={logout}>Logout</button>
          </div>
        </div>
      {:else}
        <div class="cta-buttons">
          <button class="btn btn-primary" on:click={() => showSignup = true}>Get Started</button>
          <button class="btn btn-secondary" on:click={() => showLogin = true}>Login</button>
        </div>
      {/if}
      
      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">🤖</div>
          <h3 class="feature-title">AI Intelligence</h3>
          <p class="feature-description">Powered by advanced AI models for intelligent conversations and helpful responses.</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🔧</div>
          <h3 class="feature-title">Tool Integration</h3>
          <p class="feature-description">Access weather, search the web, execute code, and more with built-in tools.</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3 class="feature-title">Real-time Chat</h3>
          <p class="feature-description">Experience seamless, real-time conversations with instant responses.</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🎨</div>
          <h3 class="feature-title">Beautiful Design</h3>
          <p class="feature-description">Enjoy a modern, intuitive interface designed for the best user experience.</p>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Login Modal -->
{#if showLogin}
  <div class="modal-overlay" on:click={() => showLogin = false}>
    <div class="modal" on:click|stopPropagation>
      <button class="modal-close" on:click={() => showLogin = false} type="button">×</button>
      <h2 class="modal-title">Welcome Back</h2>
      <form on:submit|preventDefault={handleLogin}>
        <div class="form-group">
          <label class="form-label" for="login-email">Email</label>
          <input 
            id="login-email"
            type="email" 
            class="form-input" 
            bind:value={loginData.email} 
            placeholder="Enter your email"
            required
          />
        </div>
        <div class="form-group">
          <label class="form-label" for="login-password">Password</label>
          <input 
            id="login-password"
            type="password" 
            class="form-input" 
            bind:value={loginData.password} 
            placeholder="Enter your password"
            required
          />
        </div>
        <button type="submit" class="form-submit">Login</button>
      </form>
      <p style="text-align: center; margin-top: 1.5rem; color: #666;">
        Don't have an account? 
        <button 
          class="modal-link"
          on:click={() => { showLogin = false; showSignup = true; }}
          type="button"
        >
          Sign up
        </button>
      </p>
    </div>
  </div>
{/if}

<!-- Signup Modal -->
{#if showSignup}
  <div class="modal-overlay" on:click={() => showSignup = false}>
    <div class="modal" on:click|stopPropagation>
      <button class="modal-close" on:click={() => showSignup = false} type="button">×</button>
      <h2 class="modal-title">Join Oasiz</h2>
      <form on:submit|preventDefault={handleSignup}>
        <div class="form-group">
          <label class="form-label" for="signup-name">Name</label>
          <input 
            id="signup-name"
            type="text" 
            class="form-input" 
            bind:value={signupData.name} 
            placeholder="Enter your name"
            required
          />
        </div>
        <div class="form-group">
          <label class="form-label" for="signup-email">Email</label>
          <input 
            id="signup-email"
            type="email" 
            class="form-input" 
            bind:value={signupData.email} 
            placeholder="Enter your email"
            required
          />
        </div>
        <div class="form-group">
          <label class="form-label" for="signup-password">Password</label>
          <input 
            id="signup-password"
            type="password" 
            class="form-input" 
            bind:value={signupData.password} 
            placeholder="Create a password"
            required
          />
        </div>
        <div class="form-group">
          <label class="form-label" for="signup-confirm">Confirm Password</label>
          <input 
            id="signup-confirm"
            type="password" 
            class="form-input" 
            bind:value={signupData.confirmPassword} 
            placeholder="Confirm your password"
            required
          />
        </div>
        <button type="submit" class="form-submit">Create Account</button>
      </form>
      <p style="text-align: center; margin-top: 1.5rem; color: #666;">
        Already have an account? 
        <button 
          class="modal-link"
          on:click={() => { showSignup = false; showLogin = true; }}
          type="button"
        >
          Login
        </button>
      </p>
    </div>
  </div>
{/if}
