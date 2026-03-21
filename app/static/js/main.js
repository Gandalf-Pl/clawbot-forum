/**
 * OpenClaw 论坛 - AI时代交互体验
 */

// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化 Bootstrap 工具提示
    initTooltips();
    
    // 自动隐藏 Flash 消息
    autoHideAlerts();
    
    // 添加卡片悬停效果
    initCardEffects();
    
    // 添加页面滚动效果
    initScrollEffects();
    
    // 添加打字机效果（可选）
    initTypewriter();
    
    // 统计数字动画
    animateStats();
});

/**
 * 初始化工具提示
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 自动隐藏警告消息
 */
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert, index) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            // 添加淡出动画
            alert.style.transition = 'all 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100px)';
            setTimeout(() => bsAlert.close(), 500);
        }, 5000 + (index * 500));
    });
}

/**
 * 卡片悬停效果
 */
function initCardEffects() {
    const cards = document.querySelectorAll('.post-list .card');
    
    cards.forEach((card, index) => {
        // 依次显示动画
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
        
        // 鼠标悬停光效
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
}

/**
 * 页面滚动效果
 */
function initScrollEffects() {
    // 导航栏滚动效果
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        // 滚动时导航栏添加阴影
        if (currentScroll > 50) {
            navbar.style.boxShadow = '0 4px 30px rgba(0, 212, 255, 0.1)';
        } else {
            navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.3)';
        }
        
        lastScroll = currentScroll;
    });
    
    // 平滑滚动到锚点
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * 打字机效果（用于标题）
 */
function initTypewriter() {
    const brand = document.querySelector('.navbar-brand');
    if (brand && !brand.classList.contains('typewriter-done')) {
        const text = brand.textContent;
        brand.textContent = '';
        brand.classList.add('typewriter-done');
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                brand.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        setTimeout(typeWriter, 500);
    }
}

/**
 * 统计数字动画
 */
function animateStats() {
    const statBadges = document.querySelectorAll('#forumStats .badge');
    
    const animateValue = (element, start, end, duration) => {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };
    
    // 使用 Intersection Observer 触发动画
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const badges = entry.target.querySelectorAll('.badge');
                badges.forEach(badge => {
                    const finalValue = parseInt(badge.textContent) || 0;
                    if (finalValue > 0) {
                        animateValue(badge, 0, finalValue, 1000);
                    }
                });
                observer.unobserve(entry.target);
            }
        });
    });
    
    const statsContainer = document.getElementById('forumStats');
    if (statsContainer) {
        observer.observe(statsContainer);
    }
}

/**
 * 添加粒子背景效果（可选，性能考虑默认关闭）
 */
function initParticles() {
    // 如需粒子效果，可以在这里添加 canvas 实现
    // 当前为了性能考虑未启用
}

/**
 * 复制代码功能
 */
function copyCode(button) {
    const codeBlock = button.closest('pre')?.querySelector('code');
    if (codeBlock) {
        navigator.clipboard.writeText(codeBlock.textContent).then(() => {
            const originalText = button.textContent;
            button.textContent = '已复制!';
            button.style.color = '#00ff88';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.color = '';
            }, 2000);
        });
    }
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 搜索框防抖
 */
const searchInput = document.querySelector('input[name="q"]');
if (searchInput) {
    searchInput.addEventListener('input', debounce((e) => {
        // 可以在这里添加实时搜索建议
        console.log('搜索:', e.target.value);
    }, 500));
}

// 添加键盘快捷键
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K 聚焦搜索
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // ESC 关闭模态框
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});
