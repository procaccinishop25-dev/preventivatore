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

    document.getElementById("color-picker").addEventListener("input", function (e) {
      DrawingEditor.setColor(e.target.value);
    });

    document.getElementById("btn-undo").addEventListener("click", function () { DrawingEditor.undo(); });
    document.getElementById("btn-redo").addEventListener("click", function () { DrawingEditor.redo(); });
  }

  function setActiveTool(tool) {
    document.querySelectorAll(".tool-btn[data-tool]").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-tool") === tool);
    });
    const labels = {
      select: "Seleziona", pen: "Penna", eraser: "Gomma",
      line: "Linea", rect: "Rettangolo", circle: "Cerchio", photo: "Foto",
    };
    document.getElementById("status-tool").textContent = labels[tool] || tool;
  }

  return { init, setActiveTool };
})();
