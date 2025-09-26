// COMPLETE REPLACEMENT - This WILL work if implemented correctly

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing mark handlers...');
    
    // Use event delegation to catch all mark forms, including dynamically added ones
    document.addEventListener('submit', function(e) {
        // Check if the submitted form has the mark-form class
        if (e.target && e.target.classList.contains('mark-form')) {
            console.log('Mark form submission intercepted!');
            
            // PREVENT DEFAULT FORM SUBMISSION
            e.preventDefault();
            e.stopImmediatePropagation();
            e.stopPropagation();
            
            handleMarkToggle(e.target);
            return false; // Extra prevention
        }
    }, true); // Use capture phase
    
    // Also add click handler directly to buttons as backup
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('mark-btn')) {
            console.log('Mark button clicked directly!');
            
            e.preventDefault();
            e.stopImmediatePropagation();
            e.stopPropagation();
            
            const form = e.target.closest('form');
            if (form && form.classList.contains('mark-form')) {
                handleMarkToggle(form);
            }
            return false;
        }
    }, true);

    function handleMarkToggle(form) {
        console.log('Handling mark toggle for form:', form.action);
        
        const button = form.querySelector('button[type="submit"]');
        const originalHTML = button.innerHTML;
        const originalClasses = button.className;
        const originalTitle = button.title;
        
        // Disable button and show loading
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
        button.disabled = true;
        
        // Get CSRF token
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        
        console.log('Making AJAX request to:', form.action);
        
        // Make AJAX request
        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'csrfmiddlewaretoken=' + encodeURIComponent(csrfToken),
            credentials: 'same-origin'
        })
        .then(response => {
            console.log('Response received:', response.status, response.headers.get('content-type'));
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type') || '';
            if (!contentType.includes('application/json')) {
                console.error('Expected JSON, got:', contentType);
                throw new Error('Server returned HTML instead of JSON - check Django view!');
            }
            
            return response.json();
        })
        .then(data => {
            console.log('JSON data received:', data);
            
            if (data.success) {
                if (data.action === 'created') {
                    // Mark created - show marked state
                    button.innerHTML = '<em class="icon ni ni-check"></em>';
                    button.className = 'btn btn-warning mark-btn marked';
                    button.title = 'حذف نشان';
                    button.style.marginLeft = '5px';
                    
                    // showInlineMessage(button, 'ساخته شد', 'success');
                    console.log('Mark created - button updated to marked state');
                    
                } else if (data.action === 'deleted') {
                    // Mark deleted - show unmarked state
                    button.innerHTML = '<em class="icon ni ni-bookmark"></em>';
                    button.className = 'btn btn-gray mark-btn';
                    button.title = 'افزودن نشان';
                    button.style.marginLeft = '0';
                    
                    // showInlineMessage(button, 'حذف شد', 'success');
                    console.log('Mark deleted - button updated to unmarked state');
                }
                
                // Re-enable button
                button.disabled = false;
                
            } else {
                console.error('Server returned error:', data.message);
                showInlineMessage(button, data.message || 'خطا', 'error');
                
                // Restore original state
                button.innerHTML = originalHTML;
                button.className = originalClasses;
                button.title = originalTitle;
                button.disabled = false;
            }
        })
        .catch(error => {
            console.error('Request failed:', error);
            showInlineMessage(button, 'خطا در ارتباط', 'error');
            
            // Restore original state
            button.innerHTML = originalHTML;
            button.className = originalClasses;  
            button.title = originalTitle;
            button.disabled = false;
        });
    }

    function showInlineMessage(button, message, type) {
        // Remove existing message
        const existing = button.parentNode.querySelector('.mark-message');
        if (existing) {
            existing.remove();
        }

        // Create new message
        const messageEl = document.createElement('span');
        messageEl.className = 'mark-message';
        messageEl.textContent = message;
        messageEl.style.cssText = `
            display: inline-block;
            margin-right: 8px;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.7em;
            font-weight: bold;
            color: white;
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
            animation: fadeInOut 3s ease forwards;
            white-space: nowrap;
            z-index: 1000;
        `;

        // Insert message
        button.parentNode.insertBefore(messageEl, button.nextSibling);

        // Auto-remove
        setTimeout(() => {
            if (messageEl && messageEl.parentNode) {
                messageEl.remove();
            }
        }, 3000);
    }
});

// Ensure CSS is added
if (!document.getElementById('mark-styles')) {
    const style = document.createElement('style');
    style.id = 'mark-styles';
    style.textContent = `
        .mark-btn {
            transition: all 0.2s ease;
            position: relative;
        }
        
        .mark-btn:hover:not(:disabled) {
            transform: scale(1.05);
        }
        
        .mark-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        @keyframes fadeInOut {
            0% { opacity: 0; transform: scale(0.9); }
            20% { opacity: 1; transform: scale(1); }
            80% { opacity: 1; transform: scale(1); }
            100% { opacity: 0; transform: scale(0.9); }
        }
        
        .mark-message {
            pointer-events: none;
        }
    `;
    document.head.appendChild(style);
}

