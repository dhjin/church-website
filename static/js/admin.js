// Sermon inline editing functions
function editSermon(sermonId) {
    // Hide all other edit forms
    document.querySelectorAll('.sermon-edit-row').forEach(row => {
        row.style.display = 'none';
    });
    document.querySelectorAll('.sermon-row').forEach(row => {
        row.style.display = '';
    });

    // Show edit form for this sermon
    const displayRow = document.querySelector(`tr[data-sermon-id="${sermonId}"]`);
    const editRow = document.getElementById(`edit-${sermonId}`);

    if (displayRow && editRow) {
        displayRow.style.display = 'none';
        editRow.style.display = '';
    }
}

function cancelEdit(sermonId) {
    const displayRow = document.querySelector(`tr[data-sermon-id="${sermonId}"]`);
    const editRow = document.getElementById(`edit-${sermonId}`);

    if (displayRow && editRow) {
        displayRow.style.display = '';
        editRow.style.display = 'none';
    }
}
