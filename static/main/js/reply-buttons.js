// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    // Get all reply buttons
    var replyButtons = document.querySelectorAll('.comment-reply-link');

    // Add click event listener to each reply button
    replyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Get the ID of the reply form to show
            var replyFormId = this.getAttribute('data-reply-form');
            var replyForm = document.getElementById(replyFormId);

            // Toggle the display of the reply form
            if (replyForm.style.display === 'none' || replyForm.style.display === '') {
                replyForm.style.display = 'block';
            } else {
                replyForm.style.display = 'none';
            }
        });
    });
});


