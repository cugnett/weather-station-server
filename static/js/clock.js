    function clock() {
        var clockElement = document.getElementById('clock');
        var date = new Date();
        clockElement.textContent = 'Nous sommes le ' + date.toLocaleDateString() + ' à ' + date.toLocaleTimeString();
    }
    setInterval(clock, 1000);