<template>
  <main class="main-content home-content">
    <div class="hero-section">
      <h1 class="hero-title">
        <span class="text-gradient">大熊AI</span> 你的AI测试伙伴
      </h1>
      <div class="mascot-container">
        <i class="ph-fill ph-robot mascot-icon"></i>
      </div>
    </div>

    <div class="chat-container">
      <div class="chat-input-wrapper">
        <div class="chat-input-header">
          <i class="ph ph-sparkle"></i>
        </div>
        <textarea placeholder="输入任意内容，开始你的测试设计~"></textarea>
        <div class="chat-input-footer">
          <div class="mode-selector">
            <i class="ph-fill ph-magic-wand"></i>
            <span>Auto</span>
            <i class="ph ph-caret-down"></i>
          </div>
          <button class="send-btn">
            <i class="ph-fill ph-paper-plane-right"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <button class="action-btn">
        <i class="ph ph-play-circle"></i>
        <span>告诉开始测试</span>
      </button>
      <button class="action-btn">
        <i class="ph ph-folder-open"></i>
        <span>打开测试设计</span>
      </button>
      <button class="action-btn">
        <i class="ph ph-plus-circle"></i>
        <span>新建测试项目</span>
      </button>
    </div>
  </main>
</template>

<script setup>
// No script logic needed for Home yet
</script>

<style scoped>
/* Home specific styles are already in home.css which is globally imported */
</style>
