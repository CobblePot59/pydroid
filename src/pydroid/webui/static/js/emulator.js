function postAndReload(url, payload) {
  return $.post(url, payload)
    .done(function () {
      window.location.reload();
    })
    .fail(function () {
      if (window.toastr) toastr.error("Something went wrong.");
    });
}

$(function () {
  $(document).on("click", "[data-emulator-action]", function (e) {
    e.preventDefault();

    const action = $(this).data("emulator-action");
    const name = $(this).data("emulator-name");
    if (!action || !name) return;

    if (action === "remove") {
      const ok = window.confirm(`Delete emulator "${name}"?`);
      if (!ok) return;
      return postAndReload("/removeEmulator", { sname: name });
    }

    if (action === "start") {
      if (window.toastr) toastr.info(`Starting "${name}"...`);
      return $.post("/startEmulator", { sname: name }).fail(function () {
        if (window.toastr) toastr.error("Failed to start emulator.");
      });
    }

    if (action === "root") {
      const ok = window.confirm(`Run root on "${name}"?`);
      if (!ok) return;
      if (window.toastr) toastr.info(`Rooting "${name}"...`);
      return $.post("/rootEmulator", { sname: name }).fail(function () {
        if (window.toastr) toastr.error("Failed to start root.");
      });
    }
  });
});

// function addCA(name) {
//     $.post('/addCA', { sname: name }, function(data) {
//     });
// }

// function addFrida(name) {
//     $.post('/addFrida', { sname: name }, function(data) {
//     });
// }
