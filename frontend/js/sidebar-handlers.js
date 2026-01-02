/**
 * Global Sidebar Handlers
 * Handles Sign Out and Delete Profile with confirmation modals across all pages.
 */

(function () {
    const API_BASE_URL = 'http://127.0.0.1:8000';

    // 1. Modal HTML Template
    const modalHTML = `
        <!-- Global Delete Account Modal -->
        <div id="globalDeleteModal" class="modal-overlay">
            <div class="modal-container">
                <h2 style="color: #FF4D4D;">Delete Account</h2>
                <p>This action cannot be undone. Please enter your password to confirm.</p>
                <div class="modal-form-group">
                    <label class="modal-form-label">Password</label>
                    <input type="password" class="modal-form-input" id="globalDeletePassword" placeholder="Enter your password">
                </div>
                <div class="modal-actions">
                    <button class="modal-btn modal-btn-cancel" id="closeDeleteModal">Cancel</button>
                    <button class="modal-btn modal-btn-danger" id="confirmDeleteBtn">Delete Account</button>
                </div>
            </div>
        </div>

        <!-- Global Sign Out Modal -->
        <div id="globalSignOutModal" class="modal-overlay">
            <div class="modal-container">
                <h2>Sign Out</h2>
                <p>Are you sure you want to sign out?</p>
                <div class="modal-actions">
                    <button class="modal-btn modal-btn-cancel" id="closeSignOutModal">Cancel</button>
                    <button class="modal-btn modal-btn-confirm" id="confirmSignOutBtn">Sign Out</button>
                </div>
            </div>
        </div>
    `;

    // 2. Inject Modals on Load
    document.addEventListener('DOMContentLoaded', () => {
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHTML;
        document.body.appendChild(modalContainer);

        setupEventListeners();
    });

    function setupEventListeners() {
        // Find sidebar links
        const signOutLinks = [
            document.getElementById('sign-out'),
            document.getElementById('sign-out-link')
        ];

        const deleteLinks = [
            document.getElementById('delete-profile'),
            document.getElementById('delete-profile-link')
        ];

        // Attach Sign Out Handlers
        signOutLinks.forEach(link => {
            if (link) {
                link.onclick = (e) => {
                    e.preventDefault();
                    document.getElementById('globalSignOutModal').style.display = 'flex';
                };
            }
        });

        // Attach Delete Handlers
        deleteLinks.forEach(link => {
            if (link) {
                link.onclick = (e) => {
                    e.preventDefault();
                    document.getElementById('globalDeleteModal').style.display = 'flex';
                };
            }
        });

        // Close buttons
        document.getElementById('closeDeleteModal').onclick = () => {
            document.getElementById('globalDeleteModal').style.display = 'none';
        };
        document.getElementById('closeSignOutModal').onclick = () => {
            document.getElementById('globalSignOutModal').style.display = 'none';
        };

        // Confirm buttons
        document.getElementById('confirmSignOutBtn').onclick = () => {
            localStorage.removeItem('user');
            window.location.href = 'login.html';
        };

        document.getElementById('confirmDeleteBtn').onclick = async () => {
            const user = JSON.parse(localStorage.getItem('user'));
            const password = document.getElementById('globalDeletePassword').value;

            if (!password) {
                alert('Please enter your password');
                return;
            }

            if (!user || !user.user_id) {
                alert('User session not found. Please log in again.');
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/delete_user/${user.user_id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: password })
                });

                const result = await response.json();
                if (result.status === 'success') {
                    localStorage.removeItem('user');
                    window.location.href = 'signup.html';
                } else {
                    alert(result.message || 'Failed to delete account');
                }
            } catch (error) {
                console.error('Error deleting account:', error);
                alert('An error occurred during account deletion.');
            }
        };
    }
})();
