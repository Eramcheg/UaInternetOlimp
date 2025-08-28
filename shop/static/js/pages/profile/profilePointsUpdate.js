document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const classId = this.getAttribute('data-class');

            tabs.forEach(t => t.classList.remove('active-tab'));
            const contents = document.querySelectorAll('.content');
            contents.forEach(content => content.classList.remove('active-content'));

            this.classList.add('active-tab');
            document.getElementById(classId).classList.add('active-content');
        });
    });
});
document.querySelectorAll(".clear-btn").forEach(button =>
    button.addEventListener('click', function () {
        const parent = button.closest('.update-field');
        const input = parent.querySelector('.max-score');
        if (input) {
            input.value = '';
        }
    }
));
document.getElementsByName('max-score').forEach(element => element.addEventListener('input', function () {
    const value = this.value;
    if (value < 0) {
        if(value !== "") {
            alert('Введіть числове значення більше бао дорівнює 0');
        }
        this.value = '';
    }
}));

document.querySelectorAll('.task-form').forEach(form => {
    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent the normal form submission

        const formData = new FormData(this); // Use 'this' to reference the current form
        const csrftoken = getCookie('csrftoken'); // Ensure you have csrftoken available

        fetch(this.action, { // Use the action attribute of the form
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(json => {
                    throw new Error(json.message || "Щось пішло не так...");
                });
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            alert("Інформацію було оновлено!");
            // Optionally update UI elements like the current points span
            this.closest('.upload-box').querySelector('.current-points').textContent = `Бали за задачу: ${formData.get('max_score')}`;
            this.querySelector('.max-score').value = '';
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message); // Display the error message from the catch or throw
        });
    });
});