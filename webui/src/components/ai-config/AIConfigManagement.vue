<template>
  <div class="ai-config-management">
    <el-card shadow="hover">
      <el-tabs v-model="activeTab" class="config-tabs">
        <el-tab-pane label="LLM配置" name="llm">
          <LLMConfig />
        </el-tab-pane>
        <el-tab-pane label="工具配置" name="tools">
          <ToolConfig />
        </el-tab-pane>
        <el-tab-pane label="技能配置" name="skills">
          <SkillConfig />
        </el-tab-pane>
        <el-tab-pane label="规则配置" name="rules">
          <RuleConfig />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LLMConfig from './LLMConfig.vue'
import ToolConfig from './ToolConfig.vue'
import SkillConfig from './SkillConfig.vue'
import RuleConfig from './RuleConfig.vue'

const activeTab = ref('llm')
</script>

<style scoped>
.ai-config-management {
  padding: 20px;
}

.config-tabs {
  min-height: 600px;
}

.config-tabs :deep(.el-tabs__content) {
  padding: 20px 0;
}
</style>
