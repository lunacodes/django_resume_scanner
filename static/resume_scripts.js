document.getElementById("delete_warn").addEventListener("click", () => {
  let ask = confirm(
    "This will delete all resume files and associated keyword data. Are you sure you want to delete this?"
  );

  if (ask) {
    window.location.href = "deleteall";
  }
});
