// Save the selected topic to localStorage
function saveToLocalStorage(selectedTopic) {
    if (selectedTopic) {
        localStorage.setItem('selectedTopic', selectedTopic);
    }
}

// Redirect to general page with the selected topic
function redirectToGeneralPage() {
    const selectedTopic = document.getElementById('dropdownInput').value;
    if (selectedTopic) {
        location.href = `general_page.html?topic=${encodeURIComponent(selectedTopic)}`;
    } else {
        showWarningMessage(); // Show warning if no topic is selected
    }
}

// Navigate to other pages and show warning if no topic is selected
function navigateTo(page) {
    const selectedTopic = document.getElementById('dropdownInput').value;
    if (selectedTopic) {
        saveToLocalStorage(selectedTopic); // Save to localStorage before navigation
        location.href = page;
    } else {
        showWarningMessage(); // Show warning if no topic is selected
    }
}

// Show a red warning message
function showWarningMessage() {
    const warningMessage = document.getElementById('warningMessage');
    warningMessage.style.display = 'block'; // Show the warning message
    setTimeout(() => {
        warningMessage.style.display = 'none'; // Hide it after 3 seconds
    }, 3000);
}

// Fetch data and initialize dropdown
window.onload = async function() {
    const labels = await fetchExcelData();
    populateSearchableDropdown(labels);

    // Check if a topic is already saved in localStorage and populate the input field
    const savedTopic = localStorage.getItem('selectedTopic');
    if (savedTopic) {
        document.getElementById('dropdownInput').value = savedTopic;
    }
};
