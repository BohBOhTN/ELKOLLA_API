document.addEventListener("DOMContentLoaded", () => {
    const invoiceForm = document.getElementById("invoice-form");
    const itemsTable = document.getElementById("items-table").getElementsByTagName("tbody")[0];
    const addItemButton = document.getElementById("add-item");
    const dateInput = document.getElementById("invoice_date");

    // Initialize Flatpickr for the date input
    flatpickr(dateInput, {
        dateFormat: "d/m/Y",
        locale: "fr",
        allowInput: true,
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

    // Validate all item rows
    function validateItems() {
        const rows = Array.from(itemsTable.querySelectorAll("tr"));
        if (rows.length === 0) {
            alert("At least one item must be added to the invoice.");
            return false;
        }

        for (const row of rows) {
            const referenceInput = row.querySelector("input[name='reference']");
            const designationInput = row.querySelector("input[name='designation']");
            const quantityInput = row.querySelector("input[name='quantity']");
            const unitPriceInput = row.querySelector("input[name='unitPrice']");

            console.log("Row validation:", {
                reference: referenceInput?.value.trim(),
                designation: designationInput?.value.trim(),
                quantity: quantityInput?.value.trim(),
                unitPrice: unitPriceInput?.value.trim(),
            });

            if (
                !referenceInput || !referenceInput.value.trim() ||
                !designationInput || !designationInput.value.trim() ||
                !quantityInput || isNaN(parseFloat(quantityInput.value.trim())) || parseFloat(quantityInput.value.trim()) <= 0 ||
                !unitPriceInput || isNaN(parseFloat(unitPriceInput.value.trim())) || parseFloat(unitPriceInput.value.trim()) <= 0
            ) {
                alert("All fields in the item rows must be filled.");
                return false;
            }
        }

        return true;
    }

    // Add event listener for adding items
    addItemButton.addEventListener("click", () => addItem());

    // Event delegation for table actions
    itemsTable.addEventListener("click", (e) => {
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
    invoiceForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const clientName = document.getElementById("client_name").value.trim();
        const vatNumber = document.getElementById("vat_number").value.trim();
        const address = document.getElementById("address").value.trim();
        const invoiceDate = document.getElementById("invoice_date").value.trim();

        if (!clientName || !vatNumber || !invoiceDate) {
            alert("Please fill in all required fields.");
            return;
        }

        if (!validateItems()) return;

        const items = Array.from(itemsTable.querySelectorAll("tr")).map((row) => ({
            reference: row.querySelector("input[name='reference']").value.trim(),
            designation: row.querySelector("input[name='designation']").value.trim(),
            quantity: parseInt(row.querySelector("input[name='quantity']").value.trim(), 10),
            unit_price: parseFloat(row.querySelector("input[name='unitPrice']").value.trim()),
        }));

        const invoiceData = {
            client_name: clientName,
            vat_number: vatNumber,
            address: address,
            invoice_date: invoiceDate,
            items: items,
        };

        localStorage.setItem("invoiceData", JSON.stringify(invoiceData));
        window.location.href = "review_invoice.html";
    });
});
