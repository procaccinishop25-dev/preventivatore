(function () {
  let initialized = false;
  let resizeTimer = null;

  function misuraViewport() {
    const wrapper = document.getElementById("canvas-wrapper");
    return {
      larghezza: wrapper.clientWidth,
      altezza: wrapper.clientHeight,
    };
  }

  function rifitta() {
    const { larghezza, altezza } = misuraViewport();
    DrawingEditor.resetFit(larghezza, altezza);
  }

  function ottieniAltezzaDisponibile() {
    try {
      if (window.parent && window.parent !== window) {
        return window.parent.innerHeight;
      }
    } catch (e) {
      // accesso bloccato (raro, cross-origin): uso il fallback qui sotto
    }
    return window.screen.availHeight || window.innerHeight || 800;
  }

  function impostaAltezzaComponente() {
    const altezza = ottieniAltezzaDisponibile();
    window.Streamlit.setFrameHeight(altezza);
  }

  function gestisciRidimensionamento() {
    impostaAltezzaComponente();
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        const { larghezza, altezza } = misuraViewport();
        DrawingEditor.onResize(larghezza, altezza);
      });
    });
  }

  function handleRender(event) {
    const args = event.detail.args || {};

    if (!initialized) {
      initialized = true;
      document.getElementById("editor-title").textContent = args.title || "Schizzo";

      impostaAltezzaComponente();

      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          const { larghezza, altezza } = misuraViewport();

          DrawingEditor.init("fabric-canvas", "canvas-wrapper");
          DrawingEditor.fitToScreen(larghezza, altezza);
          ToolbarUI.init();

          if (args.initial_state) {
            DrawingEditor.loadState(args.initial_state);
          } else if (args.background_image_url) {
            DrawingEditor.loadImageAsObject(args.background_image_url);
          }
        });
      });

      const resizeObserver = new ResizeObserver(function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(gestisciRidimensionamento, 120);
      });
      resizeObserver.observe(document.getElementById("app"));

      window.addEventListener("orientationchange", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(gestisciRidimensionamento, 300);
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

  window.AppLayout = { rifitta };
})();
