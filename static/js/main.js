/**
 * 华为云存储服务控制系统 - 商业版
 * 主JavaScript文件
 */

// 在DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化警告框自动关闭
    initAlertDismiss();
    
    // 初始化侧边栏折叠功能
    initSidebar();
    
    // 初始化数据表格
    initDataTables();
    
    // 注册事件监听器
    registerEventListeners();
    
    // 检查会话状态
    checkSessionStatus();
});

/**
 * 初始化Bootstrap工具提示
 */
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 初始化警告框自动关闭
 */
function initAlertDismiss() {
    // 5秒后自动关闭警告框
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
}

/**
 * 初始化侧边栏折叠功能
 */
function initSidebar() {
    var sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
            localStorage.setItem('sidebar-collapsed', document.body.classList.contains('sidebar-collapsed'));
        });
        
        // 从本地存储恢复侧边栏状态
        if (localStorage.getItem('sidebar-collapsed') === 'true') {
            document.body.classList.add('sidebar-collapsed');
        }
    }
}

/**
 * 初始化数据表格
 */
function initDataTables() {
    var tables = document.querySelectorAll('.data-table');
    tables.forEach(function(table) {
        if (typeof $.fn.DataTable !== 'undefined') {
            $(table).DataTable({
                responsive: true,
                language: {
                    url: '/static/js/dataTables.chinese.json'
                },
                pageLength: 10,
                lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "全部"]]
            });
        }
    });
}

/**
 * 注册事件监听器
 */
function registerEventListeners() {
    // 确认删除对话框
    var confirmDeleteButtons = document.querySelectorAll('.confirm-delete');
    confirmDeleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('您确定要删除此项吗？此操作不可逆。')) {
                e.preventDefault();
            }
        });
    });
    
    // 表单验证
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // 动态表单字段
    var addFieldButtons = document.querySelectorAll('.add-field');
    addFieldButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var container = document.getElementById(button.dataset.container);
            var template = document.getElementById(button.dataset.template).innerHTML;
            var index = container.children.length;
            var newField = template.replace(/\{index\}/g, index);
            
            var div = document.createElement('div');
            div.innerHTML = newField;
            container.appendChild(div.firstChild);
            
            // 重新初始化新添加字段的工具提示
            initTooltips();
        });
    });
}

/**
 * 检查会话状态
 */
function checkSessionStatus() {
    // 每5分钟检查一次会话状态
    setInterval(function() {
        fetch('/api/session/check', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (!data.valid) {
                // 会话已过期，显示提示并在5秒后重定向到登录页面
                showSessionExpiredWarning();
                setTimeout(function() {
                    window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                }, 5000);
            }
        })
        .catch(error => {
            console.error('会话检查失败:', error);
        });
    }, 300000); // 5分钟 = 300000毫秒
}

/**
 * 显示会话过期警告
 */
function showSessionExpiredWarning() {
    var warningDiv = document.createElement('div');
    warningDiv.className = 'alert alert-warning alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    warningDiv.setAttribute('role', 'alert');
    warningDiv.innerHTML = `
        <strong>会话已过期！</strong> 您将在5秒后被重定向到登录页面。
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(warningDiv);
}

/**
 * 格式化日期时间
 * @param {string|Date} dateTime - 日期时间字符串或Date对象
 * @param {string} format - 格式化模式，默认为'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期时间字符串
 */
function formatDateTime(dateTime, format = 'YYYY-MM-DD HH:mm:ss') {
    if (!dateTime) return '';
    
    var date = typeof dateTime === 'string' ? new Date(dateTime) : dateTime;
    
    if (isNaN(date.getTime())) return '';
    
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    var hours = String(date.getHours()).padStart(2, '0');
    var minutes = String(date.getMinutes()).padStart(2, '0');
    var seconds = String(date.getSeconds()).padStart(2, '0');
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数，默认为2
 * @returns {string} 格式化后的文件大小字符串
 */
function formatFileSize(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 显示加载中遮罩
 * @param {string} message - 显示的消息，默认为"加载中..."
 */
function showLoading(message = '加载中...') {
    var loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-spinner"></div>
        <div class="loading-message">${message}</div>
    `;
    document.body.appendChild(loadingOverlay);
    document.body.classList.add('loading');
}

/**
 * 隐藏加载中遮罩
 */
function hideLoading() {
    var loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
        document.body.classList.remove('loading');
    }
}

/**
 * 发送API请求
 * @param {string} url - API端点URL
 * @param {string} method - HTTP方法，默认为'GET'
 * @param {Object} data - 请求数据，默认为null
 * @param {boolean} showLoader - 是否显示加载中遮罩，默认为true
 * @returns {Promise} 请求Promise
 */
function apiRequest(url, method = 'GET', data = null, showLoader = true) {
    if (showLoader) {
        showLoading();
    }
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .finally(() => {
            if (showLoader) {
                hideLoading();
            }
        });
}

/**
 * 显示通知消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型，可选值：success, info, warning, error，默认为info
 * @param {number} duration - 显示时长（毫秒），默认为3000
 */
function showNotification(message, type = 'info', duration = 3000) {
    // 创建通知元素
    var notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            ${type === 'success' ? '<i class="bi bi-check-circle-fill"></i>' : 
              type === 'warning' ? '<i class="bi bi-exclamation-triangle-fill"></i>' : 
              type === 'error' ? '<i class="bi bi-x-circle-fill"></i>' : 
              '<i class="bi bi-info-circle-fill"></i>'}
        </div>
        <div class="notification-content">${message}</div>
        <button class="notification-close"><i class="bi bi-x"></i></button>
    `;
    
    // 添加到通知容器
    var container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // 添加关闭按钮事件
    var closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', function() {
        notification.classList.add('notification-hiding');
        setTimeout(function() {
            notification.remove();
        }, 300);
    });
    
    // 自动关闭
    setTimeout(function() {
        notification.classList.add('notification-hiding');
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, duration);
    
    // 显示动画
    setTimeout(function() {
        notification.classList.add('notification-show');
    }, 10);
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise} 复制操作的Promise
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text)
            .then(() => {
                showNotification('已复制到剪贴板', 'success');
                return true;
            })
            .catch(err => {
                console.error('复制失败:', err);
                showNotification('复制失败', 'error');
                return false;
            });
    } else {
        // 兼容性处理
        var textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            var successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            if (successful) {
                showNotification('已复制到剪贴板', 'success');
                return Promise.resolve(true);
            } else {
                showNotification('复制失败', 'error');
                return Promise.resolve(false);
            }
        } catch (err) {
            document.body.removeChild(textArea);
            console.error('复制失败:', err);
            showNotification('复制失败', 'error');
            return Promise.resolve(false);
        }
    }
}

/**
 * 导出表格数据为CSV
 * @param {HTMLElement} table - 表格元素
 * @param {string} filename - 文件名，默认为'export.csv'
 */
function exportTableToCSV(table, filename = 'export.csv') {
    var rows = table.querySelectorAll('tr');
    var csv = [];
    
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (var j = 0; j < cols.length; j++) {
            // 获取单元格文本并处理引号
            var text = cols[j].innerText.replace(/"/g, '""');
            row.push('"' + text + '"');
        }
        
        csv.push(row.join(','));
    }
    
    // 下载CSV文件
    downloadCSV(csv.join('\n'), filename);
}

/**
 * 下载CSV文件
 * @param {string} csv - CSV内容
 * @param {string} filename - 文件名
 */
function downloadCSV(csv, filename) {
    var csvFile = new Blob([csv], {type: 'text/csv;charset=utf-8;'});
    var downloadLink = document.createElement('a');
    
    downloadLink.href = URL.createObjectURL(csvFile);
    downloadLink.download = filename;
    downloadLink.style.display = 'none';
    
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖处理后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 限制时间（毫秒）
 * @returns {Function} 节流处理后的函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
