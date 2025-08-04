!(function (NioApp, $) {
    "use strict";

    // Variable
    var $win = $(window), $body = $('body'), breaks = NioApp.Break;

    NioApp.Calendar = function () {

        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0');
        var yyyy = today.getFullYear();

        var tomorrow = new Date(today);
        tomorrow.setDate(today.getDate() + 1);
        var t_dd = String(tomorrow.getDate()).padStart(2, '0');
        var t_mm = String(tomorrow.getMonth() + 1).padStart(2, '0');
        var t_yyyy = tomorrow.getFullYear();

        var yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);
        var y_dd = String(yesterday.getDate()).padStart(2, '0');
        var y_mm = String(yesterday.getMonth() + 1).padStart(2, '0');
        var y_yyyy = yesterday.getFullYear();

        var YM = yyyy + '-' + mm;
        var YESTERDAY = y_yyyy + '-' + y_mm + '-' + y_dd;
        var TODAY = yyyy + '-' + mm + '-' + dd;
        var TOMORROW = t_yyyy + '-' + t_mm + '-' + t_dd;

        var month = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"];

        var initialLocaleCode = 'fa';
        var localeSelectorEl = document.getElementById('locale-selector');
        var calendarEl = document.getElementById('calendar');
        var eventsEl = document.getElementById('externalEvents');

        var removeEvent = document.getElementById('removeEvent');

        var addEventBtn = $('#addEvent');
        var addEventForm = $('#addEventForm');
        var addEventPopup = $('#addEventPopup');

        var updateEventBtn = $('#updateEvent');
        var editEventForm = $('#editEventForm');
        var editEventPopup = $('#editEventPopup');

        var previewEventPopup = $('#previewEventPopup');

        var deleteEventBtn = $('#deleteEvent');

        var mobileView = (NioApp.Win.width < NioApp.Break.md) ? true : false;

        var calendar = new FullCalendar.Calendar(calendarEl, {
            timeZone: 'UTC',
            initialView: mobileView ? 'listWeek' : 'dayGridMonth',
            themeSystem: 'bootstrap5',
            headerToolbar: {
                left: 'title prev,next',
                center: null,
                right: 'today dayGridMonth,timeGridWeek,timeGridDay,listWeek'
            },
            height: 800,
            contentHeight: 780,
            aspectRatio: 3,

            editable: true,
            droppable: true,
            views: {
                dayGridMonth: {
                    dayMaxEventRows: 2,
                }
            },
            direction: NioApp.State.isRTL ? "rtl" : "ltr",

            nowIndicator: true,
            now: TODAY + 'T09:25:00',

            // Add custom content to each day cell
            dayCellContent: function(info) {
                // Convert Gregorian date to Persian date
                var gregDate = info.date;
                var persianDate = new Intl.DateTimeFormat('fa-IR', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    calendar: 'persian'
                }).format(gregDate).split('/');

                // Get the Persian day number (keep it as string to preserve Persian numerals)
                var persianDayStr = persianDate[2];

                // Create the day number element
                var dayNumberEl = document.createElement('div');
                dayNumberEl.className = 'fc-daygrid-day-number';
                dayNumberEl.innerHTML = persianDayStr; // Use the string directly

                // Create the task creation button
                var taskBtnEl = document.createElement('button');
                taskBtnEl.className = 'btn btn-sm btn-outline-primary task-create-btn';
                taskBtnEl.innerHTML = '<i class="icon ni ni-plus"></i>';
                taskBtnEl.title = 'ایجاد وظیفه برای این روز';
                taskBtnEl.style.cssText = 'position: absolute; bottom: 5px; right: 5px; padding: 2px 4px; font-size: 10px; line-height: 1; z-index: 10; min-width: 20px; min-height: 20px;';

                // Add click event to redirect to task creation with deadline
                taskBtnEl.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    window.open('/task/create/?deadline=' + encodeURIComponent(persianDate.join('/')), '_blank');
                };

                // Create wrapper for day content
                var wrapperEl = document.createElement('div');
                wrapperEl.style.cssText = 'position: relative; width: 100%; height: 100%; min-height: 100px;';
                wrapperEl.appendChild(dayNumberEl);
                wrapperEl.appendChild(taskBtnEl);

                return { domNodes: [wrapperEl] };
            },

            // Add custom styling after render
            datesSet: function() {
                // Add hover effects for task creation buttons
                setTimeout(function() {
                    $('.task-create-btn').hover(
                        function() {
                            $(this).removeClass('btn-outline-primary').addClass('btn-primary');
                        },
                        function() {
                            $(this).removeClass('btn-primary').addClass('btn-outline-primary');
                        }
                    );
                }, 100);
            },

            eventMouseEnter: function (info) {
                let elm = info.el, title = info.event._def.title, content = info.event._def.extendedProps.description;
                if (content) {
                    const fcPopover = new bootstrap.Popover(elm, {
                        template: '<div class="popover event-popover"><div class="popover-arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>',
                        title: title,
                        content: content ? content : '',
                        placement: 'top',
                    })
                    fcPopover.show();
                }
            },
            eventMouseLeave: function () {
                removePopover();
            },
            eventDragStart: function () {
                removePopover();
            },
            eventClick: function (info) {
                // Get data
                var title = info.event._def.title;
                var description = info.event._def.extendedProps.description;
                var start = info.event._instance.range.start;
                var startDate = start.getFullYear() + '-' + String(start.getMonth() + 1).padStart(2, '0') + '/' + String(start.getDate()).padStart(2, '0');
                var startTime = start.toUTCString().split(' '); startTime = startTime[startTime.length - 2]; startTime = (startTime == '00:00:00') ? '' : startTime;
                var end = info.event._instance.range.end;
                var endDate = end.getFullYear() + '-' + String(end.getMonth() + 1).padStart(2, '0') + '/' + String(end.getDate()).padStart(2, '0');
                var endTime = end.toUTCString().split(' '); endTime = endTime[endTime.length - 2]; endTime = (endTime == '00:00:00') ? '' : endTime;
                var className = info.event._def.ui.classNames[0].slice(3);
                var eventId = info.event._def.publicId;

                //Set data in eidt form
                $('#edit-event-title').val(title);
                $('#edit-event-start-date').val(startDate).datepicker('update');
                $('#edit-event-end-date').val(endDate).datepicker('update');
                $('#edit-event-start-time').val(startTime);
                $('#edit-event-end-time').val(endTime);
                $('#edit-event-description').val(description);
                $('#edit-event-theme').val(className);
                $('#edit-event-theme').trigger('change.select2');
                editEventForm.attr('data-id', eventId);

                // Set data in preview
                var previewStart = String(start.getDate()).padStart(2, '0') + ' ' + month[start.getMonth()] + ' ' + start.getFullYear() + (startTime ? ' - ' + to12(startTime) : '');
                var previewEnd = String(end.getDate()).padStart(2, '0') + ' ' + month[end.getMonth()] + ' ' + end.getFullYear() + (endTime ? ' - ' + to12(endTime) : '');
                $('#preview-event-title').text(title);
                $('#preview-event-header').addClass('fc-' + className);
                $('#preview-event-start').text(previewStart);
                $('#preview-event-end').text(previewEnd);
                $('#preview-event-description').text(description);
                !description ? $('#preview-event-description-check').css('display', 'none') : null;

                removePopover();

                let fcMorePopover = document.querySelectorAll('.fc-more-popover');
                fcMorePopover && fcMorePopover.forEach(elm => {
                    elm.remove();
                })
                previewEventPopup.modal('show');
            },
        });
        calendar.render();

        //Add event
        addEventBtn.on("click", function (e) {
            e.preventDefault();
            var eventTitle = $('#event-title').val();
            var eventStartDate = $('#event-start-date').val();
            var eventEndDate = $('#event-end-date').val();
            var eventStartTime = $('#event-start-time').val();
            var eventEndTime = $('#event-end-time').val();
            var eventDescription = $('#event-description').val();
            var eventTheme = $('#event-theme').val();
            var eventStartTimeCheck = eventStartTime ? 'T' + eventStartTime + 'Z' : '';
            var eventEndTimeCheck = eventEndTime ? 'T' + eventEndTime + 'Z' : '';

            calendar.addEvent({
                id: 'added-event-id-' + Math.floor(Math.random() * 9999999),
                title: eventTitle,
                start: eventStartDate + eventStartTimeCheck,
                end: eventEndDate + eventEndTimeCheck,
                className: "fc-" + eventTheme,
                description: eventDescription,
            });
            addEventPopup.modal('hide');
        });

        updateEventBtn.on("click", function (e) {
            e.preventDefault();
            var eventTitle = $('#edit-event-title').val();
            var eventStartDate = $('#edit-event-start-date').val();
            var eventEndDate = $('#edit-event-end-date').val();
            var eventStartTime = $('#edit-event-start-time').val();
            var eventEndTime = $('#edit-event-end-time').val();
            var eventDescription = $('#edit-event-description').val();
            var eventTheme = $('#edit-event-theme').val();
            var eventStartTimeCheck = eventStartTime ? 'T' + eventStartTime + 'Z' : '';
            var eventEndTimeCheck = eventEndTime ? 'T' + eventEndTime + 'Z' : '';

            var selectEvent = calendar.getEventById(editEventForm[0].dataset.id);
            selectEvent.remove();
            calendar.addEvent({
                id: editEventForm[0].dataset.id,
                title: eventTitle,
                start: eventStartDate + eventStartTimeCheck,
                end: eventEndDate + eventEndTimeCheck,
                className: "fc-" + eventTheme,
                description: eventDescription,
            });
            editEventPopup.modal('hide');
        });

        deleteEventBtn.on("click", function (e) {
            e.preventDefault();
            var selectEvent = calendar.getEventById(editEventForm[0].dataset.id);
            selectEvent.remove();
        });

        function removePopover() {
            let fcPopover = document.querySelectorAll('.event-popover');
            fcPopover.forEach(elm => {
                elm.remove();
            })
        }

        function to12(time) {
            time = time.toString().match(/^([01]\d|2[0-3])(:)([0-5]\d)(:[0-5]\d)?$/) || [time];

            if (time.length > 1) {
                time = time.slice(1);
                time.pop();
                time[5] = +time[0] < 12 ? ' قبل از ظهر' : ' بعد از ظهر'; // Set AM/PM
                time[0] = +time[0] % 12 || 12;
            }
            time = time.join('');
            return time;
        }

        function customCalSelect(cat) {
            if (!cat.id) {
                return cat.text;
            }
            var $cat = $('<span class="fc-' + cat.element.value + '"> <span class="dot"></span>' + cat.text + '</span>');
            return $cat;
        };

        NioApp.Select2('.select-calendar-theme', {
            templateResult: customCalSelect
        });

        addEventPopup.on('hidden.bs.modal', function (e) {
            setTimeout(function () {
                $('#addEventForm input,#addEventForm textarea').val('');
                $('#event-theme').val('event-primary');
                $('#event-theme').trigger('change.select2');
            }, 1000);
        });

        previewEventPopup.on('hidden.bs.modal', function (e) {
            $('#preview-event-header').removeClass().addClass('modal-header');
        });

    };

    NioApp.coms.docReady.push(NioApp.Calendar);

})(NioApp, jQuery);