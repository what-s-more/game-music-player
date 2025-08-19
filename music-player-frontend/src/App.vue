<template>
  <div class="container mx-auto px-4 py-8 max-w-5xl">
    <el-card shadow="always" class="mb-6">
      <template #header>
        <h1 class="text-2xl font-bold">游戏乐器自动演奏器</h1>
        <p class="text-gray-500">编辑乐谱，让程序帮你自动演奏</p>
      </template>
    </el-card>

    <el-row :gutter="20">
      <!-- 按键映射说明 -->
      <el-col :span="24" class="mb-6">
        <el-card shadow="hover">
          <template #header>
            <el-icon class="mr-2"><Music /></el-icon>
            <span>音符按键映射</span>
          </template>
          <div class="p-4">
            <el-row :gutter="10">
              <el-col
                :xs="6"
                :sm="4"
                :md="3"
                v-for="(key, note) in keyMapping"
                :key="note"
              >
                <el-card class="text-center">
                  <div class="font-medium">{{ note }}</div>
                  <el-tag type="info" class="mt-1">{{ key }}</el-tag>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>

      <!-- 乐谱编辑区 -->
      <el-col :span="24" class="mb-6">
        <el-card shadow="hover">
          <template #header>
            <el-icon class="mr-2"><Edit /></el-icon>
            <span>乐谱编辑</span>
          </template>
          <div class="p-4">
            <el-row :gutter="20">
              <el-col :span="16">
                <el-input
                  type="textarea"
                  v-model="scoreJson"
                  :rows="10"
                  placeholder='示例: [{"note":"1","duration":0.3},{"note":"1","duration":0.3}]'
                  clearable
                />
                <el-text type="info" class="text-xs mt-1 block">
                  使用JSON格式，note为音符(1~7,1-~7-,1+~7+,0为休止符)，duration为时长(秒)
                </el-text>
              </el-col>
              <el-col :span="8">
                <el-form label-width="100px" size="small">
                  <el-form-item label="演奏速度">
                    <el-slider
                      v-model="speed"
                      :min="0.5"
                      :max="2"
                      :step="0.1"
                      :show-input="true"
                      input-size="small"
                    />
                  </el-form-item>
                  <el-form-item label="按键延迟(秒)">
                    <el-input-number
                      v-model="delay"
                      :min="0.01"
                      :max="0.5"
                      :step="0.01"
                      :precision="2"
                    />
                  </el-form-item>
                  <!-- 新增循环播放控件 -->
                  <el-form-item label="循环播放">
                    <el-switch
                      v-model="loop"
                      active-text="开启"
                      inactive-text="关闭"
                    />
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>

      <!-- 控制区域 -->
      <el-col :span="24" class="mb-6">
        <el-card shadow="hover" class="text-center p-4">
          <el-row :gutter="20" justify="center">
            <!-- 在这里添加示例选择按钮 -->
            <el-col :span="24" class="mb-4">
              <el-text class="mx-2">示例乐谱:</el-text>
              <el-button @click="loadExample('twinkle')" size="small">小星星</el-button>
              <el-button @click="loadExample('odeToJoy')" size="small">欢乐颂</el-button>
              <el-button @click="loadExample('jingleBells')" size="small">铃儿响叮当</el-button>
            </el-col>
            
            <el-col>
              <el-button
                @click="startPlay"
                type="success"
                :icon="Play"
                :disabled="isPlaying"
              >
                开始演奏
              </el-button>
            </el-col>
            <el-col>
              <el-button
                @click="stopPlay"
                type="danger"
                :icon="Stop"
                :disabled="!isPlaying"
              >
                停止演奏
              </el-button>
            </el-col>
          </el-row>
          
          <!-- 状态显示 -->
          <div class="mt-4">
            <el-descriptions column="1" border>
              <el-descriptions-item label="当前状态">
                <el-tag :type="isPlaying ? 'success' : 'info'">
                  <el-icon v-if="isPlaying" class="mr-1"><Loading /></el-icon>
                  <el-icon v-else class="mr-1"><Pause /></el-icon>
                  {{ isPlaying ? '正在演奏中...' : '就绪' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="消息" v-if="message">
                {{ message }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="text-center text-gray-500 text-sm">
      <p>注意：使用前请将游戏窗口置于前台，部分游戏可能视为作弊行为</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 配置 axios
const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// 状态变量
const scoreJson = ref('')
const speed = ref(1.0)
const delay = ref(0.05)
const isPlaying = ref(false)
const message = ref('')
const keyMapping = ref({})
const loop = ref(false)

// 在现有 loadExample 函数中添加更多示例
const loadExample = (exampleType = 'twinkle') => {
  let example = [];
  let title = '';

  switch(exampleType) {
    case 'twinkle': // 小星星（当前示例）
      example = [
        { note: '0', duration: 2 },
        { note: '1', duration: 0.3 },
        { note: '1', duration: 0.3 },
        { note: '5', duration: 0.3 },
        { note: '5', duration: 0.3 },
        { note: '6', duration: 0.3 },
        { note: '6', duration: 0.3 },
        { note: '5', duration: 0.6 },
        { note: '4', duration: 0.3 },
        { note: '4', duration: 0.3 },
        { note: '3', duration: 0.3 },
        { note: '3', duration: 0.3 },
        { note: '2', duration: 0.3 },
        { note: '2', duration: 0.3 },
        { note: '1', duration: 0.6 }
      ];
      title = '《小星星》';
      break;
      
    case 'odeToJoy': // 欢乐颂（节奏较快）
      example = [
        { note: '0', duration: 2 },
        { note: '3', duration: 0.4 },
        { note: '3', duration: 0.4 },
        { note: '4', duration: 0.4 },
        { note: '5', duration: 0.4 },
        { note: '5', duration: 0.4 },
        { note: '4', duration: 0.4 },
        { note: '3', duration: 0.4 },
        { note: '2', duration: 0.4 },
        { note: '1', duration: 0.4 },
        { note: '1', duration: 0.4 },
        { note: '2', duration: 0.4 },
        { note: '3', duration: 0.4 },
        { note: '3', duration: 0.6 },
        { note: '2', duration: 0.2 },
        { note: '2', duration: 0.8 }
      ];
      title = '《欢乐颂》';
      break;
      
    case 'jingleBells': // 铃儿响叮当（节奏轻快）
      example = [
        { note: '0', duration: 2 },
        { note: '3', duration: 0.3 },
        { note: '3', duration: 0.3 },
        { note: '3', duration: 0.6 },
        { note: '3', duration: 0.3 },
        { note: '3', duration: 0.3 },
        { note: '3', duration: 0.6 },
        { note: '3', duration: 0.3 },
        { note: '5', duration: 0.3 },
        { note: '1', duration: 0.3 },
        { note: '2', duration: 0.3 },
        { note: '3', duration: 1.2 },
        { note: '4', duration: 0.3 },
        { note: '4', duration: 0.3 },
        { note: '4', duration: 0.3 },
        { note: '4', duration: 0.3 },
        { note: '4', duration: 0.3 },
        { note: '3', duration: 0.3 },
        { note: '3', duration: 0.3 },
        { note: '3', duration: 0.3 },
        { note: '5', duration: 0.3 },
        { note: '5', duration: 0.3 },
        { note: '4', duration: 0.3 },
        { note: '2', duration: 0.3 },
        { note: '1', duration: 0.6 },
        { note: '1+', duration: 0.6 }
      ];
      title = '《铃儿响叮当》';
      break;
  }

  scoreJson.value = JSON.stringify(example, null, 2);
  message.value = `已加载示例乐谱${title}`;
}

// 开始演奏
const startPlay = async () => {
  try {
    const notes = JSON.parse(scoreJson.value)
    await api.post('/play', {
      notes,
      speed: speed.value,
      delay: delay.value,
      loop: loop.value
    })
    isPlaying.value = true
    message.value = '演奏开始'
  } catch (error) {
    console.error(error)
    message.value = error.response?.data?.detail || '演奏失败，请检查乐谱格式'
    ElMessage.error(message.value)
  }
}

// 停止演奏
const stopPlay = async () => {
  try {
    await api.post('/stop')
    isPlaying.value = false
    message.value = '已停止演奏'
    ElMessage.success('已停止演奏')
  } catch (error) {
    console.error(error)
    message.value = '停止失败'
    ElMessage.error('停止失败')
  }
}

// 检查状态
const checkStatus = async () => {
  try {
    const response = await api.get('/status')
    isPlaying.value = response.data.is_playing
  } catch (error) {
    console.error('获取状态失败', error)
  }
}

// 获取按键映射
const fetchKeyMapping = async () => {
  try {
    const response = await api.get('/key-mapping')
    keyMapping.value = response.data.mapping
  } catch (error) {
    console.error('获取按键映射失败', error)
  }
}

// 初始化
onMounted(() => {
  fetchKeyMapping()
  setInterval(checkStatus, 1000)
})
</script>