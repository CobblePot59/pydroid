(function () {
  function getModalEl() {
    return document.getElementById("pydroidLoadingModal");
  }

  function getTitleEl(modalEl) {
    return modalEl ? modalEl.querySelector("[data-loading-title]") : null;
  }

  function getSubtextEl(modalEl) {
    return modalEl ? modalEl.querySelector("[data-loading-subtext]") : null;
  }

  function showLoading(opts) {
    const modalEl = getModalEl();
    if (!modalEl || !window.bootstrap || !bootstrap.Modal) return;

    const titleEl = getTitleEl(modalEl);
    const subtextEl = getSubtextEl(modalEl);

    const title = (opts && opts.title) || "Working...";
    const subtext = (opts && opts.subtext) || "Please wait. This can take a while.";

    if (titleEl) titleEl.textContent = title;
    if (subtextEl) subtextEl.textContent = subtext;

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl, {
      backdrop: "static",
      keyboard: false,
    });
    modal.show();
  }

  function hideLoading() {
    const modalEl = getModalEl();
    if (!modalEl || !window.bootstrap || !bootstrap.Modal) return;
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.hide();
  }

  window.PydroidLoading = {
    show: showLoading,
    hide: hideLoading,
  };

  function jsonOrNull(xhr) {
    try {
      return xhr && xhr.responseJSON ? xhr.responseJSON : null;
    } catch (_) {
      return null;
    }
  }

  function errorMsg(xhr) {
    const j = jsonOrNull(xhr);
    if (j && j.error) return j.error;
    return "Something went wrong.";
  }

  $(function () {
    $(document).on("submit", "form[data-ajax-form]", function (e) {
      e.preventDefault();

      const $form = $(this);
      const action = $form.attr("action");
      const method = String($form.attr("method") || "POST").toUpperCase();
      if (!action) return;

      const selectedCount = $form.find('input[name="checkbox"]:checked').length;
      const baseTitle = $form.data("loadingText") || $form.data("loading-text") || "Working...";
      const title = selectedCount ? `${baseTitle} (${selectedCount})` : baseTitle;

      const $submit = $form.find('[type="submit"]').first();
      $submit.prop("disabled", true);
      showLoading({ title: title });

      $.ajax({
        url: action,
        method: method,
        data: $form.serialize(),
        headers: { "X-Requested-With": "XMLHttpRequest" },
        dataType: "json",
      })
        .done(function (res) {
          if (res && res.redirect) {
            window.location.href = res.redirect;
            return;
          }
          window.location.reload();
        })
        .fail(function (xhr) {
          hideLoading();
          $submit.prop("disabled", false);
          if (window.toastr) toastr.error(errorMsg(xhr));
          else window.alert(errorMsg(xhr));
        });
    });
  });
})();

