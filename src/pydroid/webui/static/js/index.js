$(function () {
  const $emulatorsTable = $("#emulatorsTable");
  if ($emulatorsTable.length) {
    $emulatorsTable.DataTable({
      order: [[0, "asc"]],
      columns: [
        { orderable: true, searchable: true },
        { orderable: true, searchable: true },
        { orderable: false, searchable: false },
      ],
    });
  }
});
