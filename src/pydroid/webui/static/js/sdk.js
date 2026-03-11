$(function () {
  const $search = $("[data-sdk-search]");
  const $cards = $("[data-sdk-card]");
  const $checkboxes = $("[data-sdk-checkbox]");
  const $selectedCount = $("[data-sdk-selected]");
  const $submit = $("[data-sdk-submit]");

  function norm(text) {
    return String(text || "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();
  }

  function updateSelected() {
    const selected = $checkboxes.filter(":checked").length;
    $selectedCount.text(selected);
    $submit.prop("disabled", selected === 0);
  }

  function setCardSelected($checkbox) {
    const isChecked = $checkbox.is(":checked");
    const $card = $checkbox.closest("[data-sdk-card]");
    $card.toggleClass("is-selected", isChecked);
  }

  function applyFilter() {
    const q = norm($search.val());
    $cards.each(function () {
      const $card = $(this);
      const hay = norm($card.attr("data-sdk-text"));
      const match = q.length === 0 || hay.indexOf(q) !== -1;
      $card.toggleClass("d-none", !match);
    });
  }

  // Initial state
  $checkboxes.each(function () {
    setCardSelected($(this));
  });
  updateSelected();
  applyFilter();

  // Events
  $(document).on("change", "[data-sdk-checkbox]", function () {
    setCardSelected($(this));
    updateSelected();
  });

  $search.on("input", function () {
    applyFilter();
  });

  $(document).on("click", "[data-sdk-select-visible]", function (e) {
    e.preventDefault();
    $cards
      .filter(":not(.d-none)")
      .find("[data-sdk-checkbox]")
      .prop("checked", true)
      .trigger("change");
  });

  $(document).on("click", "[data-sdk-clear]", function (e) {
    e.preventDefault();
    $checkboxes.prop("checked", false).trigger("change");
  });
});

