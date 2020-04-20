$(document).ready(
    function () {
        $.ajaxSetup({
            cache: false
        });
        const username = '{{ username }}';
        setInterval(function () {
            const min = 1;
            const max = 1000;
            let random = Math.floor(Math.random() * (+max - +min)) + +min;

            $('#show').load("{{ url_for('static', filename= username + 'info.txt')}}");
            setTimeout(function () {
                $('#show').scrollTop($('#show')[0].scrollHeight);

            }, 100);
        }, 7000);
    });
