let user_class = profileConfig.userClass;

document.addEventListener("DOMContentLoaded", function() {
    const downloadTasks = document.querySelectorAll('.download-task');
    downloadTasks.forEach(task => {
        let id = task.getAttribute('id');
        task.setAttribute('href', '/uk/download/'+id+"_"+user_class+" клас 2 тур.pdf")
    });
});