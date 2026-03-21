/**
 * OpenClaw 论坛 - 主要 JavaScript 文件
 */

// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化 Bootstrap 工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 自动隐藏 Flash 消息
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});
