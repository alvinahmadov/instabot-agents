(function ($) {
    "use strict"; // Start of use strict
    $('#dropdownYear').each(function () {
        var year = (new Date()).getFullYear();
        var current = year;
        year = 2020;
        for (var i = 0; i < 6; i++) {
            if ((year + i) == current)
                $(this).append('<option class="btn btn-outline-primary" selected value="' + (year + i) + '">' + (year + i) + '</option>');
            else
                $(this).append('<option class="btn btn-outline-primary" value="' + (year + i) + '">' + (year + i) + '</option>');
        }
    });

    // Toggle the side navigation
    $("#sidebarToggle, #sidebarToggleTop").on('click', function () {
        $("body").toggleClass("sidebar-toggled");
        let sidebar = $(".sidebar");
        sidebar.toggleClass("toggled");

        if (sidebar.hasClass("toggled")) {
            console.log('has');
            $('.sidebar .collapse').collapse('hide');
            $(".menu-text").addClass('text-hide');
            localStorage.setItem('sidebarHidden', '');
        } else {
            console.log('no');
            $(".menu-text").removeClass("text-hide");
            localStorage.setItem('sidebarHidden', 'toggled')
        }
    });

    $(document).ready(function () {
        if (localStorage.getItem('sidebarHidden') === 'toggled') {
            $('.sidebar .collapse').collapse('hide');
        }
    });


    // Close any open menu accordions when window is resized below 768px
    $(window).resize(function () {
        if ($(window).width() < 768) {
            $('.sidebar .collapse').collapse('hide');
        }
    });

    // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
    $('body.fixed-nav .sidebar')
        .on('mousewheel DOMMouseScroll wheel', function (e) {
            if ($(window).width() > 768) {
                let e0 = e.originalEvent,
                    delta = e0.wheelDelta || -e0.detail;
                this.scrollTop += (delta < 0 ? 1 : -1) * 30;
                e.preventDefault();
            }
        });

    // Scroll to top button appear
    $(document).on('scroll', function () {
        let scrollDistance = $(this).scrollTop();
        if (scrollDistance > 100) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });

    // Smooth scrolling using jQuery easing
    $(document).on('click', 'a.scroll-to-top', function (e) {
        let $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: ($($anchor.attr('href')).offset().top)
        }, 1000, 'easeInOutExpo');
        e.preventDefault();
    });

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
})(jQuery); // End of use strict


function collapseStateWatcher(id, value_id, value) {
    $('#' + value_id).addClass(localStorage.getItem(value_id));

    $('#' + id).on('click', () => {
        if ($('#' + value_id).hasClass(value)) {
            localStorage.setItem(value_id, '')
        } else {
            localStorage.setItem(value_id, value)
        }
    });
}


function checkboxStateWatcher(id, value) {
    if (value === 'True')
        $('#' + id).prop('checked', true);
    else
        $('#' + id).prop('checked', false);
}

function saveStorage(item, key, value) {
    localStorage.setItem(key, value)
}

function logSelectedValue(sel, loc) {
    let currentValue = sel.options[sel.selectedIndex].value;
    localStorage.setItem('bot_id', currentValue);
    document.cookie = "bot_id=" + currentValue;
    loc.reload()
}

function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}