import(window.config.firebaseFunctionScriptUrl)
    .then(module => {
        const {fetchAllUsers} = module;
        let allUsers = [];
        let usersTablePaginator = null;
        let filteredUsers = [];
        let sortPriority = [];
        async function init() {
            showOverlay();
            allUsers = await fetchAllUsers();

            addEventListenersToUsers();
            addFilterInputs();
            addEventListenersToFilterInputs();

            const wrapper = document.querySelector('[data-table-id="users-control-table"]');
            if (!usersTablePaginator) {
                usersTablePaginator = initPagination(
                  wrapper,
                  allUsers,
                  buildUsersControlTable
                );
              } else {
                usersTablePaginator.setData(allUsers);
            }
            hideOverlay();
        }

        function addEventListenersToUsers() {
            const headers = document.querySelectorAll('.arrow-sorting');
            headers.forEach((header, index) => {
                header.addEventListener('click', () => {
                    updateSortPriority(index);
                    adjustSortIcon(index); // Use the updated function here
                    sortUsers(getActualArray());
                });
            });
        }

        function updateSortPriority(columnIndex) {
            const existingPriority = sortPriority.findIndex(sp => sp.columnIndex === columnIndex);
            if (existingPriority === -1) {
                // Add new sort priority if not already present
                sortPriority.push({ columnIndex: columnIndex, direction: 'asc' });
            } else {
                // If clicked again, update direction or remove if it's the third click
                if (sortPriority[existingPriority].direction === 'asc') {
                    sortPriority[existingPriority].direction = 'desc';
                } else {
                    sortPriority.splice(existingPriority, 1); // Remove this sort priority
                }
            }
        }

        function adjustSortIcon(columnIndex) {
            const arrows = document.querySelectorAll('.sort-arrow');
            const currentArrow = arrows[columnIndex];
            const existingPriority = sortPriority.find(sp => sp.columnIndex === columnIndex);
            const direction = existingPriority ? existingPriority.direction : null;
            // Set current arrow based on direction
            if (direction === 'asc') {
                currentArrow.classList.remove('fa-arrow-up','fa-x' );
                currentArrow.classList.add( "fa-arrow-down"); //= '↓'; // Down arrow indicates ascending sort

            } else if (direction === 'desc') {
                currentArrow.classList.remove('fa-arrow-down','fa-x' );
                currentArrow.classList.add("fa-arrow-up");// = '↑'; // Up arrow indicates descending sort
            } else {
                currentArrow.classList.remove('fa-arrow-down', 'fa-arrow-up','fa-x' );
                currentArrow.classList.add("fa-x");
            }
        }

        function sortUsers(array) {
            array.sort((a, b) => {
                for (let i = 0; i < sortPriority.length; i++) {
                    const { columnIndex, direction } = sortPriority[i];
                    let valA, valB;
                    // Switch statement to assign valA and valB based on columnIndex
                    switch (columnIndex) {
                        case 0: // User ID
                            valA = a.userId; valB = b.userId;
                            break;
                        case 1: // Customer
                           valA = a.first_name || ""; valB = b.first_name || "";
                            break;
                        case 2: // First Name
                            valA = a.last_name || ""; valB = b.last_name || "";
                            break;
                        case 3: // Last Name
                            valA = a.third_name || ""; valB = b.third_name || "";
                            break;
                        case 4: // Email
                            valA = a.email; valB = b.email;
                            break;
                        case 5: // school
                            valA = a.school || ""; valB = b.school || "";
                            break;
                        case 6: // Enabled
                             valA = a.Enabled || false ? "Yes" : "No"; valB = b.Enabled || false ? "Yes" : "No";
                            break;
                        case 7: // paralel
                            valA = a.paralel || ""; valB = b.paralel || "";
                            break;
                        case 8: // RegistrationDate
                            valA = a.registrationDate ? new Date(a.registrationDate) : new Date(0);
                            valB = b.registrationDate ? new Date(b.registrationDate) : new Date(0);
                            break;

                        // Add additional cases as needed.
                    }

                    let comparison = 0;
                    if (valA < valB) {
                        comparison = -1;
                    } else if (valA > valB) {
                        comparison = 1;
                    }

                    if (comparison !== 0) {
                        return direction === 'asc' ? comparison : -comparison;
                    }
                }
                return 0; // If all priorities compare equal
            });

            usersTablePaginator.setData(getActualArray());
            document.getElementById('remove-filters').style.display = 'inline';
        }

        function filterUsers() {
            const inputs = document.querySelectorAll('.filter-input');
            // Ensure `allOrders` contains your orders data
            filteredUsers = allUsers.filter(order => {
                return Array.from(inputs).every((input, index) => {
                    if (!input.value.trim()) return true; // Skip empty inputs

                    const columnName = input.getAttribute('data-column');
                    let orderValue = order[input.getAttribute('data-column')]; // Adjust based on your data keys

                    // Special handling for the "Total" column with comparison operators
                    if (columnName === "price") {
                        const operatorSelect = input.previousSibling; // Assuming the select is right before the input
                        const operator = operatorSelect.value;
                        const value = parseFloat(input.value);
                        orderValue = parseFloat(orderValue);

                        switch (operator) {
                            case '>': return orderValue > value;
                            case '<': return orderValue < value;
                            case '>=': return orderValue >= value;
                            case '<=': return orderValue <= value;
                            case '==': return orderValue === value;
                            default: return true;
                        }
                    } else if (columnName === "registrationDate" && input.getAttribute('data-range')) {
                        const orderDate = new Date(orderValue ? (order.registrationDate) : 0);
                        if (input.getAttribute('data-range') === 'from') {
                            const fromDate = new Date(input.value);
                            return fromDate <= orderDate;
                        } else if (input.getAttribute('data-range') === 'to') {
                            const toDate = new Date(input.value);
                            toDate.setHours(23, 59, 59, 999); // Set to the end of the day for 'to' date
                            return toDate >= orderDate;
                        }
                    }
                    else { // Textual data
                        return orderValue.toString().toLowerCase().includes(input.value.toLowerCase());
                    }
                });
            });

            usersTablePaginator.setData(filteredUsers); // Rebuild the table with the filtered data
            document.getElementById('remove-filters').style.display = 'inline';
        }

        function addFilterInputs() {
            const table = document.getElementById('usersTable');
            const headerRow = table.querySelector('thead tr');
            const filterRow = document.createElement('tr');

            Array.from(headerRow.cells).forEach((cell, index) => {
                const filterCell = document.createElement('th');

                if (index > 0 && index < headerRow.cells.length - 1) { // Skip first and last columns
                    if (cell.textContent.trim() === "Total") {
                        filterCell.classList.add('header-total-cell');
                        const select = document.createElement('select');
                        ["==", ">", "<", ">=", "<="].forEach(op => {
                            const option = document.createElement('option');
                            option.value = op;
                            option.textContent = op;
                            select.appendChild(option);
                        });
                        filterCell.appendChild(select);
                    }

                    let data_column = "";
                    if (cell.textContent.trim() === "User ID")
                    {
                        data_column="userId";
                    }
                    else if(cell.textContent.trim() === "First Name"){
                        data_column="first_name";
                    }
                    else if(cell.textContent.trim() === "Last name"){
                        data_column="last_name";
                    }
                    else if(cell.textContent.trim() === "Third name"){
                        data_column="third_name";
                    }
                    else if(cell.textContent.trim() === "Email"){
                        data_column="email";
                    }
                    else if(cell.textContent.trim() === "School"){
                        data_column="school";
                    }
                    else if(cell.textContent.trim() === "Enabled"){
                        data_column="Enabled";
                    }
                    else if(cell.textContent.trim() === "Paralel"){
                        data_column="paralel";
                    }
                    else if(cell.textContent.trim() === "Registration Date"){
                        data_column="registrationDate";
                    }

                    if (cell.textContent.trim() === "Registration Date") {
                        // Create "From" date input
                        const div_input_from = document.createElement('div');
                        const label_input_from = document.createElement('span');
                        label_input_from.textContent = "From";
                        const inputFrom = document.createElement('input');
                        inputFrom.type = 'date';
                        inputFrom.className = 'filter-input';
                        inputFrom.setAttribute('data-column', data_column);
                        inputFrom.setAttribute('data-range', 'from');
                        inputFrom.placeholder = "From";
                        div_input_from.appendChild(label_input_from);
                        div_input_from.appendChild(inputFrom);
                        filterCell.appendChild(div_input_from);

                        // Create "To" date input
                        const div_input_to = document.createElement('div');
                        const label_input_to = document.createElement('span');
                        label_input_to.textContent = "To";
                        const inputTo = document.createElement('input');
                        inputTo.type = 'date';
                        inputTo.className = 'filter-input';
                        inputTo.setAttribute('data-column', data_column);
                        inputTo.setAttribute('data-range', 'to');
                        inputTo.placeholder = "To";
                        div_input_to.appendChild(label_input_to);
                        div_input_to.appendChild(inputTo);
                        filterCell.appendChild(div_input_to);
                    }
                    else {
                        // Regular text input for other columns
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.className = 'filter-input';
                        input.setAttribute('data-column', data_column);
                        input.placeholder = `Search ${cell.textContent}`;
                        filterCell.appendChild(input);
                    }

                }
                else if(index===(headerRow.cells.length - 1)){
                    const buttonSearch = document.createElement('button');
                    buttonSearch.textContent = "Search";
                    buttonSearch.addEventListener('click', filterUsers);
                    filterCell.appendChild(buttonSearch);
                }

                filterRow.appendChild(filterCell);
            });

            table.querySelector('thead').appendChild(filterRow);
        }

        function addEventListenersToFilterInputs() {
            const filterInputs = document.querySelectorAll('.filter-input');
            const operatorSelects = document.querySelectorAll('select');

            operatorSelects.forEach(select => {
                select.addEventListener('change', filterUsers);
            });
        }

        document.getElementById('remove-filters').addEventListener('click', function() {
            showOverlay();
            fetchAllUsers().then(users => {
                allUsers = users;
                sortPriority = [];

                resetSortIcons();
                usersTablePaginator.setData(allUsers); // Rebuild table without sorting
                hideOverlay();
            });

            const inputs = document.querySelectorAll('.filter-input');
            inputs.forEach(input => input.value = '');

            this.style.display = 'none';
        });

        function resetSortIcons() {
            const arrows = document.querySelectorAll('.sort-arrow');
            arrows.forEach((arrow) => {
                // Assuming you're using text content like 'x', '↑', '↓' for sorting indicators
                arrow.classList.add('fa-x'); // Reset to 'x' to indicate no sorting

            });
        }

        function buildUsersControlTable(usersArray, tbody) {
            tbody.innerHTML = '';
            usersArray.forEach(user => {
                // Create the row
                let row = document.createElement('tr');

                // Checkbox cell
                let checkBoxCell = document.createElement('td');
                let checkBox = document.createElement('input');
                checkBox.setAttribute('type', 'checkbox');
                checkBox.setAttribute('name', 'selectedUser');
                checkBox.setAttribute('value', user.userId);
                checkBoxCell.appendChild(checkBox);
                row.appendChild(checkBoxCell);

                // User ID cell
                let userIdCell = document.createElement('td');
                userIdCell.textContent = user.userId;
                row.appendChild(userIdCell);

                let firstNameCell = document.createElement('td');
                firstNameCell.textContent = user.first_name;
                row.appendChild(firstNameCell);

                let lastNameCell = document.createElement('td');
                lastNameCell.textContent = user.last_name;
                row.appendChild(lastNameCell);

                let thirdNameCell = document.createElement('td');
                thirdNameCell.textContent = user.third_name;
                row.appendChild(thirdNameCell);

                let emailCell = document.createElement('td');
                emailCell.textContent = user.email;
                row.appendChild(emailCell);


                // Repeat for each user property...
                // For cells with static content like '---' for sales
                let schoolCell = document.createElement('td');
                schoolCell.textContent = user.school || "Жюри"; // Assuming sales data is not available
                row.appendChild(schoolCell);

                let enabledCell = document.createElement('td');
                enabledCell.textContent = user.Enabled ? "Активний" : "Неактивний"; // Assuming sales data is not available
                row.appendChild(enabledCell);

                // For boolean values, you might want to show a more user-friendly value
                let paralelCell = document.createElement('td');
                paralelCell.textContent = user.paralel;
                row.appendChild(paralelCell);


                let registrationDateCell = document.createElement('td');

                registrationDateCell.textContent = user.registrationDate.split(" ")[0];
                row.appendChild(registrationDateCell);

                // Actions cell
                let actionsCell = document.createElement('td');
                let editLink = document.createElement('a');

                let editUrl = `/admin_tools/users_control/edit_user/${user.userId}/`; // Construct the URL using the user ID
                editLink.setAttribute('href', editUrl);
                const editbutton = document.createElement('i');
                editbutton.classList.add('material-icons');
                editbutton.textContent = 'edit';
                editLink.appendChild(editbutton);
                actionsCell.appendChild(editLink);

                let optionsButton = document.createElement('i');
                optionsButton.classList.add('material-symbols-outlined');
                let optionsLink = document.createElement('a');
                optionsButton.textContent = 'more_vert';
                optionsButton.style.cursor = 'pointer';
                optionsLink.appendChild(optionsButton);
                actionsCell.appendChild(optionsLink);
                optionsButton.addEventListener('click', function(event) {
                    event.stopPropagation(); // Prevent the click from closing the menu immediately

                    // Position the menu
                    const contextMenu = document.getElementById('contextMenu');
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = `${event.pageX - 100}px`;
                    contextMenu.style.top = `${event.pageY}px`;

                    // Function to hide the context menu
                    function hideContextMenu() {
                        contextMenu.style.display = 'none';
                    }

                    // Close the menu when clicking outside of it
                    document.addEventListener('click', hideContextMenu, { once: true });

                    // Set up the menu actions
                    document.getElementById('viewUser').onclick = function() {
                        // Replace with the actual function or navigation action
                        window.location.href = `/admin_tools/users_control/view_user/${user.userId}/`;
                    };
                    document.getElementById('deleteUser').onclick = async function() {
                        const csrftoken = getCookie('csrftoken'); // Get the CSRF token
                        let userIds = [user.userId]
                        const jsonObject = { userIds: userIds };
                        const response = await fetch(window.config.atDeleteUsersUrl, { // Use the correct URL for your request
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrftoken, // Include CSRF token in request headers
                            },
                            body: JSON.stringify(jsonObject),
                        });

                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }

                        allUsers = allUsers.filter(user => !userIds.includes(user.userId));
                        usersTablePaginator.setData(allUsers);
                    }
                });
                row.appendChild(actionsCell);
                // Append the row to the table body
                tbody.appendChild(row);
            });
            document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.addEventListener('change', updateBulkActionsDropdown);
            });
        }
        function updateBulkActionsDropdown() {
            const checkboxes = document.querySelectorAll(' input[type="checkbox"]');
            const bulkActionsDropdown = document.getElementById('bulk-actions');
            const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

            bulkActionsDropdown.disabled = !anyChecked;
        }

        document.getElementById('bulk-actions').addEventListener('change', async function() {
            const action = this.value;
            const selectedUserIds = Array.from(document.querySelectorAll('#usersTable input[type="checkbox"]:checked')).map(checkbox => checkbox.value);
            // Ensure there are selected users
            if (selectedUserIds.length === 0) {
                resetBulkActionsDropdown();
                return;
            }

            switch(action) {
                case 'Enable selected':
                    await performBulkAction(window.config.atEnableUsersUrl, selectedUserIds, 'enable');
                    break;
                case 'Disable selected':
                    await performBulkAction(window.config.atDisableUsersUrl, selectedUserIds, 'disable');
                    break;
                case 'Delete accounts':
                    const confirmDelete = confirm('Do you really want to delete the selected users?');
                    if (confirmDelete) {
                        await performBulkAction(window.config.atDeleteUsersUrl, selectedUserIds, 'delete');
                    }
                    break;
            }

            resetBulkActionsDropdown();
        });

        async function performBulkAction(bulk_url, userIds, actionType) {
            // Your fetch logic here...
            const csrftoken = getCookie('csrftoken'); // Get the CSRF token
            const jsonObject = { userIds: userIds }; // Assuming you're sending a list of user IDs

            try {
                const response = await fetch(bulk_url, { // Use the correct URL for your request
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken, // Include CSRF token in request headers
                    },
                    body: JSON.stringify(jsonObject),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                // Assuming JSON response for simplicity
                const data = await response.json();

                if (actionType === 'delete') {
                    allUsers = allUsers.filter(user => !userIds.includes(user.userId.toString()));
                } else {
                    const enabledStatus = actionType === 'enable';
                    allUsers.forEach(user => {
                        if (userIds.includes(user.userId.toString())) {
                            user.Enabled = enabledStatus;
                        }
                    });
                }
                usersTablePaginator.setData(allUsers);

                // After performing the action, check checkboxes and update dropdown state
                updateBulkActionsDropdown();
            } catch (error) {
                console.error('Failed to perform bulk action:', error);
            }
        }

        function resetBulkActionsDropdown() {
            const bulkActionsDropdown = document.getElementById('bulk-actions');
            bulkActionsDropdown.value = "";
            bulkActionsDropdown.disabled = true;
            updateBulkActionsDropdown();
        }

        function getActualArray(){
            return filteredUsers.length === 0 ? allUsers : filteredUsers;
        }

        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', init);
        } else {
          init();
        }
    })
    .catch(error => {
        console.error("Error during dynamic import:", error);
    });