document.addEventListener("DOMContentLoaded", () => {
    // Load data from localStorage
    const invoiceData = JSON.parse(localStorage.getItem("invoiceData"));

    if (!invoiceData) {
        alert("No invoice data found. Redirecting to form page.");
        window.location.href = "invoice_form.html";
        return;
    }

    // Populate review fields
    document.getElementById("review-client-name").textContent = invoiceData.client_name;
    document.getElementById("review-vat-number").textContent = invoiceData.vat_number;
    document.getElementById("review-address").textContent = invoiceData.address || "N/A";
    document.getElementById("review-invoice-date").textContent = invoiceData.invoice_date;

    const itemsTableBody = document.getElementById("review-items-table").querySelector("tbody");
    invoiceData.items.forEach(item => {
        const row = itemsTableBody.insertRow();
        row.innerHTML = `
            <td>${item.reference}</td>
            <td>${item.designation}</td>
            <td>${item.quantity}</td>
            <td>${item.unit_price.toFixed(3)}</td>
        `;
    });

    // Edit button functionality
    document.getElementById("edit-invoice").addEventListener("click", () => {
        window.location.href = "invoice_form.html";
    });

    // Confirm button functionality
    document.getElementById("confirm-invoice").addEventListener("click", async () => {
        try {
            const response = await fetch("http://127.0.0.1:8123/create_invoice", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(invoiceData),
            });

            if (response.ok) {
                const result = await response.json();
                alert("Invoice successfully created! Invoice Number: " + result.invoice_number);
                localStorage.removeItem("invoiceData");
                window.location.href = "invoices.html";
            } else {
                const errorData = await response.json();
                alert("Error: " + errorData.detail);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An unexpected error occurred.");
        }
    });
});
