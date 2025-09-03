import(window.config.firebaseFunctionScriptUrl)
    .then(module => {
        const {fetchAllRegistrations} = module;
        let allRegistrations = [];
        let usersTablePaginator = null;
        let filteredRegistrations = [];
        let sortPriority = [];

        const COLUMNS = [
          { key: "_select",    title: "",               group: "",           width: 40,  sticky: "left" },
          { key: "lastNameUk", title: "ПІБ", group: "Основне",  width: 220, sticky: "left2", render: u => `${u.lastName_uk} ${u.firstName_uk}${u.patronymic_uk? " "+u.patronymic_uk:""}` },
          { key: "fullNameEn", title: "Ім'я EN • Прізвище EN", group: "Основне", width: 220, render: u => `${u.lastName_en} ${u.firstName_en}` },

          { key: "studyInUkraine", title: "Навчається в Україні", group: "Навчання", width: 160, render: u => u.studyInUkraine ? '<span class="badge badge-yes">Так</span>' : '<span class="badge badge-no">Ні</span>' },
          { key: "schoolOblast",   title: "Область школи", group: "Навчання", width: 150, render: u => u.studyInUkraine ? (u.schoolOblast||"") : "" },
          { key: "schoolNumber",   title: "№ школи",      group: "Навчання", width: 100, render: u => u.studyInUkraine ? (u.schoolNumber||"") : "" },
          { key: "schoolName",     title: "Назва школи",  group: "Навчання", width: 220, render: u => u.studyInUkraine ? (u.schoolName||"") : (u.studyAbroadNote||"") },

          { key: "residence",      title: "Місце проживання", group: "Проживання", width: 220, render: u => `${u.residenceCountry}, ${u.residenceCity}` },

          { key: "contactEmail",   title: "Email",        group: "Контакти", width: 220, render: u => `<span class="mono">${u.contactEmail}</span>` },
          { key: "contactLinks",   title: "Посилання на соцмережі", group: "Контакти", width: 260, wrap: true, render: u => (u.contactLinks||"") },

          { key: "paralel",        title: "Паралель",     group: "Навчання", width: 110 },
          { key: "olympiadsParticipation", title: "Участь в олімпіадах", group: "Олімпіади", width: 170,
            render: u => u.olympiadsParticipation ? '<span class="badge badge-yes">Так</span>' : '<span class="badge badge-no">Ні</span>' },
          { key: "olympiadsAchievements",  title: "Досягнення", group: "Олімпіади", width: 320, wrap: true, render: u => (u.olympiadsAchievements||"") },

          { key: "createdAt",      title: "Створено",     group: "Службове", width: 140, render: u => formatDate(u.createdAt) },

          { key: "_actions",       title: "Дії",          group: "",         width: 80,  sticky: "right" },
        ];

        async function init() {
            showOverlay();
            allRegistrations = await fetchAllRegistrations();

            addEventListenersToUsers();

            const wrapper = document.querySelector('[data-table-id="registrations-control-table"]');
            if (!usersTablePaginator) {
                usersTablePaginator = initPagination(
                  wrapper,
                  allRegistrations,
                  buildUsersControlTable
                );
              } else {
                usersTablePaginator.setData(allRegistrations);
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
                        case 1: // First Name
                           valA = a.firstName_uk || ""; valB = b.firstName_uk || "";
                            break;
                        case 2: // Last Name
                            valA = a.lastName_uk || ""; valB = b.lastName_uk || "";
                            break;
                        case 3: // Third Name
                            valA = a.patronymic_uk || ""; valB = b.patronymic_uk || "";
                            break;
                        case 4: // First name EN
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
            filteredRegistrations = allRegistrations.filter(order => {
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
                    else if (["olympiadsParticipation", "studyInUkraine"].includes(columnName)) {
                        let boolVal = orderValue ? "Так" : "Ні";
                        return boolVal.toString().toLowerCase().includes(input.value.toLowerCase());
                    }
                    else { // Textual data
                        return orderValue.toString().toLowerCase().includes(input.value.toLowerCase());
                    }
                });
            });

            usersTablePaginator.setData(filteredRegistrations); // Rebuild the table with the filtered data
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

                    if (cell.textContent.trim() === "createdAt") {
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
                        if (data_column === "lastNameUk"){
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
            fetchAllRegistrations().then(users => {
                allRegistrations = users;
                sortPriority = [];

                resetSortIcons();
                usersTablePaginator.setData(allRegistrations); // Rebuild table without sorting
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
        function formatDate(createdAt) {
          // createdAt может быть Timestamp Firestore или строка
          try {
            if (!createdAt) return "";
            // если Firestore Timestamp
            if (createdAt.seconds) {
              const d = new Date(createdAt.seconds * 1000);
              return d.toLocaleDateString('uk-UA');
            }
            const d = new Date(createdAt);
            return isNaN(d) ? "" : d.toLocaleDateString('uk-UA');
          } catch { return ""; }
        }
        function buildUsersControlTable(usersArray, tbody) {
            buildHeader();

            addFilterInputs();
            addEventListenersToFilterInputs();
            buildBody(usersArray, tbody);
            return;
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

                let firstNameCell = document.createElement('td');
                firstNameCell.textContent = user.firstName_uk;
                row.appendChild(firstNameCell);

                let lastNameCell = document.createElement('td');
                lastNameCell.textContent = user.lastName_uk;
                row.appendChild(lastNameCell);

                let thirdNameCell = document.createElement('td');
                thirdNameCell.textContent = user.patronymic_uk;
                row.appendChild(thirdNameCell);

                let firstNameENCell = document.createElement('td');
                firstNameENCell.textContent = user.firstName_en;
                row.appendChild(firstNameENCell);

                let lastNameENCell = document.createElement('td');
                lastNameENCell.textContent = user.lastName_en;
                row.appendChild(lastNameENCell);

                // Repeat for each user property...
                // For cells with static content like '---' for sales
                let studyWhereCell = document.createElement('td');
                studyWhereCell.textContent = user.studyInUkraine ? "Так" : "Ні"; // Assuming sales data is not available
                row.appendChild(studyWhereCell);

                let livingPlaceCell = document.createElement('td');
                livingPlaceCell.textContent = `${user.residenceCountry}, ${user.residenceCity}`; // Assuming sales data is not available
                row.appendChild(livingPlaceCell);

                let emailCell = document.createElement('td');
                emailCell.textContent = user.contactEmail;
                row.appendChild(emailCell);

                // For boolean values, you might want to show a more user-friendly value
                let paralelCell = document.createElement('td');
                paralelCell.textContent = user.paralel;
                row.appendChild(paralelCell);

                let olympParticipCell = document.createElement('td');
                olympParticipCell.textContent = user.olympiadsParticipation ? "Так" : "Ні";
                row.appendChild(olympParticipCell);

                let olimpAchiveCell = document.createElement('td');
                olimpAchiveCell.textContent = user.olympiadsAchievements;
                row.appendChild(olimpAchiveCell);

                let registrationDateCell = document.createElement('td');

                registrationDateCell.textContent = "";//user.registrationDate.split(" ")[0];
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

                        allRegistrations = allRegistrations.filter(user => !userIds.includes(user.userId));
                        usersTablePaginator.setData(allRegistrations);
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

        function buildHeader() {
          const colgroup = document.getElementById('usersColGroup');
          const thead = document.getElementById('usersThead');
          colgroup.innerHTML = "";
          thead.innerHTML = "";

          // верхняя строка (группы)
          const groupsRow = document.createElement('tr');
          // нижняя строка (поля)
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
            th.innerHTML = col.title;

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
              } else {
                const html = (col.render ? col.render(user) : (user[col.key] ?? ""));
                td.innerHTML = html;
                // наводишь — показываем полный текст (для обрезанных)
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
              allRegistrations = allRegistrations.filter(u => !userIds.includes(u.userId));
              usersTablePaginator.setData(allRegistrations);
              renderUsersTable(allRegistrations);
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
                    allRegistrations = allRegistrations.filter(user => !userIds.includes(user.userId.toString()));
                } else {
                    const enabledStatus = actionType === 'enable';
                    allRegistrations.forEach(user => {
                        if (userIds.includes(user.userId.toString())) {
                            user.Enabled = enabledStatus;
                        }
                    });
                }
                usersTablePaginator.setData(allRegistrations);

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
            return filteredRegistrations.length === 0 ? allRegistrations : filteredRegistrations;
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