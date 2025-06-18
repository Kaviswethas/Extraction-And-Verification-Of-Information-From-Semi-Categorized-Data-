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
    
    // Reset text, file, and radio inputs
    form.querySelectorAll('input[type="text"], input[type="file"], input[type="radio"], input[type="date"]').forEach(input => {
        if (input.type === "radio") {
            input.checked = false;
        } else {
            input.value = ""; // Clears text, file, and date inputs
        }
    });

    // Reset dropdowns (select elements)
    form.querySelectorAll('select').forEach(select => {
        select.selectedIndex = 0; // Resets to the first option
    });

    // Hide disability details section on reset
    toggleDisabilityDetails();
}
