import { ref, computed, watch, onMounted } from 'vue'

export function useTheme() {
    const theme = ref(localStorage.getItem('theme') || 'light')

    const toggleTheme = () => {
        theme.value = theme.value === 'light' ? 'dark' : 'light'
    }

    const setTheme = (newTheme) => {
        theme.value = newTheme
    }

    const isDark = computed(() => theme.value === 'dark')

    // 监听主题变化，更新DOM和本地存储
    watch(theme, (newTheme) => {
        document.documentElement.setAttribute('data-theme', newTheme)
        localStorage.setItem('theme', newTheme)
    }, { immediate: true })

    // 初始化时应用主题
    onMounted(() => {
        document.documentElement.setAttribute('data-theme', theme.value)
    })

    return {
        theme,
        toggleTheme,
        setTheme,
        isDark
    }
}

