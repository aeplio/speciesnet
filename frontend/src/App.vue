<template>
  <v-app>
    <v-main>
      <v-container class="pa-6" fluid>
        <v-row>
          <v-col cols="12">
            <v-toolbar color="primary" dark flat>
              <v-toolbar-title>基于Speciesnet模型的脊椎动物分类识别系统</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-btn icon="mdi-information" @click="showHelp = true" />
            </v-toolbar>
          </v-col>
        </v-row>

        <v-row>
          <!-- 上方：上传与预览 -->
          <v-col cols="12" md="7">
            <v-card>
              <v-card-title>上传图片</v-card-title>
              <v-card-text>
                <v-alert v-if="errorMessage" type="error" class="mb-4" border="start" variant="tonal">
                  <div class="mb-1">{{ errorMessage }}</div>
                  <div v-if="errorHint" class="text-medium-emphasis">{{ errorHint }}</div>
                  <details v-if="errorStderr" class="mt-2">
                    <summary>展开错误详情</summary>
                    <pre style="white-space: pre-wrap">{{ errorStderr }}</pre>
                  </details>
                </v-alert>
                <v-file-input
                  v-model="file"
                  label="选择图片"
                  accept="image/*"
                  prepend-inner-icon="mdi-image"
                  show-size
                  @change="onFileChange"
                />
                <v-img v-if="previewUrl" :src="previewUrl" height="320" class="mt-4 preview-img" />
                <v-row class="mt-4" dense>
                  <v-col cols="12" sm="4">
                    <v-select
                      v-model="selectedModel"
                      label="选择模型"
                      :items="modelOptions"
                      item-title="label"
                      item-value="value"
                      prepend-inner-icon="mdi-brain"
                    />
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="country" label="国家(ISO3，可选) 例：CHN/USA/GBR" />
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-text-field v-model="admin1" label="州/省(可选) 例：CA" />
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions class="px-4 pb-4">
                <v-btn
                  color="primary"
                  variant="elevated"
                  size="x-large"
                  rounded="pill"
                  block
                  prepend-icon="mdi-magnify-scan"
                  :loading="loading"
                  :disabled="!file || loading"
                  @click="submit"
                >
                  开始识别
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>

          <!-- 右侧：标记后的图片 -->
          <v-col cols="12" md="5">
            <v-card>
              <v-card-title>模型标注</v-card-title>
              <v-card-text>
                <v-img v-if="annotatedUrl" :src="annotatedUrl" height="360" class="annotated-img" />
                <div v-else class="text-medium-emphasis">等待识别后显示...</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 下方：分类信息 -->
        <v-row class="mt-2">
          <v-col cols="12">
            <v-card>
              <v-card-title>物种分类信息</v-card-title>
              <v-card-text>
                <div v-if="result">
                  <v-chip
                    v-if="result.model_version"
                    color="primary"
                    variant="tonal"
                    class="mb-3"
                    prepend-icon="mdi-brain"
                  >
                    使用模型: {{ result.model_version }}
                    {{ result.model_version === 'v4.0.1a' ? '(Always-crop)' : result.model_version === 'v4.0.1b' ? '(Full-image)' : '' }}
                  </v-chip>
                  <v-alert type="info" v-if="result.category !== 'animals'">
                    {{ result.category }}（置信度 {{ (result.confidence*100).toFixed(1) }}%）
                  </v-alert>
                  <template v-else>
                    <v-row>
                      <v-col cols="12" md="8">
                        <v-list density="comfortable">
                          <v-list-item title="使用模型" :subtitle="result.model_version || 'v4.0.1a'" />
                          <v-list-item title="纲 (Class)" :subtitle="taxonomyParsed.class || ''" />
                          <v-list-item title="目 (Order)" :subtitle="taxonomyParsed.order || ''" />
                          <v-list-item title="科 (Family)" :subtitle="taxonomyParsed.family || ''" />
                          <v-list-item title="属 (Genus)" :subtitle="taxonomyParsed.genus || ''" />
                          <v-list-item title="种 (Species)" :subtitle="taxonomyParsed.species || ''" />
                          <v-list-item title="常见名称 (Common)" :subtitle="taxonomyParsed.common || ''" />
                          <v-list-item title="最终置信度" :subtitle="(result.confidence*100).toFixed(1) + '%'" />
                        </v-list>
                      </v-col>
                      <v-col cols="12" md="4">
                        <div class="text-subtitle-2 mb-2">其他Top分数（简略）</div>
                        <v-list density="comfortable">
                          <v-list-item
                            v-for="(item, i) in otherTaxonomyList"
                            :key="i"
                            :title="`置信度 ${item.scorePercent}`"
                            :subtitle="`${item.class || ''}；${item.order || ''}；${item.family || ''}；${item.genus || ''}；${item.species || ''}；${item.common || ''}`"
                          />
                        </v-list>
                      </v-col>
                    </v-row>
                  </template>
                </div>
                <div v-else class="text-medium-emphasis">未有结果，请先上传并识别。</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-dialog v-model="showHelp" width="700">
          <v-card>
            <v-card-title>使用说明</v-card-title>
            <v-card-text>
              <div class="mb-4">
                <strong>基本信息：</strong><br/>
                - 本项目由本人团队完全自主出品（我、机械革命、VsCode）。<br/>
                - 本项目基于谷歌开源的Speciesnet模型完成。<br/>
                - 上传图片将放入后端临时文件夹并在识别完成后清理。
              </div>
              <div class="mb-4">
                <strong>模型选择：</strong><br/>
                - <strong>v4.0.1a (Always-crop)</strong>：先运行检测器，将图像裁剪到顶部检测边界框，然后送入物种分类器。适合动物主体明确的图像。<br/>
                - <strong>v4.0.1b (Full-image)</strong>：同时在完整图像上独立运行检测器和物种分类器。适合复杂场景或多个目标的图像。
              </div>
              <div>
                <strong>地理信息（可选）：</strong><br/>
                提供国家代码（如CHN、USA、GBR）和州/省信息可以提高识别准确性。
              </div>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="showHelp=false">关闭</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- 引用信息 -->
        <v-row class="mt-6">
          <v-col cols="12">
            <div class="text-center text-caption text-medium-emphasis">
              <div class="mb-2">如果您在出版物中使用此模型，请引用—— DOI：10.1049/cvi2.12318</div>
              <div>
                Gadot, T., Istrate, Ș., Kim, H., Morris, D., Beery, S., Birch, T., & Ahumada, J. (2024). 
                To crop or not to crop: Comparing whole-image and cropped classification on a large dataset of camera trap images. 
                IET Computer Vision. https://doi.org/10.1049/cvi2.12318
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import axios from 'axios'
import { computed, ref } from 'vue'

const file = ref<File|undefined>()
const previewUrl = ref<string|undefined>()
const annotatedUrl = ref<string|undefined>()
const loading = ref(false)
const result = ref<any>(null)
const showHelp = ref(false)
const country = ref('')
const admin1 = ref('')
const selectedModel = ref('v4.0.1a')
const errorMessage = ref('')
const errorHint = ref('')
const errorStderr = ref('')

const modelOptions = [
  {
    label: 'v4.0.1a - Always-crop 模型（默认）',
    value: 'v4.0.1a',
  },
  {
    label: 'v4.0.1b - Full-image 模型',
    value: 'v4.0.1b',
  }
]

// 解析除最高分之外的其他分类，输出谱系与百分比
const otherTaxonomyList = computed(() => {
  const p = result.value?.raw_json?.predictions?.[0]
  const classes = (p?.classifications?.classes ?? []) as string[]
  const scores = (p?.classifications?.scores ?? []) as number[]
  if (!Array.isArray(classes) || !Array.isArray(scores) || classes.length === 0 || scores.length === 0) {
    return [] as Array<any>
  }
  // 找到最高分索引
  let topIdx = 0
  let max = -Infinity
  for (let i = 0; i < Math.min(classes.length, scores.length); i++) {
    const s = typeof scores[i] === 'number' ? scores[i] : Number(scores[i])
    if (!Number.isNaN(s) && s > max) { max = s; topIdx = i }
  }
  // 收集其余项并按分数降序
  const others: Array<{ idx:number, score:number, raw:string }> = []
  for (let i = 0; i < Math.min(classes.length, scores.length); i++) {
    if (i === topIdx) continue
    const s = typeof scores[i] === 'number' ? scores[i] : Number(scores[i])
    if (!Number.isNaN(s)) others.push({ idx: i, score: s, raw: String(classes[i] ?? '') })
  }
  others.sort((a, b) => b.score - a.score)
  // 映射为谱系结构
  return others.map(o => {
    const parts = o.raw.split(';').map(x => (typeof x === 'string' ? x.trim() : ''))
    while (parts.length < 7) parts.push('')
    return {
      class: parts[1] ?? '',
      order: parts[2] ?? '',
      family: parts[3] ?? '',
      genus: parts[4] ?? '',
      species: parts[5] ?? '',
      common: parts[6] ?? '',
      scorePercent: (o.score * 100).toFixed(1) + '%',
    }
  })
})

// 从 raw_json.predictions[0].classifications.classes 中解析以分号分隔的物种信息
// 结构: UUID; Class; Order; Family; Genus; Species; Common
const taxonomyParsed = computed(() => {
  const p = result.value?.raw_json?.predictions?.[0]
  const classes = (p?.classifications?.classes ?? []) as string[]
  const scores = (p?.classifications?.scores ?? []) as number[]
  if (!Array.isArray(classes) || classes.length === 0) {
    return { class: '', order: '', family: '', genus: '', species: '', common: '' }
  }
  let idx = 0
  if (Array.isArray(scores) && scores.length === classes.length && scores.length > 0) {
    let max = -Infinity
    for (let i = 0; i < scores.length; i++) {
      if (typeof scores[i] === 'number' && scores[i] > max) { max = scores[i]; idx = i }
    }
  }
  const raw = String(classes[idx] ?? '')
  const parts = raw.split(';').map(s => (typeof s === 'string' ? s.trim() : ''))
  while (parts.length < 7) parts.push('')
  const klass = parts[1] ?? ''
  const order = parts[2] ?? ''
  const family = parts[3] ?? ''
  const genus = parts[4] ?? ''
  const species = parts[5] ?? ''
  const common = parts[6] ?? ''
  return { class: klass, order, family, genus, species, common }
})

function onFileChange() {
  annotatedUrl.value = undefined
  result.value = null
  errorMessage.value = ''
  errorHint.value = ''
  errorStderr.value = ''
  if (!file.value) {
    previewUrl.value = undefined
    return
  }
  const url = URL.createObjectURL(file.value)
  previewUrl.value = url
}

async function submit() {
  if (!file.value) return
  loading.value = true
  try {
    errorMessage.value = ''
    errorHint.value = ''
    errorStderr.value = ''
    const form = new FormData()
    form.append('file', file.value)
    if (country.value) form.append('country', country.value)
    if (admin1.value) form.append('admin1_region', admin1.value)
    if (selectedModel.value) form.append('model', selectedModel.value)
    const { data } = await axios.post('/api/upload', form)
    result.value = data
    if (data.annotated_image_data) {
      annotatedUrl.value = data.annotated_image_data
    }
  } catch (err: any) {
    if (axios.isAxiosError(err)) {
      const data = err.response?.data as any
      errorMessage.value = data?.message || data?.detail || '后端处理失败'
      errorHint.value = data?.hint || ''
      errorStderr.value = data?.stderr || ''
    } else {
      errorMessage.value = String(err)
    }
  } finally {
    loading.value = false
  }
}

// 页面卸载时尝试清理
// 后端已在响应前清理临时目录，这里无需处理
</script>

<style>
html, body, #app { height: 100%; }
/* 使上传预览完整显示在框内 */
.preview-img > .v-img__img { object-fit: contain !important; }
.preview-img { background-color: #fafafa; border: 1px dashed rgba(0,0,0,0.12); }
/* 使模型标注图完整显示 */
.annotated-img > .v-img__img { object-fit: contain !important; }
.annotated-img { background-color: #fafafa; border: 1px solid rgba(0,0,0,0.08); }
</style>
