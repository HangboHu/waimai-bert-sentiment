export const DEFAULT_API = '/api/v1';

export function normalizeBaseUrl(value) {
  const normalized = value.trim().replace(/\/+$/, '');
  if (normalized.startsWith('/') && !normalized.startsWith('//') && !/[\\?#\s]/.test(normalized)) {
    return normalized;
  }
  try {
    const url = new URL(normalized);
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
      throw new Error();
    }
    return url.href.replace(/\/+$/, '');
  } catch {
    throw new Error('请填写以 / 开头的路径，或完整的 HTTP / HTTPS 地址。');
  }
}

export async function apiRequest(base, path, { body, timeout = 90000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(`${base}${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      headers: body !== undefined && !(body instanceof FormData) ? { 'Content-Type': 'application/json' } : {},
      body: body instanceof FormData ? body : body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok || payload?.code !== 200) {
      throw new Error(typeof payload?.message === 'string' ? payload.message : `服务暂不可用（${response.status}），请检查后端服务和连接设置。`);
    }
    return payload;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('分析服务响应超时，请减少评价数量后重试。');
    if (error instanceof TypeError) throw new Error('无法连接分析服务，请确认后端已启动，并检查连接设置。');
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export function validateResults(results, expectedCount) {
  if (!Array.isArray(results) || results.length !== expectedCount || results.some(item =>
    !item || typeof item.text !== 'string' || typeof item.label !== 'string' ||
    typeof item.is_certain !== 'boolean' || typeof item.confidence !== 'string' ||
    !/^\d+(?:\.\d+)?%$/.test(item.confidence) || Number.parseFloat(item.confidence) > 100
  )) {
    throw new Error('服务返回的分析结果格式不完整，请检查后端接口后重试。');
  }
  return results;
}
