import { computed, onBeforeUnmount, ref, shallowRef } from 'vue';
import { apiRequest, DEFAULT_API, normalizeBaseUrl, validateResults } from '../api.js';

export const MAX_LINES = 500;
const MAX_FILE_BYTES = 2 * 1024 * 1024;
const lines = text => text.split(/\r?\n/).map(line => line.trim()).filter(Boolean);

export function useAnalysis() {
  const apiBase = ref(DEFAULT_API);
  try { apiBase.value = normalizeBaseUrl(localStorage.getItem('tingjian-api') || DEFAULT_API); } catch { /* Use default when storage is unavailable. */ }
  const mode = ref('text');
  const text = ref('');
  const error = ref('');
  const busy = ref(false);
  const fileReading = ref(false);
  const selectedFile = shallowRef(null);
  const results = shallowRef([]);
  const activeFilter = ref(null);
  const search = ref('');
  const elapsed = ref('');
  const announcement = ref('');
  const toast = ref('');
  const connection = ref('checking');
  const connectionHint = ref('正在检查后端连接');
  const labels = ref([]);
  let fileVersion = 0;
  let connectionVersion = 0;
  let toastTimer;

  const lineCount = computed(() => lines(text.value).length);
  const connectionText = computed(() => ({ checking: '正在连接', online: '服务已连接', offline: '服务未连接' })[connection.value]);
  const submitHint = computed(() => connection.value === 'offline'
    ? '请启动后端服务，或在右上角设置连接'
    : labels.value.length ? `支持${labels.value.join('、')}识别` : '支持好评与差评识别');
  const summary = computed(() => [
    { value: results.value.length, label: '已分析评价' },
    { value: results.value.filter(item => item.is_certain).length, label: '高置信度' },
    { value: `${(results.value.length ? results.value.reduce((sum, item) => sum + Number.parseFloat(item.confidence), 0) / results.value.length : 0).toFixed(1)}%`, label: '平均置信度' },
  ]);
  const filters = computed(() => {
    const counts = new Map();
    results.value.forEach(item => counts.set(item.label, (counts.get(item.label) || 0) + 1));
    return [{ label: null, count: results.value.length }, ...Array.from(counts, ([label, count]) => ({ label, count }))];
  });
  const visibleResults = computed(() => {
    const query = search.value.trim().toLocaleLowerCase();
    return results.value.filter(item => (activeFilter.value === null || item.label === activeFilter.value) && item.text.toLocaleLowerCase().includes(query));
  });

  async function checkConnection() {
    const version = ++connectionVersion;
    connection.value = 'checking';
    try {
      await apiRequest(apiBase.value, '/', { timeout: 8000 });
      if (version !== connectionVersion) return;
      const payload = await apiRequest(apiBase.value, '/labels', { timeout: 8000 });
      if (!Array.isArray(payload.results) || !payload.results.length || payload.results.some(label => typeof label !== 'string')) {
        throw new Error('未能读取分类标签，请检查后端配置。');
      }
      if (version !== connectionVersion) return;
      labels.value = payload.results;
      connection.value = 'online';
      connectionHint.value = '点击重新检查连接';
    } catch (cause) {
      if (version !== connectionVersion) return;
      connection.value = 'offline';
      connectionHint.value = `${cause.message} 点击重试。`;
    }
  }

  function saveConnection(value) {
    apiBase.value = normalizeBaseUrl(value);
    try { localStorage.setItem('tingjian-api', apiBase.value); } catch { /* Connection works without persistent storage. */ }
    checkConnection();
  }

  function resetFile() {
    fileVersion += 1;
    selectedFile.value = null;
    fileReading.value = false;
    error.value = '';
  }

  async function selectFile(file) {
    if (!file || busy.value) return;
    resetFile();
    const version = fileVersion;
    fileReading.value = true;
    try {
      if (!/\.txt$/i.test(file.name)) throw new Error('请选择 .txt 文件，每行放入一条评价。');
      if (file.size > MAX_FILE_BYTES) throw new Error('文件超过 2 MB，请拆分成较小的文件后重试。');
      let content;
      try { content = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer()); }
      catch { throw new Error('无法按 UTF-8 读取文件，请将文件另存为 UTF-8 编码后重试。'); }
      if (version !== fileVersion) return;
      const reviews = lines(content);
      if (!reviews.length) throw new Error('文件中没有评价，请添加内容后重新选择。');
      if (reviews.length > MAX_LINES) throw new Error(`文件包含 ${reviews.length} 条评价，每次最多分析 ${MAX_LINES} 条，请拆分后重试。`);
      selectedFile.value = {
        file: new File([reviews.join('\n')], file.name, { type: 'text/plain;charset=utf-8' }),
        count: reviews.length,
        size: file.size,
      };
    } catch (cause) {
      if (version === fileVersion) error.value = cause.message;
    } finally {
      if (version === fileVersion) fileReading.value = false;
    }
  }

  async function analyze() {
    if (busy.value || fileReading.value) return;
    error.value = '';
    let body;
    let count;
    let path;
    if (mode.value === 'text') {
      const reviews = lines(text.value);
      if (!reviews.length) { error.value = '先写下一条评价，再开始分析。'; return; }
      if (reviews.length > MAX_LINES) { error.value = `每次最多分析 ${MAX_LINES} 条评价，请分批提交。`; return; }
      count = reviews.length;
      body = { text: reviews.length === 1 ? reviews[0] : reviews };
      path = '/classify';
    } else {
      if (!selectedFile.value) { error.value = '请先选择一份包含评价的 TXT 文件。'; return; }
      body = new FormData();
      body.append('text_file', selectedFile.value.file);
      count = selectedFile.value.count;
      path = '/classify_from_file';
    }
    busy.value = true;
    const started = performance.now();
    try {
      const payload = await apiRequest(apiBase.value, path, { body });
      results.value = validateResults(payload.results, count);
      activeFilter.value = null;
      search.value = '';
      elapsed.value = ((performance.now() - started) / 1000).toFixed(1);
      announcement.value = `已完成 ${results.value.length} 条评价分析，结果已更新。`;
    } catch (cause) {
      error.value = `${cause.message}${results.value.length ? ' 保留上次成功的分析结果。' : ''}`;
    } finally {
      busy.value = false;
    }
  }

  function exportCsv() {
    if (!results.value.length || busy.value) return;
    const escape = value => {
      const cell = String(value);
      return `"${(/^[\s\uFEFF]*[=+@-]/.test(cell) ? `'${cell}` : cell).replace(/"/g, '""')}"`;
    };
    const rows = [['评价内容', '情感分类', '置信度', '是否建议复核'], ...results.value.map(item => [item.text, item.label, item.confidence, item.is_certain ? '否' : '是'])];
    const csv = '\uFEFF' + rows.map(row => row.map(escape).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `听见-情感分析-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    clearTimeout(toastTimer);
    toast.value = `已导出全部 ${results.value.length} 条分析结果`;
    toastTimer = setTimeout(() => { toast.value = ''; }, 3600);
  }

  onBeforeUnmount(() => { clearTimeout(toastTimer); fileVersion += 1; connectionVersion += 1; });

  return {
    apiBase, mode, text, error, busy, fileReading, selectedFile, results, activeFilter, search, elapsed,
    announcement, toast, connection, connectionText, connectionHint, submitHint, lineCount, summary, filters, visibleResults,
    checkConnection, saveConnection, resetFile, selectFile, analyze, exportCsv,
  };
}
