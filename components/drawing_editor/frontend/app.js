(function () {
  let initialized = false;

  function calcolaAltezzaTarget() {
    const altezzaSchermo = window.screen.availHeight || window.screen.height || 800;
    let altezza = Math.round(altezzaSchermo * 0.85);
    altezza = Math.max(500, Math.min(altezza, 900));
    return altezza;
  }

  function misuraCanvasDaWrapper() {
    const wrapper = document.getElementById("canvas-wrapper");
    const larghezza = Math.max(280, wrapper.clientWidth - 24);
    const altezza = Math.max(300, wrapper.clientHeight - 24);
    return { larghezza, altezza };
  }

  function gestisciRidimensionamento() {
    const altezzaTarget = calcolaAltezzaTarget();
    window.Streamlit.setFrameHeight(altezzaTarget);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        const { larghezza, altezza } = misuraCanvasDaWrapper();
        DrawingEditor.resize(larghezza, altezza);
      });
    });
  }

  function handleRender(event) {
    const args = event.detail.args || {};

    if (!initialized) {
      initialized = true;
      document.getElementById("editor-title").textContent = args.title || "Schizzo";

      const altezzaTarget = calcolaAltezzaTarget();
      window.Streamlit.setFrameHeight(altezzaTarget);

      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          const { larghezza, altezza } = misuraCanvasDaWrapper();

          DrawingEditor.init("fabric-canvas", larghezza, altezza);
          ToolbarUI.init();

          if (args.initial_state) {
            DrawingEditor.loadState(args.initial_state);
          } else if (args.background_image_url) {
            DrawingEditor.loadImageAsObject(args.background_image_url);
          }
        });
      });

      let timerRidimensionamento = null;
      window.addEventListener("resize", function () {
        clearTimeout(timerRidimensionamento);
        timerRidimensionamento = setTimeout(gestisciRidimensionamento, 200);
      });
      window.addEventListener("orientationchange", function () {
        clearTimeout(timerRidimensionamento);
        timerRidimensionamento = setTimeout(gestisciRidimensionamento, 300);
      });
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
