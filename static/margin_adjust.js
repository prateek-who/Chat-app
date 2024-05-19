const pElement = document.querySelector('p');
const passwordRetakeinElement = document.querySelector('.password-retakein');

if (window.getComputedStyle(pElement).display !== 'none') {
    passwordRetakeinElement.style.marginBottom = '10vh';
} else {
    passwordRetakeinElement.style.marginBottom = '25vh';
}
