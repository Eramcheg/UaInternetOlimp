
    const jury_tasks = profileConfig.jury_tasks;
    const tasks = profileConfig.tasks;
    const savedCriteria = profileConfig.saved_criteria;
    document.addEventListener('DOMContentLoaded', function () {
        const tabs = document.querySelectorAll('.tab');
        const criteriaContainer = document.getElementById('criteria-container');
        const currentTask = document.getElementById('current-task');

        // Функция для отображения сохраненных критериев задачи
        function showTask(taskId) {
            currentTask.innerHTML = ``;
            const headerTask = document.createElement('h1');
            headerTask.textContent = `Задача ${taskId}`;

            const pointsHeader = document.createElement('h3');
            pointsHeader.textContent =  tasks['task'+taskId].max_points +` балів`;

            currentTask.appendChild(headerTask);
            currentTask.appendChild(pointsHeader);

            criteriaContainer.innerHTML = '';  // Очистка контейнера критериев
            if (savedCriteria[taskId].length !== 0) {

                savedCriteria[taskId].forEach(criterion => {
                    addCriteriaRow(criterion.criterion_text, criterion.points);
                });
            }
            else{
                addCriteriaRow();
            }
        }
        if(jury_tasks.length !== 0) {
            showTask(jury_tasks[0]);
        }
        // Функция для добавления новой строки критериев
        function addCriteriaRow(criterion_text = '', points = '') {
            const row = document.createElement('div');
            row.classList.add('criteria-row');
            row.innerHTML = `
                <input type="text" class="criteria-text" placeholder="Текст критерію" value="${criterion_text}">
                <input class="criteria-points" placeholder="Балів" value="${points}">
                <button type="button" class="remove-criteria"><i class='fa-solid fa-remove'></i></button>
            `;
            criteriaContainer.appendChild(row);
            row.querySelector('.remove-criteria').addEventListener('click', function () {
                row.remove();
            });
        }
        // Переключение между задачами
        tabs.forEach(tab => {
            let task = tasks['task'+tab.getAttribute('data-task')];
            if(task.status !== "") {
                tab.classList.add(task.status);
            }
            tab.addEventListener('click', function () {
                document.querySelector('.active-tab').classList.remove('active-tab');
                this.classList.add('active-tab');
                const taskId = this.getAttribute('data-task');
                showTask(taskId);
            });
        });

        // Добавление новой строки критериев
        document.getElementById('add-criteria').addEventListener('click', function () {
            addCriteriaRow();
        });


        // Обработка отправки критериев
        document.getElementById('submit-criteria').addEventListener('click', function () {
            const taskId = document.querySelector('.active-tab').getAttribute('data-task');
            const maxPoints = tasks['task'+taskId].max_points;  // Получение максимальных баллов для задачи
            // Сбор данных критериев
            const criteriaRows = document.querySelectorAll('.criteria-row');
            const criteriaData = [];
            let totalPoints = 0;
            criteriaRows.forEach((row, index) => {
                const criterion_text = row.querySelector('.criteria-text').value;
                const points = parseFloat(row.querySelector('.criteria-points').value.replace(',', '.')) || 0;
                criteriaData.push({ criterion_text, points, num: index + 1, id: `${taskId}` });
                totalPoints += points;
            });

            // Проверка суммы баллов
            if (totalPoints > maxPoints) {
                alert('Забагато балів! Сумарна кількість балів всіх критеріїв повиння дорівнювати ' + maxPoints);
                return;
            } else if (totalPoints < maxPoints) {
                alert('Замало балів! Сумарна кількість балів всіх критеріїв повиння дорівнювати ' + maxPoints);
                return;
            }
            const csrftoken = getCookie('csrftoken'); // Ensure you have csrftoken available
            fetch(profileConfig.submitCriteriaUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({ task_id: taskId, criteria: criteriaData })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Критерії успішно збережені!');
                } else {
                    alert('Помилка при збереженні критеріїв.');
                    console.log(data.error);
                }
            });
        });
    });