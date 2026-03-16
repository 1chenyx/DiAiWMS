<template>
  <div class="ai-chat">
    <div class="chat-container">
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <h3>对话历史</h3>
          <el-button type="primary" size="small" @click="handleNewChat">
            <el-icon><Plus /></el-icon> 新对话
          </el-button>
        </div>
        <div class="chat-list">
          <div
            v-for="chat in chatHistory"
            :key="chat.id"
            :class="['chat-item', { active: currentChatId === chat.id }]"
            @click="handleSelectChat(chat.id)"
          >
            <el-icon><ChatDotRound /></el-icon>
            <span class="chat-title">{{ chat.title }}</span>
            <el-button type="danger" size="small" text @click.stop="handleDeleteChat(chat.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
      
      <div class="chat-main">
        <div class="chat-header">
          <div class="config-selector">
            <span class="label">AI模型：</span>
            <el-select v-model="selectedConfigId" placeholder="选择AI配置" style="width: 200px" clearable>
              <el-option
                v-for="config in configList"
                :key="config.id"
                :label="`${config.provider_name} - ${config.model_name}`"
                :value="config.id"
              >
                <span>{{ config.provider_name }} - {{ config.model_name }}</span>
                <el-tag v-if="config.is_default" type="success" size="small" style="margin-left: 8px">默认</el-tag>
              </el-option>
            </el-select>
          </div>
          <div class="header-actions">
            <el-button @click="handleClearMessages" :disabled="messages.length === 0">
              <el-icon><Delete /></el-icon> 清空对话
            </el-button>
          </div>
        </div>
        
        <div class="chat-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <el-icon :size="64" color="#c0c4cc"><ChatDotRound /></el-icon>
            <p>开始与AI助手对话</p>
            <div class="quick-actions">
              <el-button v-for="action in quickActions" :key="action" @click="handleQuickAction(action)">
                {{ action }}
              </el-button>
            </div>
          </div>
          
          <div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
            <div class="message-avatar">
              <el-avatar v-if="message.role === 'user'" :size="36">
                {{ userStore.userInfo?.user_name?.charAt(0)?.toUpperCase() || 'U' }}
              </el-avatar>
              <el-avatar v-else :size="36" style="background: #409eff">
                <el-icon><Monitor /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="role-name">{{ message.role === 'user' ? '我' : 'AI助手' }}</span>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="message-text" v-html="formatMessage(message.content)"></div>
            </div>
          </div>
          
          <div v-if="loading" class="message assistant">
            <div class="message-avatar">
              <el-avatar :size="36" style="background: #409eff">
                <el-icon><Monitor /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="role-name">AI助手</span>
              </div>
              <div class="message-text typing">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息... (Ctrl+Enter 发送)"
            @keydown.ctrl.enter="handleSend"
            :disabled="loading"
          />
          <div class="input-actions">
            <div class="input-options">
              <el-slider
                v-model="temperature"
                :min="0"
                :max="2"
                :step="0.1"
                style="width: 120px"
                :format-tooltip="(val: number) => `温度: ${val}`"
              />
            </div>
            <el-button type="primary" @click="handleSend" :loading="loading" :disabled="!inputMessage.trim()">
              <el-icon><Position /></el-icon> 发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { Plus, Delete, ChatDotRound, Monitor, Position } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { aiChatService, type ChatMessage } from '@/services/aiChatService'
import { tenantAIConfigService, type TenantAIConfig } from '@/services/aiConfigService'

const userStore = useUserStore()

const messages = ref<(ChatMessage & { timestamp: number })[]>([])
const inputMessage = ref('')
const loading = ref(false)
const temperature = ref(0.7)
const selectedConfigId = ref<number | undefined>()
const configList = ref<TenantAIConfig[]>([])
const messagesContainer = ref<HTMLElement | null>(null)

const chatHistory = ref<{ id: string; title: string; messages: (ChatMessage & { timestamp: number })[] }[]>([])
const currentChatId = ref<string>('')

const quickActions = [
  '查询当前库存情况',
  '分析最近的订单趋势',
  '推荐最优拣货路径',
  '检查库存预警'
]

const fetchConfigList = async () => {
  try {
    const result = await tenantAIConfigService.getList({ page_index: 1, page_size: 100 })
    configList.value = result.data || result.rows || []
    const defaultConfig = configList.value.find(c => c.is_default)
    if (defaultConfig) {
      selectedConfigId.value = defaultConfig.id
    }
  } catch (error: any) {
    console.error('获取AI配置列表失败:', error)
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const handleSend = async () => {
  if (!inputMessage.value.trim() || loading.value) return
  
  const userMessage: ChatMessage & { timestamp: number } = {
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: Date.now()
  }
  
  messages.value.push(userMessage)
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()
  
  try {
    const response = await aiChatService.completions({
      messages: messages.value.map(m => ({ role: m.role, content: m.content })),
      config_id: selectedConfigId.value,
      temperature: temperature.value
    })
    
    const assistantMessage: ChatMessage & { timestamp: number } = {
      role: 'assistant',
      content: response.message.content,
      timestamp: Date.now()
    }
    messages.value.push(assistantMessage)
    scrollToBottom()
    
    if (!currentChatId.value) {
      const chatId = Date.now().toString()
      currentChatId.value = chatId
      chatHistory.value.unshift({
        id: chatId,
        title: userMessage.content.slice(0, 20) + (userMessage.content.length > 20 ? '...' : ''),
        messages: [...messages.value]
      })
    } else {
      const chat = chatHistory.value.find(c => c.id === currentChatId.value)
      if (chat) {
        chat.messages = [...messages.value]
      }
    }
    
    saveChatHistory()
  } catch (error: any) {
    ElMessage.error(error.message || '发送消息失败')
  } finally {
    loading.value = false
  }
}

const handleQuickAction = (action: string) => {
  inputMessage.value = action
  handleSend()
}

const handleNewChat = () => {
  messages.value = []
  currentChatId.value = ''
}

const handleSelectChat = (chatId: string) => {
  const chat = chatHistory.value.find(c => c.id === chatId)
  if (chat) {
    currentChatId.value = chatId
    messages.value = [...chat.messages]
    scrollToBottom()
  }
}

const handleDeleteChat = async (chatId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    chatHistory.value = chatHistory.value.filter(c => c.id !== chatId)
    if (currentChatId.value === chatId) {
      handleNewChat()
    }
    saveChatHistory()
  } catch {
    // 用户取消
  }
}

const handleClearMessages = async () => {
  try {
    await ElMessageBox.confirm('确定要清空当前对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    messages.value = []
    if (currentChatId.value) {
      const chat = chatHistory.value.find(c => c.id === currentChatId.value)
      if (chat) {
        chat.messages = []
      }
      saveChatHistory()
    }
  } catch {
    // 用户取消
  }
}

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatMessage = (content: string) => {
  return content.replace(/\n/g, '<br>').replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
}

const saveChatHistory = () => {
  localStorage.setItem('ai_chat_history', JSON.stringify(chatHistory.value.slice(0, 20)))
}

const loadChatHistory = () => {
  const saved = localStorage.getItem('ai_chat_history')
  if (saved) {
    try {
      chatHistory.value = JSON.parse(saved)
    } catch {
      chatHistory.value = []
    }
  }
}

watch(messages, scrollToBottom, { deep: true })

onMounted(() => {
  fetchConfigList()
  loadChatHistory()
})
</script>

<style scoped>
.ai-chat {
  height: calc(100vh - 120px);
  padding: 20px;
}

.chat-container {
  display: flex;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-sidebar {
  width: 260px;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.3s;
}

.chat-item:hover {
  background: #f5f7fa;
}

.chat-item.active {
  background: #ecf5ff;
}

.chat-title {
  flex: 1;
  margin-left: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-selector .label {
  font-size: 14px;
  color: #606266;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-state p {
  margin-top: 16px;
  font-size: 16px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 24px;
  justify-content: center;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  margin: 0 12px;
}

.message.user .message-content {
  text-align: right;
}

.message-header {
  margin-bottom: 8px;
}

.role-name {
  font-weight: 500;
  color: #303133;
}

.message-time {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
}

.message.user .message-text {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: #f5f7fa;
  color: #303133;
  border-bottom-left-radius: 4px;
}

.message-text pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-text code {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}

.typing {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
}

.typing .dot {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.chat-input {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-options {
  display: flex;
  gap: 16px;
  align-items: center;
}
</style>
