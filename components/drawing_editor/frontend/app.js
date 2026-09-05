(function () {
  let initialized = false;

  function calcolaDimensioniCanvas() {
    const wrapper = document.getElementById("canvas-wrapper");
    const paddingOrizzontale = 32; // 16px per lato, da CSS
    const larghezzaDisponibile = wrapper.clientWidth - paddingOrizzontale;
    const larghezza = Math.max(280, Math.min(larghezzaDisponibile, 1200));

    let altezza;
    if (larghezza < 600) {
      altezza = Math.min(Math.round(larghezza * 1.1), 550);
    } else {
      altezza = 700;
    }
    return { larghezza, altezza };
  }

  function adattaAltezzaFinestra() {
    requestAnimationFrame(function () {
      const altezzaReale = document.getElementById("app").scrollHeight;
      window.Streamlit.setFrameHeight(altezzaReale);
    });
  }

  function gestisciRidimensionamento() {
    const { larghezza, altezza } = calcolaDimensioniCanvas();
    DrawingEditor.resize(larghezza, altezza);
    adattaAltezzaFinestra();
  }

  function handleRender(event) {
    const args = event.detail.args || {};

    if (!initialized) {
      initialized = true;
      document.getElementById("editor-title").textContent = args.title || "Schizzo";

      const { larghezza, altezza } = calcolaDimensioniCanvas();

      DrawingEditor.init("fabric-canvas", larghezza, altezza);
      ToolbarUI.init();

      if (args.initial_state) {
        DrawingEditor.loadState(args.initial_state);
      } else if (args.background_image_url) {
        DrawingEditor.loadImageAsObject(args.background_image_url);
      }

      adattaAltezzaFinestra();

      let timerRidimensionamento = null;
      window.addEventListener("resize", function () {
        clearTimeout(timerRidimensionamento);
        timerRidimensionamento = setTimeout(gestisciRidimensionamento, 200);
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
