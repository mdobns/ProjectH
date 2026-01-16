// Company Registration JavaScript

const API_BASE_URL = window.location.origin;

// Form elements
const form = document.getElementById('registerForm');
const submitBtn = document.getElementById('submitBtn');
const buttonText = submitBtn.querySelector('.button-text');
const buttonLoader = submitBtn.querySelector('.button-loader');
const alertContainer = document.getElementById('alertContainer');

// Auto-generate slug from company name
const companyNameInput = document.getElementById('companyName');
const companySlugInput = document.getElementById('companySlug');

companyNameInput.addEventListener('input', (e) => {
    const name = e.target.value;
    const slug = generateSlug(name);
    companySlugInput.value = slug;
});

function generateSlug(name) {
    return name
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
        .replace(/\s+/g, '-')          // Replace spaces with hyphens
        .replace(/-+/g, '-')           // Replace multiple hyphens with single
        .replace(/^-|-$/g, '');        // Remove leading/trailing hyphens
}

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Clear previous alerts
    clearAlerts();

    // Get form data
    const formData = new FormData(form);
    const data = {
        name: formData.get('name'),
        slug: formData.get('slug'),
        email: formData.get('email'),
        phone: formData.get('phone') || undefined,
        website: formData.get('website') || undefined,
        description: formData.get('description') || undefined,
        password: formData.get('password')
    };

    // Validate required fields
    if (!data.name || !data.slug || !data.email || !data.password) {
        showAlert('Please fill in all required fields', 'error');
        return;
    }

    // Validate email format
    if (!isValidEmail(data.email)) {
        showAlert('Please enter a valid email address', 'error');
        return;
    }

    // Validate slug format
    if (!isValidSlug(data.slug)) {
        showAlert('Company slug must contain only lowercase letters, numbers, and hyphens', 'error');
        return;
    }

    // Validate password length
    if (data.password.length < 8) {
        showAlert('Password must be at least 8 characters long', 'error');
        return;
    }

    // Show loading state
    setLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/companies/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            // Success
            showAlert(
                `✓ Account created successfully! Welcome to ChatBot SaaS, ${result.name}!`,
                'success'
            );

            // Reset form
            form.reset();

            // Redirect to admin login after 2 seconds
            setTimeout(() => {
                window.location.href = '/admin?registered=true&company=' + encodeURIComponent(result.slug);
            }, 2000);
        } else {
            // Error from API
            const errorMessage = result.detail || 'Registration failed. Please try again.';
            showAlert(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAlert('Network error. Please check your connection and try again.', 'error');
    } finally {
        setLoading(false);
    }
});

// Helper functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidSlug(slug) {
    const slugRegex = /^[a-z0-9-]+$/;
    return slugRegex.test(slug);
}

function setLoading(loading) {
    submitBtn.disabled = loading;
    if (loading) {
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'inline-flex';
    } else {
        buttonText.style.display = 'inline';
        buttonLoader.style.display = 'none';
    }
}

function showAlert(message, type = 'error') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;

    const icon = document.createElement('div');
    icon.className = 'alert-icon';

    if (type === 'success') {
        icon.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
        `;
    } else {
        icon.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
            </svg>
        `;
    }

    const messageDiv = document.createElement('div');
    messageDiv.textContent = message;

    alert.appendChild(icon);
    alert.appendChild(messageDiv);
    alertContainer.appendChild(alert);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function clearAlerts() {
    alertContainer.innerHTML = '';
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);

// Real-time slug validation
companySlugInput.addEventListener('input', (e) => {
    const slug = e.target.value;
    if (slug && !isValidSlug(slug)) {
        e.target.setCustomValidity('Only lowercase letters, numbers, and hyphens are allowed');
    } else {
        e.target.setCustomValidity('');
    }
});

// Real-time email validation
const emailInput = document.getElementById('email');
emailInput.addEventListener('blur', (e) => {
    const email = e.target.value;
    if (email && !isValidEmail(email)) {
        e.target.setCustomValidity('Please enter a valid email address');
    } else {
        e.target.setCustomValidity('');
    }
});

// Password strength indicator (optional enhancement)
const passwordInput = document.getElementById('password');
passwordInput.addEventListener('input', (e) => {
    const password = e.target.value;
    if (password.length > 0 && password.length < 8) {
        e.target.style.borderColor = '#f59e0b'; // warning color
    } else if (password.length >= 8) {
        e.target.style.borderColor = '#10b981'; // success color
    } else {
        e.target.style.borderColor = ''; // reset
    }
});

console.log('Company Registration Form Ready!');
