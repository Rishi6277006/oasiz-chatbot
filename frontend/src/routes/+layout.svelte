<script lang="ts">
  import { page } from "$app/stores";
  import { injectAnalytics } from "@vercel/analytics/sveltekit";
  import "../app.css";
  
  // Initialize Vercel Analytics
  injectAnalytics();
</script>

<div class="app">
  <slot />
</div>

<style>
  .app {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
</style>
