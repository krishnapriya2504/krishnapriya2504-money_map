const form = document.getElementById('income-form'); // For income.html (use 'expense-form' for expense.html)
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('description').value;
    const amount = parseFloat(document.getElementById('amount').value);
    await fetch('/income', { // Use '/expense' for expense.html
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, amount }),
    });
    alert('Data added successfully!');
    form.reset();
});
