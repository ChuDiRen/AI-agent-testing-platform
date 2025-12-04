<template>
  <div 
    class="card unified-card" 
    :style="cardStyle"
  >
    <!-- Decoration -->
    <div v-html="decoration" class="card-decoration"></div>

    <div class="card-header" style="position:relative;z-index:1;">
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <span 
          class="badge" 
          :style="{ backgroundColor: item.color, color: item.textColor }"
          style="padding:3px 10px;border-radius:4px;font-size:0.75rem;font-weight:500;"
        >
          {{ badgeText }}
        </span>
        <span 
          v-for="tag in extraBadges" 
          :key="tag"
          class="badge" 
          :style="{ backgroundColor: item.color, color: item.textColor }"
          style="margin-left:4px;font-size:0.7rem;"
        >
          {{ tag }}
        </span>
      </div>
      
      <span v-if="showStatus" class="mcp-status" :class="statusText.toLowerCase()" style="margin-left:auto;font-size:0.7rem;">
          <span class="status-dot"></span>
          {{ statusText }}
      </span>
    </div>

    <h3 class="card-title" style="position:relative;z-index:1;margin-top:12px;font-size:1rem;font-weight:600;">
      {{ item.title }}
    </h3>
    <p class="card-desc" style="position:relative;z-index:1;font-size:0.85rem;color:#666;line-height:1.5;margin-top:8px;flex:1;">
      {{ item.desc }}
    </p>

    <div class="card-footer" style="position:relative;z-index:1;margin-top:auto;padding-top:12px;">
      <div class="author-info">
        <div 
          class="avatar-sm" 
          :style="{ backgroundColor: item.textColor }"
          style="width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:0.65rem;font-weight:bold;"
        >
          {{ item.author[0] }}
        </div>
        <span style="font-size:0.8rem;color:#888;">{{ item.author }} · {{ item.date }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
  }
});

const badgeText = computed(() => {
  if (props.options.badgeText) return props.options.badgeText;
  if (props.item.tags && props.item.tags.length > 0) return props.item.tags[0];
  if (props.item.type) return props.item.type;
  return '';
});

const showIcon = computed(() => props.options.showIcon || false);
const iconName = computed(() => props.options.iconName || props.item.icon || 'star');
const showStatus = computed(() => props.options.showStatus || false);
const statusText = computed(() => props.options.statusText || props.item.status || '');
const extraBadges = computed(() => props.options.extraBadges || []);

const cardStyle = computed(() => ({
  background: `linear-gradient(145deg, ${props.item.color}50 0%, ${props.item.color}20 50%, white 100%)`,
  minHeight: '180px',
  position: 'relative',
  overflow: 'hidden'
}));

const decoration = computed(() => {
  const decorations = [
    `<div style="position:absolute;right:12px;top:12px;opacity:0.6;font-size:2rem;color:${props.item.textColor}40;"><i class="ph-fill ph-${iconName.value}"></i></div>`,
    `<div style="position:absolute;right:8px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:4px;opacity:0.5;">
        <div style="width:8px;height:8px;border-radius:50%;background:${props.item.textColor}60;"></div>
        <div style="width:6px;height:6px;border-radius:50%;background:${props.item.textColor}40;"></div>
        <div style="width:4px;height:4px;border-radius:50%;background:${props.item.textColor}30;"></div>
    </div>`
  ];
  // Deterministic decoration based on id or title to avoid hydration mismatch if random
  // But original was random. Let's use a simple hash of ID for consistency
  const index = (props.item.id || 0) % decorations.length;
  return decorations[index];
});
</script>

<style scoped>
/* Add any specific scoped styles if needed, but we are using global CSS */
</style>
