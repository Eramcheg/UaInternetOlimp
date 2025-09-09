import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.10/firebase-app.js";
import { getFirestore, collection, query, onSnapshot, doc, getDoc, setDoc, serverTimestamp, addDoc,updateDoc, where, orderBy } from "https://www.gstatic.com/firebasejs/9.6.10/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyAzV7CPVJJbgteozTbjdlIcyt85Kbuxd90",
    authDomain: "uainternetolimp-41dd1.firebaseapp.com",
    projectId: "uainternetolimp-41dd1",
    storageBucket: "uainternetolimp-41dd1.appspot.com",
    messagingSenderId: "545486624571",
    appId: "1:545486624571:web:4a543063a04b43e5bb091e",
    measurementId: "G-MJBJXCE1SJ"
};
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

let currentTour = profileConfig.currentTour;
let currentYear = profileConfig.currentYear;
const jury_tasks = profileConfig.jury_tasks;
let show_without = true;
const DOWNLOAD_API_PREFIX = "/api/download-file";
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const taskIndexOf = (taskKey) => parseInt(String(taskKey ?? "").split("_")[1] || "0", 10);
let unsubscribeAssignments = null;

const MAX_TASKS = 5;

    const byUser = new Map();
$(document).ready(function() {
    // Загружаем студентов класса 9 при первой загрузке страницы
    loadStudents(9);

    const tabs = document.querySelectorAll('.tab');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            document.querySelector('.active-tab').classList.remove('active-tab');
            this.classList.add('active-tab');
            const paralel = this.getAttribute('data-task');
            loadStudents(paralel);
        });
    });

    function loadStudents(classNumber) {
        if (byUser) byUser.clear();

        $.ajax({
            url: `/api/assignments/`,  // URL для получения данных о студентах
            data: { class: classNumber },
            success: function(response) {
                let tableBody = $('#students-table tbody');
                tableBody.empty();  // Очищаем таблицу перед заполнением

                let grouped = [];

                if (Array.isArray(response.assignments)) {
                    grouped = response.assignments.map(obj => {
                      const [userId, tasks] = Object.entries(obj)[0] || [];
                      return { userId, tasks: tasks || [] };
                    }).filter(x => x.userId);
                  } else if (response.assignments && typeof response.assignments === 'object') {
                    grouped = Object.entries(response.assignments).map(([userId, tasks]) => ({
                      userId, tasks: tasks || []
                    }));
                  }
                if (!grouped.length) {
                    tableBody.append('<tr><td colspan="999">Немає даних</td></tr>');
                }
                else {
                    const rowsHtml = grouped.map(({userId, tasks}) => {
                        const paralel = (tasks[0] && tasks[0].paralel) || classNumber;
                        const payload = {userId, paralel, tasks};
                        return `<tr data-student-id="${userId}">${generateTaskCells(payload)}</tr>`;
                    }).join('');
                    tableBody.append(rowsHtml);
                }
                setupRealtimeUpdates(String(classNumber));
            }
        });
    }

    // Функция для создания ячеек с заданиями студента
    function generateTaskCells(assignmentOrGroup) {
      let userId, paralel, tasks = [];

      // NEW: если пришла группа { userId, paralel, tasks: [...] }
      if (assignmentOrGroup && typeof assignmentOrGroup === "object" && Array.isArray(assignmentOrGroup.tasks)) {
        userId = assignmentOrGroup.userId;
        paralel = assignmentOrGroup.paralel;
        tasks = assignmentOrGroup.tasks.slice();
      } else {
        // OLD: одиночный assignment (как раньше)
        const a = assignmentOrGroup || {};
        userId = a.userId;
        paralel = a.paralel;
        tasks = [a];
      }

      // карта индекс -> task
      const byIndex = new Map();
      for (const t of tasks) {
        const idx = taskIndexOf(t.taskKey) || Number(t.taskId) || 0; // task_1 -> 1
        if (idx) byIndex.set(idx, t);
      }

      let cells = '';
      cells += `<td>${esc(userId ?? "")}</td>`;

      for (let i = 1; i <= MAX_TASKS; i++) {
        const t = byIndex.get(i);
        if (!t) {
          cells += `<td data-task="task_${i}">Файл відсутній</td>`;
          continue;
        }

        // сумма оценок
        let grade = 0.0;
        if (Array.isArray(t.grading)) {
          for (const el of t.grading) {
            const num = Number(el);
            if (!Number.isNaN(num)) grade += num;
          }
          grade = Number(grade.toFixed(1));
        }

        const hasFile = Boolean(t.fileUrl);
        const isDone  = Boolean(t.status);
        const btnClass = isDone ? 'btn-green' : 'btn-gray';
        const btnText  = isDone ? `Оцінено: ${grade}` : 'Оцінити';
        const downloadUrl = `${DOWNLOAD_API_PREFIX}/${esc(userId)}/${esc(paralel)}/${i}`;

        let grading = t.grading;
        cells += `<td data-task="task_${i}">
          ${
            hasFile
              ? `
                <button class="${btnClass} evaluate-btn"
                        data-student-id="${esc(userId)}"
                        data-task-id="${i}"
                        data-student-class="${esc(paralel)}"
                        data-student='${esc(JSON.stringify({ userId, paralel, grading }))}'>
                  ${btnText}
                </button>
                <a class="download-btn" href="${downloadUrl}" download="${esc(userId)}_${esc(paralel)}_${i}.pdf">
                  <i class="fa-solid fa-download"></i>
                </a>
              `
              : 'Файл відсутній'
          }
        </td>`;
      }

      return cells;
    }


    function setupRealtimeUpdates(paralel) {
        if (typeof unsubscribeAssignments === 'function') {
            unsubscribeAssignments();
            unsubscribeAssignments = null;
        }
        byUser.clear();

        const q = query(
            collection(db, 'assignments'),
            where('paralel', '==', String(paralel)),
            where('tour', '==', currentTour),
            where('year', '==', currentYear)
        );

        unsubscribeAssignments = onSnapshot(q, (snapshot) => {
        // 1) при первом снимке соберём всё состояние
        if (snapshot.docChanges().every(ch => ch.type === 'added')) {
          byUser.clear();
          snapshot.forEach(doc => {
            const a = doc.data();
            if (!byUser.has(a.userId)) byUser.set(a.userId, { paralel: a.paralel, tasks: [] });
            byUser.get(a.userId).tasks.push(a);
          });
          const $tb = $('#students-table tbody').empty();
          if (!byUser.size) {
            $tb.append('<tr><td colspan="999">Немає даних</td></tr>');
          } else {
            const rows = [];
            for (const [userId, {paralel, tasks}] of byUser.entries()) {
              rows.push(`<tr data-student-id="${userId}">${generateTaskCells({ userId: userId, paralel: paralel, tasks: tasks })}</tr>`);
            }
            $tb.append(rows.join(''));
          }
          return;
        }
        // 2) на последующих изменениях точечно обновляем строки
        snapshot.docChanges().forEach((change) => {
          const a = change.doc.data();
          const userId = a.userId;
          if (!byUser.has(userId)) byUser.set(userId, { paralel: a.paralel, tasks: [] });
          const entry = byUser.get(userId);

          if (change.type === 'removed') {
            entry.tasks = entry.tasks.filter(t => t.taskKey !== a.taskKey);
          } else { // added | modified
            entry.paralel = a.paralel;
            const i = entry.tasks.findIndex(t => t.taskKey === a.taskKey);
            if (i === -1) entry.tasks.push(a); else entry.tasks[i] = a;
          }

          // перерисовать только одну строку
          const rowHtml = generateTaskCells({ userId, paralel: entry.paralel, tasks: entry.tasks });
          let row = document.querySelector(`tr[data-student-id="${CSS.escape(userId)}"]`);
          if (row) {
            row.innerHTML = rowHtml;
          } else {
            row = document.createElement('tr');
            row.setAttribute('data-student-id', userId);
            row.innerHTML = rowHtml;
            document.querySelector('#students-table tbody').appendChild(row);
          }
        });
      });
    }


    $(document).on('click', '.evaluate-btn', function() {
        let studentId = $(this).data('student-id');
        let taskId = $(this).data('task-id');
        let studentClass = $(this).data('student-class');
        let student = $(this).data('student');

        // Загружаем критерии для выбранного задания
        openEvaluateModal(studentClass, taskId, studentId, student );
    });

    $(document).on('click', '#evaluate-modal-actions', function() {
        let studentId = $(this).data('student-id');
        let taskId = $(this).data('task-id');
        let studentClass = $(this).data('student-class');
        let student = $(this).data('student');

        // Загружаем критерии для выбранного задания
        openActionsModal(studentClass, taskId, studentId, student );
    });
    function openActionsModal(studentClass, taskId, studentId, student) {
        $.ajax({
            url: `/api/get-actions/`,
            data: { task_id: `${studentClass}_${taskId}`, student_id: studentId },
            success: function(response) {
                let modal_title = $('.actions-modal-title');
                modal_title.text(`Оцінка завдання ${studentClass}_${taskId}`);

                let modal_user_id = $('.actions-modal-user-id');
                modal_user_id.text(`Id учня ${studentId}`);

                let modal = $('#actions-modal');
                modal.data('task-id', taskId).data('studentClass', studentClass).data('studentId', studentId);
                let actionsContainer = $('#action-messages-container');
                actionsContainer.empty();

                response.actions.forEach((action, index) => {
                        const values = action.action_type === "update" ? Object.values(action.action_value) : "";
                        actionsContainer.append(`
                            <div class="action-container ${ action.action_type === "update" ? "update-msg" : "delete-msg" }" >
                                <span class="action-message">
                                    ${ action.action_type === "update" ? `Користувач ${action.action_performer} оновив оцінки критеріїв завдання: ${values.join(' | ')}` : `Користувач ${action.action_performer} очистив оцінку завдання`}
                                </span>
                                <span class="action-date">
                                    ${action.formatted_action_time}
                                </span>
                            </div>
                        `);
                    });
                modal.show();  // Show modal dialog
            }
        });
    }
    // Функция для открытия модального окна оценивания
    function openEvaluateModal(studentClass, taskId, studentId, student) {
        // Загружаем критерии для выбранного задания
        console.log(studentClass + "_"+ taskId+ "");
        let id = studentClass + "_" + taskId+ "_" + currentTour;
        if( !jury_tasks.includes(id) ){
            alert("У вас немає прав для оцінювання цього завдання");
            return;
        }
        $.ajax({
            url: `/api/criteria/`,
            data: { task_id: id },
            success: function(response) {
                if(response.criteria.length === 0) {
                    alert("Завдання не має критеріїв оцінювання або додані критерії не були затвердженні");
                    return;
                }

                let actions_button = $('#evaluate-modal-actions');
                actions_button.attr('data-student-id', studentId);
                actions_button.attr('data-task-id', taskId);
                actions_button.attr('data-student-class', studentClass);
                actions_button.attr('data-student', student);

                let modal_title = $('.modal-title');
                modal_title.text(`Оцінка завдання ${studentClass}_${taskId}`);

                let modal_user_id = $('.modal-user-id');
                modal_user_id.text(`Id учня ${studentId}`);

                let modal = $('#evaluate-modal');
                let tableBody = $('#criteria-table-body');
                tableBody.empty();
                modal.data('task-id', taskId).data('studentClass', studentClass).data('studentId', studentId);
                response.criteria.forEach((criterion, index) => {
                        tableBody.append(`
                            <tr>
                                <td class="td-text">${criterion.criterion_text}</td>
                                <td>
                                    <input class="input-criterion" type="text" name="criterion_${criterion.id}"
                                           data-max="${criterion.points}"
                                           placeholder="Макс ${criterion.points}"
                                           min="0"
                                           max="${criterion.points}"
                                           value="${student[`grading`] && student[`grading`][index] ? student[`grading`][index] : ''}"
                                           required
                                           />
                                </td>
                                <td>${criterion.points}</td>
                            </tr>
                        `);
                    });
                $('#modal-overlay').show();
                 $('body').css('overflow', 'hidden');
                modal.show();  // Show modal dialog
            }
        });
    }

    $('#form-clear-btn').on('click', function() {

        let modal = $('#evaluate-modal');
        let taskId = modal.data('task-id');
        let studentId = modal.data('student-id');
        let studentClass = modal.data('student-class');
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: profileConfig.apiClearEvaluationUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                student_id: studentId,
                task_id: taskId,
                student_class: studentClass,
            }),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken  // Включаем CSRF-токен
            },
            success: function(response) {
                console.log('Успешный ответ:', response);  // Лог успешного ответа
                if (response.success) {
                    hideOverlay();
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка AJAX-запроса:', error);  // Лог ошибок
                alert('Помилка під час збереження оцінки.');
            }
        });

        return false;
    });

    // Функция для отправки оценки
   $('#evaluation-form').on('submit', function(i) {
        i.preventDefault();  // Останавливаем стандартное поведение формы
        let hasErrors = false;
        let points = {};
        let modal = $('#evaluate-modal');
        let taskId = modal.data('task-id'); // Получаем ID задачи
        let studentId = modal.data('student-id');
        let student_class = modal.data('student-class');

        console.log(`taskId: ${taskId}, studentId: ${studentId}`);  // Лог для проверки

        let counter = 1;
        $('#criteria-table-body input[type="text"]').each(function() {
            let maxPoints = $(this).data('max');
            let value = parseFloat($(this).val().replace(',', '.'));

            if (isNaN(value)) {
                alert('Будь ласка, введіть правильне числове значення!');
                value = 0;  // Устанавливаем значение по умолчанию, если это не число
                hasErrors = true;
                return false;
            }

            if (value > maxPoints && value >= 0) {
                alert('Оцінка не може бути більша за максимальний бал!');
                value = maxPoints;  // Ограничиваем значение
                hasErrors = true;
                console.log("PROBLEM PROBLEM PROBLEM");
                return false;
            }
            points[counter] = value;  // Используем счетчик как ключ
            counter++;
        });
        if (hasErrors) {
            return; // Останавливаем выполнение функции
        }
        const csrftoken = getCookie('csrftoken');

        // Отправляем оценки на сервер
        $.ajax({
            url: profileConfig.apiEvaluateTaskUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                student_id: studentId,
                task_id: taskId,
                points: points,
                student_class: student_class,
            }),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            },
            success: function(response) {
                console.log('Успешный ответ:', response); // Success
                if (response.success) {
                    hideOverlay();
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка AJAX-запроса:', error); // Error
                alert('Помилка під час збереження оцінки.');
            }
        });

        return false;
   });

   document.querySelector('#evaluate-modal-close').addEventListener('click', () => {
       hideOverlay();
   });
   document.querySelector('#actions-modal-close').addEventListener('click', () => {
       hideActionsModal();
   });
   function hideActionsModal(){
        $('#actions-modal').hide();  // Hide modal dialog
   }
   function hideOverlay(){
        $('#evaluate-modal').hide();  // Hide modal dialog
        $('#modal-overlay').hide();
        $('body').css('overflow', '');
   }
});
