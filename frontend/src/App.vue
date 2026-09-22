<script setup>
import { onMounted, ref } from 'vue';
import AppIcon from './components/AppIcon.vue';
import InputPanel from './components/InputPanel.vue';
import ResultsPanel from './components/ResultsPanel.vue';
import { useAnalysis } from './composables/useAnalysis.js';
import { DEFAULT_API } from './api.js';

const {
  apiBase, mode, text, error, busy, fileReading, selectedFile, results, activeFilter, search, elapsed,
  announcement, toast, connection, connectionText, connectionHint, submitHint, lineCount, summary, filters, visibleResults,
  checkConnection, saveConnection, resetFile, selectFile, analyze, exportCsv,
} = useAnalysis();
const settingsDialog = ref(null);
const apiDraft = ref('');
const settingsError = ref('');
function openSettings() { apiDraft.value = apiBase.value; settingsError.value = ''; settingsDialog.value.showModal(); }
function saveSettings() {
  try { saveConnection(apiDraft.value); settingsDialog.value.close(); }
  catch (cause) { settingsError.value = cause.message; }
}
onMounted(checkConnection);
</script>

<template>
  <header class="topbar"><div class="nav-inner"><a class="brand" href="./" aria-label="听见首页"><span class="brand-mark"><AppIcon name="wave" /></span><span>听见<span class="brand-divider">/</span><span class="brand-caption">情感分析</span></span></a><div class="nav-actions"><button class="connection" :title="connectionHint" :disabled="connection === 'checking'" @click="checkConnection"><span class="status-dot" :data-status="connection" />{{ connectionText }}</button><span class="nav-divider" /><button class="icon-button" :disabled="busy" aria-label="连接设置" title="连接设置" @click="openSettings"><AppIcon name="settings" /></button></div></div></header>
  <main>
    <section class="intro" aria-labelledby="page-title"><div class="intro-copy"><h1 id="page-title">每一句评价，都值得听见。</h1><p class="intro-description">从一份餐食的反馈，发现真实的情绪。</p></div><div class="sound-art" aria-hidden="true"><div class="sound-orbit orbit-one" /><div class="sound-orbit orbit-two" /><div class="sound-core"><span v-for="i in 7" :key="i" /></div><span class="art-spark spark-one" /></div></section>
    <div class="workspace">
      <InputPanel v-model:mode="mode" v-model:text="text" v-model:error="error" :busy="busy" :file-reading="fileReading" :selected-file="selectedFile" :line-count="lineCount" :submit-hint="submitHint" @analyze="analyze" @select-file="selectFile" @reset-file="resetFile" />
      <ResultsPanel v-model:active-filter="activeFilter" v-model:search="search" :busy="busy" :results="results" :visible-results="visibleResults" :summary="summary" :filters="filters" :elapsed="elapsed" @export="exportCsv" />
    </div>
    <aside class="guide" aria-label="分析说明"><span><b>1</b>放入真实评价</span><span><b>2</b>查看情感与置信度</span><span><b>3</b>筛选并导出结果</span></aside>
    <footer class="footer"><span>听见 · 让反馈有回响</span><span>基于 BERT 的情感分析 / 模型判断仅供参考</span></footer>
  </main>
  <dialog ref="settingsDialog" aria-labelledby="settings-title"><form @submit.prevent="saveSettings"><div class="dialog-heading"><h2 id="settings-title">连接设置</h2><button type="button" class="icon-button" aria-label="关闭连接设置" @click="settingsDialog.close()"><AppIcon name="close" /></button></div><p class="dialog-description">连接提供情感分析的后端服务。</p><label for="api-url">接口基础地址</label><input id="api-url" v-model="apiDraft" type="text" placeholder="/api/v1" required autocomplete="url" aria-describedby="api-help" /><p id="api-help" class="field-help">本地开发使用 /api/v1。远程服务填写完整地址，例如 http://127.0.0.1:8000/api/v1。</p><div v-if="settingsError" id="settings-error" class="error-message" role="alert">{{ settingsError }}</div><div class="dialog-actions"><button type="button" class="secondary-button" @click="apiDraft = DEFAULT_API">恢复默认</button><button class="primary-button" type="submit">保存并连接</button></div></form></dialog>
  <div v-if="toast" class="toast" role="status">{{ toast }}</div>
  <div class="visually-hidden" role="status" aria-live="polite">{{ announcement }}</div>
</template>
