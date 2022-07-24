// Initial date range filter
var minDate, maxDate

$.fn.dataTable.ext.search.push(function (settings, data) {
    var min = new Date(minDate).getTime();
    var max = new Date(maxDate).getTime();
    var table_date = data[1].split(".")[2] + '-' + data[1].split(".")[1] + '-' + data[1].split(".")[0]
    var date = new Date(table_date).getTime();

    if (
        (isNaN(min) && isNaN(max)) ||
        (isNaN(min) && date <= max) ||
        (min <= date && isNaN(max)) ||
        (min <= date && date <= max)
    ) {
        return true;
    }
    return false;
});
//


$(document).ready(function () {
    var date_input = $('#id_date')

    //Date range picker
    date_input.daterangepicker({
        timePicker: false,
        timePickerIncrement: 30,
        autoUpdateInput: false,

        locale: {
            format: 'DD.MM.YYYY',
            "applyLabel": "Ок",
            "cancelLabel": "Отмена",
            "fromLabel": "От",
            "toLabel": "До",
            "customRangeLabel": "Произвольный",
            "daysOfWeek": [
                "Вс",
                "Пн",
                "Вт",
                "Ср",
                "Чт",
                "Пт",
                "Сб"
            ],
            "monthNames": [
                "Январь",
                "Февраль",
                "Март",
                "Апрель",
                "Май",
                "Июнь",
                "Июль",
                "Август",
                "Сентябрь",
                "Октябрь",
                "Ноябрь",
                "Декабрь"
            ],
            firstDay: 1
        }
    });


    // Setup - add a text input to each footer cell
    $('#table_cash_box tfoot th').each(function () {
        $(this).html('<input type="text" name="custom_search"/>');
    });


    // DataTable
    var table = $('#table_cash_box').DataTable({
        dom: 'Bfrtip',
        buttons: [
            'excel'
        ],
        "responsive": false,
        'pageLength': 10,
        'paging': true,
        'lengthChange': false,
        'searching': true,
        'ordering': true,
        'info': true,
        'autoWidth': true,
        'columnDefs': [
            {
                'orderable': false,
                'targets': [0, 2, 3, 4, 5, 6, 7, 8]
            }
        ],
        order: [],
        "language": {
            "infoFiltered": "(Отфильтровано _MAX_ записей)",
            "zeroRecords": "Записей не найдено",
            "info": "",
            "infoEmpty": "Нет записей.",
            "paginate": {
                "previous": '<i class="fa fa-angle-left" style="color: #337AB7"></i>',
                "last": "Последняя",
                "next": '<i class="fa fa-angle-right" style="color: #337AB7"></i>',
            }
        },

        initComplete: function () {
            // Apply the search
            this.api()
                .columns([0, 5])
                .every(function () {
                    var that = this;
                    $('input', this.footer()).on('keyup change clear', function () {
                        if (that.search() !== this.value) {
                            that.search(this.value).draw();
                        }
                    });
                });
            this.api()
                .columns([2, 3, 4, 6])

                .every(function () {
                    var column = this;
                    var select = $('<select name="custom_select"><option value="">Выберите</option></select>')
                        .appendTo($(column.footer()).empty())
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex($(this).val());

                            column.search(val ? '^' + val + '$' : '', true, false).draw();
                        });

                    column
                        .data()
                        .unique()
                        .sort()
                        .each(function (d, j) {
                            var val = $('<div/>').html(d).text();
                            select.append('<option value="' + val + '">' + val + '</option>');
                        });
                });
        },
    });

    // export to excel
    $('.buttons-excel').css('display', 'none')
    $('#export').on("click", function () {
        table.buttons('.buttons-excel').trigger('click');
    })
    //

    // clean button
    $("#table_cash_box_filter").css('display', 'none')
    $("#clean").on("click", function () {
        $('input').val('');
        $('select').val('');
        minDate = ''
        maxDate = ''
        table.columns().search("").draw();
    })
    //


    // daterange
    date_input.on('apply.daterangepicker', function (ev, picker) {
        minDate = new Date(picker.startDate).getTime();
        maxDate = new Date(picker.endDate).getTime();
        $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
        table.draw();
    });

    date_input.on('cancel.daterangepicker', function () {
        $(this).val('');
        minDate = ''
        maxDate = ''
        table.draw();
    });
    //


    // total
    table.on('draw', function () {
        var income = []
        var expense = []

        table.column(7, {search: 'applied'}).nodes().to$().each(function (d, j) {
            if ($(j).attr('data-filter') === 'income') {
                income.push($(j).attr('value'))
            }
        })

        table.column(7, {search: 'applied'}).nodes().to$().each(function (d, j) {
            if ($(j).attr('data-filter') === 'expense') {
                expense.push($(j).attr('value'))
            }
        })


        $("#pri").html(parseFloat(income.reduce(totals, 0)).toFixed(2).toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, " ") + ' грн')
        $("#ras").html(parseFloat(expense.reduce(totals, 0)).toFixed(2).toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, " ") + ' грн')

        function totals(b, a) {
            return parseFloat(b) + parseFloat(a)
        }

    })

    var income = []
    var expense = []

    table.column(7).nodes().to$().each(function (d, j) {
        if ($(j).attr('data-filter') === 'income') {
            income.push($(j).attr('value'))
        }
    })

    table.column(7).nodes().to$().each(function (d, j) {
        if ($(j).attr('data-filter') === 'expense') {
            expense.push($(j).attr('value'))
        }
    })
    $("#pri").html(parseFloat(income.reduce(totals, 0)).toFixed(2).toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, " ") + ' грн')
    $("#ras").html(parseFloat(expense.reduce(totals, 0)).toFixed(2).toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, " ") + ' грн')

    function totals(b, a) {
        return parseFloat(b) + parseFloat(a)
    }

    //
});

