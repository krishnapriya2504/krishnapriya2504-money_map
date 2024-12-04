window.onload = async () => {
    const response = await fetch('/transactions');
    const transactions = await response.json(); // Backend should return a JSON array of transactions
    const container = document.getElementById('transactions');
    transactions.forEach((transaction) => {
        const div = document.createElement('div');
        div.innerHTML = `<strong>${transaction.description}</strong>: $${transaction.amount} (${transaction.type})`;
        container.appendChild(div);
    });
};


