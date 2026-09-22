<script setup>
import { nextTick, ref } from 'vue';
import AppIcon from './AppIcon.vue';
import { MAX_LINES } from '../composables/useAnalysis.js';

const props = defineProps({ busy: Boolean, fileReading: Boolean, selectedFile: Object, lineCount: Number, submitHint: String });
const mode = defineModel('mode');
const text = defineModel('text');
const error = defineModel('error');
const emit = defineEmits(['analyze', 'selectFile', 'resetFile']);
const textInput = ref(null);
const fileInput = ref(null);
const textTab = ref(null);
const fileTab = ref(null);
const dragOver = ref(false);
const examples = [
  { label: '满意的一餐', value: '粥还是热的，包装很用心，下次还会点。' },
  { label: '不太好的体验', value: '等了一个多小时才送到，饭菜都凉了，汤还洒了一半。' },
  { label: '多条评价', value: '粥还是热的，包装很用心，下次还会点。\n等了一个多小时才送到，饭菜都凉了。\n分量很足，鸡腿外酥里嫩，配送也很快。\n备注了不要辣，结果还是放了很多辣椒。' },
];

function setMode(value) { if (!props.busy) { mode.value = value; error.value = ''; } }
async function tabKey(event) {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
  event.preventDefault();
  setMode(event.key === 'Home' ? 'text' : event.key === 'End' ? 'file' : mode.value === 'text' ? 'file' : 'text');
  await nextTick();
  (mode.value === 'text' ? textTab : fileTab).value?.focus();
}
function fillText(value) { text.value = value; error.value = ''; textInput.value?.focus(); }
function fileChange(event) { const file = event.target.files[0]; event.target.value = ''; emit('selectFile', file); }
function dropFile(event) {
  dragOver.value = false;
  if (props.busy) return;
  if (event.dataTransfer.files.length !== 1) { error.value = '每次请选择一个 TXT 文件。'; return; }
  emit('selectFile', event.dataTransfer.files[0]);
}
function submit() {
  emit('analyze');
  if (mode.value === 'text' && !text.value.trim()) textInput.value?.focus();
  if (mode.value === 'file' && !props.selectedFile) fileInput.value?.focus();
}
</script>

<template>
  <section class="panel input-panel" aria-labelledby="input-title">
    <div class="panel-heading"><div><h2 id="input-title">开始倾听</h2><p>放入评价，剩下的交给我们。</p></div><span class="step-glyph"><AppIcon name="wave" /></span></div>
    <div class="segmented" role="tablist" aria-label="评价输入方式" @keydown="tabKey">
      <button id="text-tab" ref="textTab" role="tab" :aria-selected="mode === 'text'" aria-controls="text-panel" :tabindex="mode === 'text' ? 0 : -1" :disabled="busy" @click="setMode('text')">输入文本</button>
      <button id="file-tab" ref="fileTab" role="tab" :aria-selected="mode === 'file'" aria-controls="file-panel" :tabindex="mode === 'file' ? 0 : -1" :disabled="busy" @click="setMode('file')">上传文件</button>
    </div>
    <form id="analysis-form" @submit.prevent="submit">
      <div v-show="mode === 'text'" id="text-panel" class="input-content" role="tabpanel" aria-labelledby="text-tab">
        <div class="field-heading"><label for="review-text">评价内容</label><button class="text-button" type="button" :disabled="busy" @click="fillText('')">清空</button></div>
        <textarea id="review-text" ref="textInput" v-model="text" :disabled="busy" aria-describedby="text-help" placeholder="今天的外卖怎么样？&#10;&#10;粥还是热的，包装很用心，下次还会点。&#10;送了一个多小时，饭都凉了。" maxlength="100000" spellcheck="false" @input="error = ''" @keydown.enter="($event.ctrlKey || $event.metaKey) && ($event.preventDefault(), submit())" />
        <div id="text-help" class="input-meta"><span>每行一条，最多 {{ MAX_LINES }} 条</span><span :class="{ 'over-limit': lineCount > MAX_LINES }">{{ lineCount }} 条</span></div>
        <div class="examples"><span>试一试</span><button v-for="example in examples" :key="example.label" type="button" :disabled="busy" @click="fillText(example.value)">{{ example.label }}</button></div>
      </div>
      <div v-show="mode === 'file'" id="file-panel" class="input-content" role="tabpanel" aria-labelledby="file-tab">
        <div class="field-heading"><span>评价文件</span><button v-if="selectedFile" type="button" class="text-button" :disabled="busy" @click="emit('resetFile')">移除</button></div>
        <label id="drop-zone" class="drop-zone" :class="{ 'has-file': selectedFile, 'drag-over': dragOver }" for="review-file" @dragenter.prevent="dragOver = !busy" @dragover.prevent="dragOver = !busy" @dragleave.prevent="dragOver = false" @drop.prevent="dropFile">
          <span class="upload-symbol"><AppIcon name="upload" /></span>
          <strong>{{ fileReading ? '正在读取文件…' : selectedFile ? selectedFile.file.name : '拖入文件，或点击选择' }}</strong>
          <span class="file-description">{{ selectedFile ? `${selectedFile.count} 条评价 · ${(selectedFile.size / 1024).toFixed(1)} KB` : 'UTF-8 编码的 .txt 文件' }}</span>
          <span class="file-limit">每行一条评价，最多 500 条 / 2 MB</span>
          <input id="review-file" ref="fileInput" type="file" accept=".txt,text/plain" :disabled="busy" @change="fileChange" />
        </label>
        <p class="file-note"><AppIcon name="info" />空行自动跳过，请只上传需要分析的评价。</p>
      </div>
      <div v-if="error" id="input-error" class="error-message" role="alert">{{ error }}</div>
      <div class="submit-area"><button id="analyze-button" class="primary-button" type="submit" :disabled="busy || fileReading"><span>{{ busy ? '正在分析…' : '分析评价' }}</span><AppIcon name="arrow" /></button><p>{{ submitHint }}</p></div>
    </form>
  </section>
</template>
