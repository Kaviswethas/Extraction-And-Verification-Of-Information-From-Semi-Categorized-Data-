document.addEventListener('DOMContentLoaded', () => {
    // Ensure disability details are hidden on page load
    toggleDisabilityDetails();
});

function toggleDisabilityDetails() {
    const yesSelected = document.querySelector('input[name="pwd"][value="yes"]').checked;
    const disabilityDetails = document.getElementById('disabilityDetails');
    disabilityDetails.style.display = yesSelected ? 'block' : 'none';
}

function resetForm() {
    // Reset all input fields
    const form = document.querySelector('.container');
    form.querySelectorAll('input[type="text"], input[type="file"], input[type="radio"]').forEach(input => {
        if (input.type === "radio") {
            input.checked = false;
        } else {
            input.value = "";
        }
    });
    // Hide disability details section on reset
    toggleDisabilityDetails();
}