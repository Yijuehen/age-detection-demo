document.addEventListener("DOMContentLoaded", function() {
    const fileInput = document.getElementById("file");
    const submitButton = document.querySelector("input[type='submit']");

    fileInput.addEventListener("change", function() {
        if (fileInput.files.length > 0) {
            submitButton.disabled = false;
        } else {
            submitButton.disabled = true;
        }
    });
});
