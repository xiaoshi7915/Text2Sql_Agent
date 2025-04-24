/**
 * Element Plus 组件库补丁
 * 解决常见问题，如 ResizeObserver 循环错误
 */

/**
 * 修复 Element Plus 中的 ResizeObserver 循环错误
 * 这是一个已知问题，当页面中有大量 Element Plus 组件同时调整大小时会发生
 */
export function patchElementPlusResizeObserver() {
  if (typeof window === 'undefined') return;

  // 自定义 ResizeObserver 的方法
  const patchResizeObserver = () => {
    const originalResizeObserver = window.ResizeObserver;
    
    if (!originalResizeObserver) return;
    
    // 修改 ResizeObserver 的实现
    window.ResizeObserver = class PatchedResizeObserver extends originalResizeObserver {
      constructor(callback) {
        // 使用防抖的回调函数
        const debouncedCallback = (entries, observer) => {
          window.requestAnimationFrame(() => {
            if (entries && entries.length) {
              callback(entries, observer);
            }
          });
        };
        
        super(debouncedCallback);
      }
    };
  };
  
  // 设置样式修复
  const applyStyleFixes = () => {
    // 某些 Element Plus 组件的样式会导致布局抖动
    // 这里可以添加覆盖样式以减少问题
    
    // 创建样式元素
    const style = document.createElement('style');
    style.innerHTML = `
      /* 防止内容溢出导致的布局抖动 */
      .el-select-dropdown, .el-dropdown-menu {
        overflow: hidden !important;
      }
      
      /* 稳定弹出框大小 */
      .el-popover {
        max-height: 80vh;
        max-width: 80vw;
        overflow: auto;
      }
      
      /* 稳定表格列宽 */
      .el-table__header, .el-table__body {
        table-layout: fixed !important;
      }
    `;
    
    // 添加到文档中
    document.head.appendChild(style);
  };
  
  // 应用补丁
  try {
    patchResizeObserver();
    applyStyleFixes();
    
    console.info('成功应用 Element Plus 补丁');
  } catch (e) {
    console.error('应用 Element Plus 补丁失败:', e);
  }
}

/**
 * 应用所有 Element Plus 补丁
 */
export function applyElementPlusPatches() {
  patchElementPlusResizeObserver();
} 