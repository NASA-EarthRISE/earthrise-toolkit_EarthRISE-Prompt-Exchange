$(document).ready(function() {
    // CSRF token setup for AJAX
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Upvote functionality - using event delegation for dynamic content
    $(document).on('click', '.upvote-btn:not(:disabled)', function(e) {
        e.preventDefault();
        e.stopPropagation(); // Prevent card click from triggering

        const button = $(this);
        const promptSlug = button.data('slug');
        const icon = button.find('i');
        const countSpan = button.find('.upvote-count');

        // Disable button during request
        button.prop('disabled', true);

        $.ajax({
            url: `/prompts/${promptSlug}/upvote/`,
            type: 'POST',
            success: function(data) {
                if (data.upvoted) {
                    button.addClass('active');
                    icon.removeClass('bi-hand-thumbs-up').addClass('bi-hand-thumbs-up-fill');
                } else {
                    button.removeClass('active');
                    icon.removeClass('bi-hand-thumbs-up-fill').addClass('bi-hand-thumbs-up');
                }
                countSpan.text(data.upvote_count);
                button.prop('disabled', false);
            },
            error: function(xhr) {
                if (xhr.status === 403 || xhr.status === 401) {
                    // User not logged in
                    window.location.href = '/login/?next=' + window.location.pathname;
                } else {
                    alert('An error occurred. Please try again.');
                }
                button.prop('disabled', false);
            }
        });
    });

    // Favorite functionality
    $(document).on('click', '.favorite-btn:not(:disabled)', function(e) {
        e.preventDefault();
        e.stopPropagation();

        const button = $(this);
        const promptSlug = button.data('slug');
        const icon = button.find('i');

        button.prop('disabled', true);

        $.ajax({
            url: `/prompts/${promptSlug}/favorite/`,
            type: 'POST',
            success: function(data) {
                if (data.favorited) {
                    button.addClass('active');
                    icon.removeClass('bi-star').addClass('bi-star-fill');
                } else {
                    button.removeClass('active');
                    icon.removeClass('bi-star-fill').addClass('bi-star');
                }
                button.prop('disabled', false);
            },
            error: function(xhr) {
                if (xhr.status === 403 || xhr.status === 401) {
                    window.location.href = '/login/?next=' + window.location.pathname;
                } else {
                    alert('An error occurred. Please try again.');
                }
                button.prop('disabled', false);
            }
        });
    });

    // Copy prompt text to clipboard
    $('.copy-prompt-btn').on('click', function() {
        const promptText = $('#prompt-text').text();
        const button = $(this);

        navigator.clipboard.writeText(promptText).then(function() {
            const originalText = button.html();
            button.html('<i class="bi bi-check"></i> Copied!');
            button.addClass('btn-success').removeClass('btn-outline-secondary');

            setTimeout(function() {
                button.html(originalText);
                button.removeClass('btn-success').addClass('btn-outline-secondary');
            }, 2000);
        }).catch(function(err) {
            alert('Failed to copy text');
            console.error('Copy failed:', err);
        });
    });

    // Search functionality with debounce
    let searchTimeout;
    $('#search-input').on('input', function() {
        clearTimeout(searchTimeout);
        const searchForm = $(this).closest('form');

        searchTimeout = setTimeout(function() {
            searchForm.submit();
        }, 500);
    });

    // Smooth scroll to comments
    $('.scroll-to-comments').on('click', function(e) {
        e.preventDefault();
        $('html, body').animate({
            scrollTop: $('#comments-section').offset().top - 100
        }, 500);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Form validation feedback
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        if (!submitBtn.hasClass('upvote-btn') && !submitBtn.hasClass('favorite-btn')) {
            submitBtn.prop('disabled', true);
            submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Submitting...');
        }
    });

    // Tag input formatting
    $('#id_tags').on('blur', function() {
        let tags = $(this).val().split(',').map(tag => tag.trim()).filter(tag => tag);
        $(this).val(tags.join(', '));
    });

    // Prevent card click from interfering with button clicks
    $('.prompt-card').on('click', function(e) {
        if (!$(e.target).closest('.upvote-btn, .favorite-btn, a, button').length) {
            const link = $(this).find('.card-title a').attr('href');
            if (link) {
                window.location.href = link;
            }
        }
    });
});