// app/static/js/autocomplete.js
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("city-input");
    const suggestions = document.getElementById("suggestions");

    input.addEventListener("input", async () => {
        const query = input.value;
        if (query.length < 2) {
            suggestions.innerHTML = "";
            return;
        }

        // потом подставим сюда fetch("/autocomplete?q=" + query)
        suggestions.innerHTML = `<li>Подсказки будут позже...</li>`;
    });
});
