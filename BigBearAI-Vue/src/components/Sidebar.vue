<template>
  <aside class="sidebar">
    <div class="logo-area">
      <i class="ph-fill ph-robot logo-icon"></i>
      <span>大熊AI</span>
    </div>
    <nav class="nav-menu">
      <router-link to="/" class="nav-item" active-class="active">
        <i class="ph ph-house"></i>
        <span>Home</span>
      </router-link>
      <router-link to="/rules" class="nav-item" active-class="active">
        <i class="ph ph-scroll"></i>
        <span>Rules</span>
      </router-link>
      <router-link to="/agents" class="nav-item" active-class="active">
        <i class="ph ph-robot"></i>
        <span>智能体</span>
      </router-link>
      <router-link to="/prompt" class="nav-item" active-class="active">
        <i class="ph ph-magic-wand"></i>
        <span>Prompt</span>
      </router-link>
      <router-link to="/mcp" class="nav-item" active-class="active">
        <i class="ph ph-plugs-connected"></i>
        <span>MCP</span>
      </router-link>
      <router-link to="/knowledge" class="nav-item" active-class="active">
        <i class="ph ph-books"></i>
        <span>知识库</span>
      </router-link>
      <router-link to="/plugins" class="nav-item" active-class="active">
        <i class="ph ph-puzzle-piece"></i>
        <span>插件</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
// Sidebar logic is mainly handled by router-link active class
</script>

<style scoped>
/* Sidebar styles are in layout.css */
</style>
