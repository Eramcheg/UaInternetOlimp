let user_info = profileConfig.user_info_dict;
document.getElementById('fileInput').addEventListener('change', function(event) {
    if (event.target.files.length > 0) {
        document.getElementById('currentProfilePicture').src = URL.createObjectURL(event.target.files[0]);
    }
});
document.addEventListener("DOMContentLoaded", function() {
    // Select the button by its data-action attribute
    setCurrentSelects();
    const togglePasswordButtons = document.querySelectorAll('button[data-action="show-password"]');

    // Listen for a click event on the button
    togglePasswordButtons.forEach(togglePasswordButton =>
        togglePasswordButton.addEventListener('click', function() {
            // Select the password input
            const passwordInput = this.parentElement.parentElement.querySelector('input');

            // Check the current type of the password input and toggle
            if (passwordInput.type === "password") {
                passwordInput.type = "text"; // Show the password
                // Change the SVG to 'eye'
                togglePasswordButton.innerHTML = '<i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg></i>';
            } else {
                passwordInput.type = "password"; // Hide the password
                // Change the SVG back to 'eye-off'
                togglePasswordButton.innerHTML = '<i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye-off"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg></i>';
            }
        })
    );
});

window.onload = function() {
    document.getElementsByName("password")[0].value = "";
};

function isValidBirthday(birthday) {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!birthday.match(regex)) return false; // Checks format

    const date = new Date(birthday);
    const timestamp = date.getTime();

    if (typeof timestamp !== 'number' || Number.isNaN(timestamp)) return false; // Checks existence

    if (date.toISOString().slice(0, 10) !== birthday) return false; // Ensures the date is valid (e.g., not Feb 30)

    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normalize today's date to ensure comparison is only based on date, not time

    if (date > today) return false; // Checks that the birthday is not in the future

    return true; // The birthday passes all checks
}

document.getElementById('customer-form').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the normal form submission

    // Validation logic here
    let isValid = true;
    let messages = [];

    // Example: Check if the first name is filled out
    if (!this.firstname.value) {
        isValid = false;
        messages.push("Ім'я є обов'язковим до заповнення");
    }
    if (!this.lastname.value) {
        isValid = false;
        messages.push("Прізвише є обов'язковим до заповнення");
    }
    if (!this.email.value) {
        isValid = false;
        messages.push("Емейл є обов'язковим до заповнення");
    }
    if (!this.password.value) {
        isValid = false;
        messages.push("Пароль є обов'язковим до заповнення");
    }
    const dateFormatRegex = /^\d{4}-\d{2}-\d{2}$/;


    // If not valid, display messages and return
    if (!isValid) {
        alert(messages.join("\n")); // Or display the messages in a more user-friendly way
        return;
    }

    const formData = new FormData(document.getElementById('customer-form'));
    formData.append('old', JSON.stringify(user_info));
    formData.append('new', JSON.stringify(Object.fromEntries(formData.entries())));

    console.log(new FormData(this));
    const csrftoken = getCookie('csrftoken');

    fetch(profileConfig.urlUpdateUserAccount, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken, // Ensure you have csrftoken available
        },
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            // If response is not ok, parse the JSON to get the error message
            // and throw it to be caught by the catch block
            return response.json().then(json => {
                throw new Error(json.message || "Щось пішло не так...");
            });
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        alert("Інформацію було оновлено!");
        window.location.href = profileConfig.urlProfileAccount;
        // Handle success response data
    }).catch(error => {
        console.error('Error:', error);
        alert(error.message); // Display the error message from the catch or throw
    });
});
function setCurrentSelects(){
     let paralel = user_info.paralel;  // From your Django template
     let selectParalel = document.getElementById('select-paralel');
     for (let i = 0; i < selectParalel.length; i++) {
         if (selectParalel.options[i].text === paralel) {
             selectParalel.selectedIndex = i;
             break;
         }
     }
 }