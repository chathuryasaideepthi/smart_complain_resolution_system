function togglePassword() {
    const password = document.getElementById('passwordInput');
    const type = password.type === 'password' ? 'text' : 'password';
    password.type = type;
}
function togglePasswordField(fieldId) {
    const field = document.getElementById(fieldId);
    field.type = field.type === 'password' ? 'text' : 'password';
}
const darkToggle = document.getElementById('darkModeToggle');
if (darkToggle) {
    darkToggle.addEventListener('click', function () {
        document.body.classList.toggle('bg-dark');
        document.body.classList.toggle('text-light');
        document.querySelectorAll('.card').forEach(card => card.classList.toggle('bg-dark'));
        document.querySelectorAll('.card').forEach(card => card.classList.toggle('text-light'));
    });
}
