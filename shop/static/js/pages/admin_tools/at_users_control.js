import(window.config.firebaseFunctionScriptUrl)
    .then(module => {
        const {fetchAllUsers} = module;
        let allUsers = [];
        let usersTablePaginator = null;
        let filteredUsers = [];
        let sortPriority = [];

        const COLUMNS = [
          { key: "_select",    title: "",               group: "",           width: 40,  sticky: "left" },
          { key: "userId", title: "Id", group: "Основне",  width: 100, sticky: "left2", render: u => `${u.userId}` },
          { key: "first_name", title: "Ім'я", group: "Основне", width: 100, render: u => `${u.first_name}` },
          { key: "last_name", title: "Прізвище", group: "Основне", width: 100, render: u => `${u.last_name}` },
          { key: "third_name",   title: "По батькові", group: "Основне", width: 100, render: u => `${u.third_name}` },
          { key: "email",   title: "Email",        group: "Основне", width: 100, render: u => `<span class="mono">${u.email}</span>` },
          { key: "phone",   title: "Телефон",      group: "Основне", width: 100, render: u => `<span class="mono">${u.phone}</span>` },

          { key: "paralel",   title: "Паралель",   group: "Навчання", width: 90, render: u => `<span class="mono">${u.paralel}</span>` },
          { key: "school",     title: "Школа",  group: "Навчання", width: 220, render: u => `${u.school}` },

          { key: "Enabled", title: "Статус акаунта", group: "Службове", width: 100, render: u => u.Enabled ? '<span class="badge badge-yes">Активний</span>' : '<span class="badge badge-no">Деактивований</span>' },
          { key: "registrationDate",      title: "Дата реєстрації",     group: "Службове", width: 140, render: u => `${u.registrationDate}` },

          { key: "_actions",       title: "Дії",          group: "",         width: 80,  sticky: "right" },
        ];

        async function init() {
            showOverlay();
            allUsers = await fetchAllUsers();

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
                    updateSortPriority(index, sortPriority);
                    adjustSortIcon(index, index, sortPriority); // Use the updated function here
                    sortUsers(getActualArray());
                });
            });
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
            const headerRow = table.querySelectorAll('thead tr')[1];
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

                    let data_column = cell.getAttribute('data-column').trim();

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
                        input.classList.add('filter-input');
                        if (data_column === "userId"){
                            filterCell.classList.add('sticky-left-2');
                        }
                        input.setAttribute('data-column', data_column);
                        input.placeholder = `Фільтр ${cell.textContent}`;
                        filterCell.appendChild(input);
                    }

                }
                else if(index===(headerRow.cells.length - 1)){
                    const buttonSearch = document.createElement('button');
                    buttonSearch.textContent = "Фільтр";
                    filterCell.classList.add('sticky-right');
                    buttonSearch.addEventListener('click', filterUsers);
                    filterCell.appendChild(buttonSearch);
                }
                else if (index===0){
                    filterCell.classList.add('sticky-left');
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
            buildHeader();
            addEventListenersToUsers();
            addFilterInputs();
            addEventListenersToFilterInputs();
            buildBody(usersArray, tbody);
        }

        function buildHeader() {
          const colgroup = document.getElementById('usersColGroup');
          const thead = document.getElementById('usersThead');
          colgroup.innerHTML = "";
          thead.innerHTML = "";

          const groupsRow = document.createElement('tr');
          const fieldsRow = document.createElement('tr');

          // считаем кол-во колонок на группу
          const groupSpans = {};
          COLUMNS.forEach(col => {
            const g = col.group || "";
            groupSpans[g] = (groupSpans[g] || 0) + 1;
          });

          // строим верхнюю строку
          let builtGroups = new Set();
          COLUMNS.forEach((col, idx) => {
            // colgroup width
            const c = document.createElement('col');
            c.style.width = (col.width || 120) + "px";
            colgroup.appendChild(c);

            // top groups (только первый раз для каждой группы)
            const g = col.group || "";
            if (!builtGroups.has(g)) {
              builtGroups.add(g);
              const thg = document.createElement('th');
              thg.className = 'group';
              thg.colSpan = groupSpans[g];
              thg.textContent = g || "";
              groupsRow.appendChild(thg);
            }

            // bottom fields
            const th = document.createElement('th');
            let existingIdx = sortPriority.findIndex(sp => (sp.columnIndex+1) === idx);
            let typeOfArrow = "fa-x";
            if (existingIdx !== -1){
                typeOfArrow = sortPriority[existingIdx].direction === "asc" ? "fa-arrow-up" : "fa-arrow-down";
            }
            if ([0, 11].includes(idx)){
                th.innerHTML = col.title;
            }
            else{
                th.innerHTML = `${col.title} <span class="arrow-sorting"><i class="sort-arrow fa-solid ${typeOfArrow}"></i></span>`;
            }

            th.setAttribute('data-column', col.key);
            // sticky classes на заголовках тоже
            if (col.sticky === "left") th.classList.add('sticky-left');
            if (col.sticky === "left2") th.classList.add('sticky-left-2');
            if (col.sticky === "right") th.classList.add('sticky-right');
            fieldsRow.appendChild(th);
          });

          thead.appendChild(groupsRow);
          thead.appendChild(fieldsRow);
        }
        function buildBody(usersArray, tbody) {
          tbody.innerHTML = "";

          usersArray.forEach(user => {
            const tr = document.createElement('tr');

            COLUMNS.forEach(col => {
              const td = document.createElement('td');

              // sticky клетки
              if (col.sticky === "left")  td.classList.add('sticky-left');
              if (col.sticky === "left2") td.classList.add('sticky-left-2');
              if (col.sticky === "right") td.classList.add('sticky-right');

              // перенос текста
              if (col.wrap) td.classList.add('wrap'); else td.classList.add('nowrap');

              // содержимое
              if (col.key === "_select") {
                const cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.name = 'selectedUser';
                cb.value = user.userId;
                td.appendChild(cb);
              } else if (col.key === "_actions") {
                td.innerHTML = renderActions(user);

                attachContextMenu(td, user); // твоя логика открытия меню
              }
              else if (col.key === "schoolOblast"){
                  td.innerHTML = (col.render ? col.render(user) : (user[col.key] ?? ""));
                  td.title = td.textContent.trim();
              }
              else {
                  td.innerHTML = (col.render ? col.render(user) : (user[col.key] ?? ""));
                  td.title = td.textContent.trim();
              }

              tr.appendChild(td);
            });

            tbody.appendChild(tr);
          });
        }
        function renderActions(user) {
          const editUrl = `/admin_tools/users_control/edit_user/${user.userId}/`;
          return `
            <a href="${editUrl}" title="Редагувати"><i class="material-icons">edit</i></a>
            <a class="more" title="Більше"><i class="material-symbols-outlined">more_vert</i></a>
          `;
        }
        function attachContextMenu(td, user) {
          const btn = td.querySelector('.more');
          if (!btn) return;
          btn.addEventListener('click', function(event) {
            event.stopPropagation();
            const contextMenu = document.getElementById('contextMenu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = `${event.pageX - 100}px`;
            contextMenu.style.top = `${event.pageY}px`;

            function hide() { contextMenu.style.display = 'none'; }
            document.addEventListener('click', hide, { once: true });

            document.getElementById('viewUser').onclick = function() {
              window.location.href = `/admin_tools/users_control/view_user/${user.userId}/`;
            };
            document.getElementById('deleteUser').onclick = async function() {
              const csrftoken = getCookie('csrftoken');
              const userIds = [user.userId];
              const response = await fetch(window.config.atDeleteUsersUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                body: JSON.stringify({ userIds })
              });
              if (!response.ok) { alert('Помилка мережі'); return; }
              allUsers = allUsers.filter(u => !userIds.includes(u.userId));
              usersTablePaginator.setData(allUsers);
              renderUsersTable(allUsers);
            };
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