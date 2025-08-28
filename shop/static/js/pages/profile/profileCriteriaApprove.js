
    document.addEventListener('DOMContentLoaded', function () {
        const tabs = document.querySelectorAll('.tab');
        const criteriaContainer = document.getElementById('criteria-container');
        const currentTask = document.getElementById('current-task');
        const jury_tasks = profileConfig.jury_tasks;
        const savedCriteria = profileConfig.saved_criteria;
        const tasks = profileConfig.tasks;

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

            // Отображение сохраненных критериев, если они есть
            if (savedCriteria[taskId] !== undefined && savedCriteria[taskId].length !== 0) {
                const rejectBtn = document.getElementById('reject-criteria');
                rejectBtn.style.display = '';
                const acceptBtn = document.getElementById('submit-criteria');
                acceptBtn.style.display = '';
                savedCriteria[taskId].forEach((criterion, index) => {
                    addCriteriaRow(criterion.criterion_text, criterion.points, index+1);
                });
            }
            else{
                addEmptyCriterion();
            }
        }
        if(jury_tasks.length !== 0) {
            showTask(jury_tasks[0]);
        }
        // Функция для добавления новой строки критериев
        function addCriteriaRow(criterion_text = '', points = '', index=1) {
            const row = document.createElement('div');
            row.classList.add('criteria-row');
            row.innerHTML = `
                <span class="criteria-counter">${index}.</span>
                <span class="criteria-text">${criterion_text}</span>
                <span class="criteria-points">${points} балів</span>
            `;
            criteriaContainer.appendChild(row);
        }
        function addEmptyCriterion() {
            const row = document.createElement('div');
            row.classList.add('criteria-row');
            row.innerHTML = `
                <span class="criterion-empty">Критерії ще не були додані.</span>
            `;
            criteriaContainer.appendChild(row);
            const rejectBtn = document.getElementById('reject-criteria');
            rejectBtn.style.display = 'none';
            const acceptBtn = document.getElementById('submit-criteria');
            acceptBtn.style.display = 'none';
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

        // Обработка отправки критериев
        document.getElementById('submit-criteria').addEventListener('click', function () {
            const taskId = document.querySelector('.active-tab').getAttribute('data-task');
            const criteriaData = [];

            const csrftoken = getCookie('csrftoken'); // Ensure you have csrftoken available
            fetch(profileConfig.approveCriteriaUrl, {
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
                    alert('Критерії було успішно підтверджено!');
                } else {
                    alert('Помилка під час підтвердження критеріїв!');
                    console.log(data.error);
                }
            });
        });
        document.getElementById('reject-criteria').addEventListener('click', function () {
            const taskId = document.querySelector('.active-tab').getAttribute('data-task');

            const csrftoken = getCookie('csrftoken'); // Ensure you have csrftoken available
            // Отправка данных на сервер
            fetch(profileConfig.rejectCriteriaUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({ task_id: taskId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Критерії було успішно відхилено!');
                } else {
                    alert('Помилка при відхиленні критеріїв!');
                    console.log(data.error);
                }
            });
        });
    });