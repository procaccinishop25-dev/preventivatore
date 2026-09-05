(function () {
  let initialized = false;

  function handleRender(event) {
    const args = event.detail.args || {};

    if (!initialized) {
      initialized = true;
      document.getElementById("editor-title").textContent = args.title || "Schizzo";

      const width = args.width || 1100;
      const height = args.height || 700;

      DrawingEditor.init("fabric-canvas", width, height);
      ToolbarUI.init();

      if (args.initial_state) {
        DrawingEditor.loadState(args.initial_state);
      } else if (args.background_image_url) {
        DrawingEditor.loadImageAsObject(args.background_image_url);
      }

      window.Streamlit.setFrameHeight(height + 160);
    }
  }

  function handleSave() {
    const png = DrawingEditor.exportPNG();
    const state = DrawingEditor.exportState();
    window.Streamlit.setComponentValue({
      event: "save",
      png_base64: png,
      state_json: JSON.stringify(state),
      save_id: Date.now(),
    });
  }

  function handleBack() {
    window.Streamlit.setComponentValue({ event: "cancel", save_id: Date.now() });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("btn-save").addEventListener("click", handleSave);
    document.getElementById("btn-back").addEventListener("click", handleBack);
    window.Streamlit.events.addEventListener(window.Streamlit.RENDER_EVENT, handleRender);
    window.Streamlit.setComponentReady();
  });
})();
