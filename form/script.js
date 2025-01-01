document.addEventListener("DOMContentLoaded", () => {
    const invoiceForm = document.getElementById("invoice-form");
    const itemsTable = document.getElementById("items-table").getElementsByTagName("tbody")[0];
    const addItemButton = document.getElementById("add-item");
    const dateInput = document.getElementById("invoice_date");

    // Initialize Flatpickr for the date input
    flatpickr(dateInput, {
        dateFormat: "d/m/Y", // DD/MM/YYYY format
        locale: "fr", // French localization
        allowInput: true, // Allow manual input
    });

    // Add a new item row to the table
    function addItem() {
        const newRow = itemsTable.insertRow();
        newRow.innerHTML = `
            <td><input type="text" name="reference" placeholder="Reference" required></td>
            <td><input type="text" name="designation" placeholder="Designation" required></td>
            <td><input type="number" name="quantity" placeholder="Quantity" min="1" required></td>
            <td><input type="text" name="unitPrice" placeholder="0.000" required></td>
            <td><button type="button" class="remove-btn">Remove</button></td>
        `;
    }

    // Validate date format
    function validateDate(date) {
        const regex = /^\d{2}\/\d{2}\/\d{4}$/;
        return regex.test(date);
    }

    // Validate all item rows
    function validateItems() {
        const rows = Array.from(itemsTable.querySelectorAll("tr"));
        if (rows.length === 0) {
            alert("At least one item must be added to the invoice.");
            return false;
        }

        for (const row of rows) {
            const reference = row.querySelector("[name='reference']").value.trim();
            const designation = row.querySelector("[name='designation']").value.trim();
            const quantity = row.querySelector("[name='quantity']").value.trim();
            const unitPrice = row.querySelector("[name='unitPrice']").value.trim();

            if (!reference || !designation || !quantity || !unitPrice) {
                alert("All fields in the item rows must be filled.");
                return false;
            }
        }

        return true;
    }

    // Add event listener for adding items
    addItemButton.addEventListener("click", () => {
        addItem();
    });

    // Event delegation for table actions
    itemsTable.addEventListener("click", (e) => {
        // Remove row functionality
        if (e.target.classList.contains("remove-btn")) {
            e.target.closest("tr").remove();
        }
    });

    // Validate unit price input
    itemsTable.addEventListener("input", (e) => {
        if (e.target.name === "unitPrice") {
            const value = e.target.value;
            if (value.includes(",")) {
                alert("Unit price must use '.' as the decimal separator.");
                e.target.value = value.replace(",", ".");
            } else if (!/^\d+(\.\d{0,3})?$/.test(value)) {
                e.target.value = value.slice(0, -1); // Remove last character if invalid
            }
        }
    });

    // Handle form submission
    invoiceForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const clientName = document.getElementById("client_name").value.trim();
        const vatNumber = document.getElementById("vat_number").value.trim();
        const address = document.getElementById("address").value.trim();
        const invoiceDate = document.getElementById("invoice_date").value.trim();

        // Validate required fields
        if (!clientName || !vatNumber || !invoiceDate) {
            alert("Please fill in all required fields.");
            return;
        }

        if (!validateDate(invoiceDate)) {
            alert("Invalid date format. Please use DD/MM/YYYY.");
            return;
        }

        if (!validateItems()) {
            return; // Validation for items failed
        }

        const items = Array.from(itemsTable.querySelectorAll("tr")).map((row) => ({
            reference: row.querySelector("[name='reference']").value.trim(),
            designation: row.querySelector("[name='designation']").value.trim(),
            quantity: parseInt(row.querySelector("[name='quantity']").value.trim(), 10),
            unit_price: parseFloat(row.querySelector("[name='unitPrice']").value.trim()),
        }));

        const invoiceData = {
            client_name: clientName,
            vat_number: vatNumber,
            address: address,
            invoice_date: invoiceDate,
            items: items,
        };

        try {
            const response = await fetch("/create_invoice", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(invoiceData),
            });

            if (response.ok) {
                const responseData = await response.json();
                alert("Invoice created successfully! Invoice Number: " + responseData.invoice_number);
                invoiceForm.reset();
                itemsTable.innerHTML = ""; // Clear the items table
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
