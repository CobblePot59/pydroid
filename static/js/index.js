$(document).ready(function () {
    $("#data").DataTable({
        order: [[0, 'desc']],
        columns: [
            {orderable: true, searchable: true},
            {orderable: false, searchable: true},
            {orderable: false, searchable: false},
            {orderable: true, searchable: false},
            ],
        });
    $("#data2").DataTable({
        order: [[0, 'desc']],
        columns: [
            {orderable: false, searchable: true},
            {orderable: false, searchable: true},
            {orderable: false, searchable: false},
            ],
        });
});
