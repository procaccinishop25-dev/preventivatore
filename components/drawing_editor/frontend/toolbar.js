const ToolbarUI = (function () {
  function init() {
    document.querySelectorAll(".tool-btn[data-tool]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const tool = btn.getAttribute("data-tool");
        if (tool === "photo") {
          document.getElementById("photo-input").click();
          return;
        }
        setActiveTool(tool);
        DrawingEditor.setTool(tool);
      });
    });

    document.getElementById("photo-input").addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function (evt) {
        DrawingEditor.addPhotoFromDataUrl(evt.target.result);
      };
      reader.readAsDataURL(file);
      e.target.value = "";
    });

    document.querySelectorAll(".color-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.querySelectorAll(".color-btn").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        DrawingEditor.setColor(btn.getAttribute("data-color"));

        const toolAttivoBtn = document.querySelector(".tool-btn.active");
        if (toolAttivoBtn) {
          DrawingEditor.setTool(toolAttivoBtn.getAttribute("data-tool"));
        }
      });
    });

    document.getElementById("btn-undo").addEventListener("click", function () { DrawingEditor.undo(); });
    document.getElementById("btn-redo").addEventListener("click", function () { DrawingEditor.redo(); });
    document.getElementById("btn-delete").addEventListener("click", function () { DrawingEditor.eliminaOggettoSelezionato(); });

    document.getElementById("btn-zoom-in").addEventListener("click", function () { DrawingEditor.zoomIn(); });
    document.getElementById("btn-zoom-out").addEventListener("click", function () { DrawingEditor.zoomOut(); });
    document.getElementById("zoom-label").addEventListener("click", function () {
      if (window.AppLayout) window.AppLayout.rifitta();
    });
  }

  function setActiveTool(tool) {
    document.querySelectorAll(".tool-btn[data-tool]").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-tool") === tool);
    });
  }

  return { init, setActiveTool };
})();
