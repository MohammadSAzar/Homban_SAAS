document.addEventListener('DOMContentLoaded', function() {
    const markForms = document.querySelectorAll('.mark-form');

    markForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const button = this.querySelector('button[type="submit"]');
            const originalText = button.innerHTML;
            button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال پردازش...';
            button.disabled = true;

            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new FormData(this)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showToast('success', data.message);

                    // Optionally change button appearance
                    button.innerHTML = '<em class="icon ni ni-star-fill"></em> نشان شده';
                    button.classList.add('btn-success');
                    button.classList.remove('btn-primary');
                } else {
                    showToast('error', data.message);
                    button.innerHTML = originalText;
                    button.disabled = false;
                }
            })
            .catch(error => {
                showToast('error', 'خطا در ارتباط با سرور');
                button.innerHTML = originalText;
                button.disabled = false;
            });
        });
    });

    function showToast(type, message) {
        // Implement your toast notification system here
        // For example, using Bootstrap toasts
        console.log(type + ': ' + message);
    }
});


