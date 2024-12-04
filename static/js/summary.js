window.onload = async () => {
    const response = await fetch('/summary'); // Backend returns income, expenses, and balance
    const summary = await response.json();
    document.getElementById('total-income').textContent = `$${summary.income}`;
    document.getElementById('total-expense').textContent = `$${summary.expense}`;
    document.getElementById('balance').textContent = `$${summary.balance}`;
};

