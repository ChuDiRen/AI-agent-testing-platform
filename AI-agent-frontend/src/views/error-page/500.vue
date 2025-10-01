<template>
  <AppPage>
    <n-result m-auto status="500">
      <template #icon>
        <AppIcon name="mdi:server-network-off" text-400px text-primary />
      </template>
      <template #footer>
        <n-button type="primary" @click="replace('/')">
          返回首页
        </n-button>
      </template>
    </n-result>
  </AppPage>
</template>

<script setup>
import { AppIcon } from '@/components'

const { replace } = useRouter()
</script>

