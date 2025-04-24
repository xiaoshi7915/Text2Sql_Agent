import { onMounted, onBeforeUnmount } from 'vue';

/**
 * 安全的 ResizeObserver 实现
 * 用于防止 "ResizeObserver loop completed with undelivered notifications" 错误
 */

// 防抖动函数，用于减少回调触发频率
const debounce = (fn, delay = 100) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

/**
 * 创建一个安全的 ResizeObserver 实例
 * @param {Function} callback - 当大小改变时要执行的回调函数
 * @param {number} delay - 防抖动延迟，默认为100ms
 * @returns {ResizeObserver} - 一个经过安全包装的 ResizeObserver 实例
 */
export function createSafeResizeObserver(callback, delay = 100) {
  // 使用防抖动来减少回调触发频率
  const debouncedCallback = debounce(callback, delay);
  
  // 如果浏览器支持 ResizeObserver
  if (typeof ResizeObserver !== 'undefined') {
    try {
      return new ResizeObserver((entries, observer) => {
        // 使用 requestAnimationFrame 来确保回调在正确的时机执行
        window.requestAnimationFrame(() => {
          if (entries && entries.length) {
            debouncedCallback(entries, observer);
          }
        });
      });
    } catch (e) {
      console.error('ResizeObserver 初始化失败:', e);
      // 返回一个空的观察者对象
      return {
        observe: () => {},
        unobserve: () => {},
        disconnect: () => {}
      };
    }
  }
  
  // 如果不支持，返回一个模拟的观察者
  return {
    observe: () => console.warn('ResizeObserver not supported in this browser'),
    unobserve: () => {},
    disconnect: () => {}
  };
}

/**
 * 在组件中使用的 ResizeObserver hook
 * 使用示例:
 * import { useResizeObserver } from '@/utils/resize-observer';
 * 
 * setup() {
 *   const elementRef = ref(null);
 *   
 *   useResizeObserver(elementRef, (entries) => {
 *     // 处理尺寸变化
 *     console.log('Size changed:', entries[0].contentRect);
 *   });
 *   
 *   return { elementRef };
 * }
 * 
 * @param {Ref} elementRef - Vue ref 引用 DOM 元素
 * @param {Function} callback - 尺寸变化回调
 * @param {number} delay - 防抖动延迟
 */
export function useResizeObserver(elementRef, callback, delay = 100) {
  let observer = null;
  
  // Vue 3 的 onMounted 钩子会自动导入
  onMounted(() => {
    // 确保 elementRef 存在并且有值
    if (!elementRef.value) return;
    
    observer = createSafeResizeObserver(callback, delay);
    observer.observe(elementRef.value);
  });
  
  // Vue 3 的 onBeforeUnmount 钩子会自动导入
  onBeforeUnmount(() => {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
  });
}

// 全局 ResizeObserver 错误处理
export function setupGlobalResizeObserverErrorHandler() {
  // 防止在SSR环境中运行
  if (typeof window === 'undefined') return;
  
  // 修复 Element Plus 中的 ResizeObserver 问题
  // 这是一个已知问题，当有大量组件同时调整大小时会发生
  const patchElementPlusResizeObserver = () => {
    // 仅在生产环境中执行，开发环境保留错误以便调试
    if (process.env.NODE_ENV === 'production') {
      const originalResizeObserver = window.ResizeObserver;
      
      if (!originalResizeObserver) return;
      
      // 用自定义的 ResizeObserver 替换原生的
      window.ResizeObserver = class PatchedResizeObserver extends originalResizeObserver {
        constructor(callback) {
          super((entries, observer) => {
            // 使用 requestAnimationFrame 来避免循环通知
            window.requestAnimationFrame(() => {
              if (entries && entries.length) {
                callback(entries, observer);
              }
            });
          });
        }
      };
    }
  };
  
  // 尝试应用 Element Plus 补丁
  try {
    patchElementPlusResizeObserver();
  } catch (e) {
    console.error('无法应用 Element Plus ResizeObserver 补丁:', e);
  }
  
  // 全局错误事件监听器
  window.addEventListener('error', (event) => {
    if (event.message && (
      event.message.includes('ResizeObserver loop') || 
      event.message.includes('ResizeObserver loop completed with undelivered notifications')
    )) {
      event.stopImmediatePropagation();
      event.preventDefault();
      return true;
    }
  }, true);
} 