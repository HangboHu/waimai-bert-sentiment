<script setup>
import AppIcon from './AppIcon.vue';
defineProps({ busy: Boolean, results: Array, visibleResults: Array, summary: Array, filters: Array, elapsed: String });
const activeFilter = defineModel('activeFilter');
const search = defineModel('search');
const emit = defineEmits(['export']);
function tone(label) {
  if (/^(好评|正面|正向|积极|positive)$/i.test(label)) return 'positive';
  if (/^(差评|负面|负向|消极|negative)$/i.test(label)) return 'negative';
  return 'neutral';
}
</script>

<template>
  <section class="panel results-panel" aria-labelledby="results-title" :aria-busy="busy">
    <div class="panel-heading"><div><div class="result-title-row"><h2 id="results-title">情绪，一目了然。</h2><span v-if="results.length" class="count-badge">{{ results.length }}</span></div><p>{{ results.length ? `本次分析完成 · 用时 ${elapsed} 秒` : '每一条反馈，都有迹可循。' }}</p></div><button class="icon-button export-button" :disabled="busy || !results.length" aria-label="导出全部分析结果为 CSV" title="导出全部分析结果为 CSV" @click="emit('export')"><AppIcon name="download" /></button></div>
    <div v-if="busy" class="loading-state" role="status"><div class="loading-wave" aria-hidden="true"><i v-for="i in 5" :key="i" /></div><h3>正在读懂这些声音</h3><p>模型正在分析，请稍候。</p></div>
    <div v-else-if="!results.length" class="empty-state">
      <div class="empty-illustration" aria-hidden="true"><div class="review-bubble bubble-back"><span /><span /></div><div class="review-bubble bubble-front"><i class="face-eye eye-left" /><i class="face-eye eye-right" /><i class="face-smile" /></div><span class="small-star">✦</span></div>
      <h3>洞察，从第一句开始。</h3><p>输入一条评价，或上传一份文件。<br />分析结果将在这里呈现。</p><div class="empty-labels"><span><i class="legend-dot positive" />好评</span><span><i class="legend-dot negative" />差评</span><span><i class="legend-dot" />置信度</span></div>
    </div>
    <div v-else id="results-content">
      <div class="result-summary"><div v-for="item in summary" :key="item.label" class="summary-item"><strong>{{ item.value }}</strong><span>{{ item.label }}</span></div></div>
      <div class="results-toolbar"><div id="result-filters" class="result-filters" role="group" aria-label="筛选结果"><button v-for="filter in filters" :key="filter.label ?? 'all'" class="filter-button" :aria-pressed="activeFilter === filter.label" @click="activeFilter = filter.label">{{ filter.label ?? '全部' }} {{ filter.count }}</button></div><label class="search-box"><AppIcon name="search" /><input v-model="search" type="search" placeholder="搜索评价" aria-label="搜索评价" /></label></div>
      <div id="result-list" class="result-list" tabindex="0" role="region" aria-label="分析结果列表">
        <article v-for="(item, index) in visibleResults" :key="index" class="result-row" :class="tone(item.label)"><p class="review-copy">{{ item.text }}</p><div class="review-meta"><span class="sentiment-badge" :class="tone(item.label)">{{ item.label }}</span><div class="confidence"><span class="confidence-track" aria-hidden="true"><span class="confidence-fill" :style="{ width: item.confidence }" /></span><span>置信度 {{ item.confidence }}</span></div><span v-if="!item.is_certain" class="uncertain-badge">建议复核</span></div></article>
        <p v-if="!visibleResults.length" id="no-matches" class="no-matches">没有匹配的评价，试试其他关键词或分类。</p>
      </div>
      <div class="result-footer"><span>显示 {{ visibleResults.length }} / {{ results.length }} 条</span><span>置信度低于 80% 时建议复核</span></div>
    </div>
  </section>
</template>
