/**
 * AccessEvent — вспомогательный JavaScript.
 * Все уведомления ВИЗУАЛЬНЫЕ (никаких звуковых сигналов) —
 * это требование доступности проекта.
 */
 
function showNotification(message, type = 'info') {
    const container = document.getElementById('notifications');
    if (!container) {
        return;
    }
 
    const notice = document.createElement('div');
    notice.className = 'notification notification-' + type;
    notice.setAttribute('role', 'status');
    notice.setAttribute('aria-live', 'polite');
    notice.textContent = message;
 
    container.appendChild(notice);
 
    setTimeout(function() {
        notice.remove();
    }, 4000);
}
 
function setupFormValidation() {
    const forms = document.querySelectorAll('.validate-me');
 
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
 
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#c5221f';
                    field.setAttribute('aria-invalid', 'true');
                } else {
                    field.style.borderColor = '#dadce0';
                    field.removeAttribute('aria-invalid');
                }
            });
 
            if (!valid) {
                e.preventDefault();
                showNotification(
                    'Пожалуйста, заполните обязательные поля',
                    'error'
                );
            }
        });
    });
}
 
document.addEventListener('DOMContentLoaded', function() {
    setupFormValidation();
});
 
if (typeof module !== 'undefined') {
    module.exports = { showNotification, setupFormValidation };
}