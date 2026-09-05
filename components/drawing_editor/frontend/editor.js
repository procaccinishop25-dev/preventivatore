const DrawingEditor = (function () {
  const DOCUMENT_WIDTH = 1400;
  const DOCUMENT_HEIGHT = 900;
  const ZOOM_MIN = 0.2;
  const ZOOM_MAX = 5;
  const ZOOM_STEP = 0.15;

  let canvas = null;
  let wrapperEl = null;
  let currentTool = "select";
  let currentColor = "#000000";
  let historyStack = [];
  let historyIndex = -1;
  let isRestoring = false;
  let isDrawingShape = false;
  let isErasingActive = false;
  let shapeOrigin = null;
  let activeShape = null;

  let pinchState = null;
  let statoPreImdiscocinta = null; // stato drawingMode/selection salvato prima del pinch

  function init(canvasId, wrapperId) {
    wrapperEl = document.getElementById(wrapperId);

    canvas = new fabric.Canvas(canvasId, {
      selection: true,
      backgroundColor: "#ffffff",
      preserveObjectStacking: true,
    });

    canvas.on("object:added", pushHistoryIfNeeded);
    canvas.on("object:modified", pushHistoryIfNeeded);
    canvas.on("object:removed", pushHistoryIfNeeded);
    canvas.on("path:created", pushHistoryIfNeeded);

    canvas.on("mouse:down", handleMouseDown);
    canvas.on("mouse:move", handleMouseMove);
    canvas.on("mouse:up", handleMouseUp);

    attachPinchHandlers();

    pushHistory();
    return canvas;
  }

  // ================== VIEWPORT: documento fisso, finestra variabile ==================

  function fitToScreen(viewportWidth, viewportHeight) {
    canvas.setWidth(viewportWidth);
    canvas.setHeight(viewportHeight);

    const zoom = Math.min(
      viewportWidth / DOCUMENT_WIDTH,
      viewportHeight / DOCUMENT_HEIGHT
    );
    applyZoomCentrato(zoom);
  }

  function applyZoomCentrato(zoom) {
    zoom = Math.max(ZOOM_MIN, Math.min(zoom, ZOOM_MAX));
    const panX = (canvas.getWidth() - DOCUMENT_WIDTH * zoom) / 2;
    const panY = (canvas.getHeight() - DOCUMENT_HEIGHT * zoom) / 2;
    canvas.setViewportTransform([zoom, 0, 0, zoom, panX, panY]);
    canvas.renderAll();
    aggiornaEtichettaZoom();
  }

  function onResize(viewportWidth, viewportHeight) {
    fitToScreen(viewportWidth, viewportHeight);
  }

  function zoomIn() {
    applyZoomCentratoIncrementale(ZOOM_STEP);
  }

  function zoomOut() {
    applyZoomCentratoIncrementale(-ZOOM_STEP);
  }

  function applyZoomCentratoIncrementale(delta) {
    const zoomAttuale = canvas.getZoom();
    const nuovoZoom = Math.max(ZOOM_MIN, Math.min(zoomAttuale + delta, ZOOM_MAX));
    const centro = new fabric.Point(canvas.getWidth() / 2, canvas.getHeight() / 2);
    canvas.zoomToPoint(centro, nuovoZoom);
    canvas.renderAll();
    aggiornaEtichettaZoom();
  }

  function resetFit(viewportWidth, viewportHeight) {
    fitToScreen(viewportWidth, viewportHeight);
  }

  function aggiornaEtichettaZoom() {
    const label = document.getElementById("zoom-label");
    if (label) label.textContent = Math.round(canvas.getZoom() * 100) + "%";
  }

  // ================== PINCH-ZOOM E PAN A DUE DITA ==================

  function distanzaTraDitaTouches(touches) {
    const dx = touches[0].clientX - touches[1].clientX;
    const dy = touches[0].clientY - touches[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  function puntoMedioTouches(touches) {
    return {
      x: (touches[0].clientX + touches[1].clientX) / 2,
      y: (touches[0].clientY + touches[1].clientY) / 2,
    };
  }

  function attachPinchHandlers() {
    wrapperEl.addEventListener("touchstart", function (e) {
      if (e.touches.length === 2) {
        e.preventDefault();
        e.stopPropagation();

        statoPreImdiscocinta = {
          isDrawingMode: canvas.isDrawingMode,
          selection: canvas.selection,
        };
        canvas.isDrawingMode = false;
        canvas.selection = false;
        canvas.discardActiveObject();
        canvas.requestRenderAll();

        const rect = canvas.upperCanvasEl.getBoundingClientRect();
        pinchState = {
          initialDistance: distanzaTraDitaTouches(e.touches),
          initialZoom: canvas.getZoom(),
          initialMidpoint: puntoMedioTouches(e.touches),
          canvasRect: rect,
        };
      }
    }, { capture: true, passive: false });

    wrapperEl.addEventListener("touchmove", function (e) {
      if (e.touches.length === 2 && pinchState) {
        e.preventDefault();
        e.stopPropagation();

        const nuovaDistanza = distanzaTraDitaTouches(e.touches);
        const scala = nuovaDistanza / pinchState.initialDistance;
        let nuovoZoom = pinchState.initialZoom * scala;
        nuovoZoom = Math.max(ZOOM_MIN, Math.min(nuovoZoom, ZOOM_MAX));

        const midpoint = puntoMedioTouches(e.touches);
        const puntoZoom = new fabric.Point(
          midpoint.x - pinchState.canvasRect.left,
          midpoint.y - pinchState.canvasRect.top
        );
        canvas.zoomToPoint(puntoZoom, nuovoZoom);

        const dx = midpoint.x - pinchState.initialMidpoint.x;
        const dy = midpoint.y - pinchState.initialMidpoint.y;
        canvas.relativePan(new fabric.Point(dx, dy));

        pinchState.initialMidpoint = midpoint;
        canvas.renderAll();
        aggiornaEtichettaZoom();
      }
    }, { capture: true, passive: false });

    function terminaPinch(e) {
      if (e.touches.length < 2 && pinchState) {
        pinchState = null;
        if (statoPreImdiscocinta) {
          canvas.isDrawingMode = statoPreImdiscocinta.isDrawingMode;
          canvas.selection = statoPreImdiscocinta.selection;
          statoPreImdiscocinta = null;
        }
      }
    }
    wrapperEl.addEventListener("touchend", terminaPinch, { capture: true, passive: false });
    wrapperEl.addEventListener("touchcancel", terminaPinch, { capture: true, passive: false });
  }

  // ================== STORICO (UNDO/REDO) ==================

  function pushHistoryIfNeeded() {
    if (isRestoring) return;
    pushHistory();
  }

  function pushHistory() {
    const json = JSON.stringify(canvas.toJSON());
    historyStack = historyStack.slice(0, historyIndex + 1);
    historyStack.push(json);
    historyIndex = historyStack.length - 1;
  }

  function undo() {
    if (historyIndex <= 0) return;
    historyIndex -= 1;
    restoreFromHistory();
  }

  function redo() {
    if (historyIndex >= historyStack.length - 1) return;
    historyIndex += 1;
    restoreFromHistory();
  }

  function restoreFromHistory() {
    isRestoring = true;
    const json = historyStack[historyIndex];
    canvas.loadFromJSON(json, function () {
      canvas.renderAll();
      isRestoring = false;
    });
  }

  function loadState(stateObj) {
    isRestoring = true;
    canvas.loadFromJSON(stateObj, function () {
      canvas.renderAll();
      isRestoring = false;
      pushHistory();
    });
  }

  // ================== OGGETTI: FOTO ==================

  function loadImageAsObject(url) {
    fabric.Image.fromURL(url, function (img) {
      const maxDim = Math.min(DOCUMENT_WIDTH, DOCUMENT_HEIGHT) * 0.6;
      if (img.width > maxDim || img.height > maxDim) {
        const scale = maxDim / Math.max(img.width, img.height);
        img.scale(scale);
      }
      img.set({ left: 40, top: 40 });
      canvas.add(img);
      canvas.renderAll();
    }, { crossOrigin: "anonymous" });
  }

  function addPhotoFromDataUrl(dataUrl) {
    fabric.Image.fromURL(dataUrl, function (img) {
      const maxDim = Math.min(DOCUMENT_WIDTH, DOCUMENT_HEIGHT) * 0.5;
      if (img.width > maxDim || img.height > maxDim) {
        const scale = maxDim / Math.max(img.width, img.height);
        img.scale(scale);
      }
      img.set({ left: DOCUMENT_WIDTH / 2 - (img.width * (img.scaleX || 1)) / 2, top: DOCUMENT_HEIGHT / 2 - (img.height * (img.scaleY || 1)) / 2 });
      canvas.add(img);
      canvas.setActiveObject(img);
      canvas.renderAll();
    });
  }

  // ================== STRUMENTI ==================

  function setColor(color) {
    currentColor = color;
    if (currentTool === "pen" && canvas.freeDrawingBrush) {
      canvas.freeDrawingBrush.color = currentColor;
    }
  }

  function setTool(tool) {
    currentTool = tool;
    canvas.isDrawingMode = false;
    canvas.selection = true;
    canvas.defaultCursor = "default";
    canvas.hoverCursor = "move";
    canvas.forEachObject(function (obj) { obj.selectable = true; });

    if (tool === "pen") {
      canvas.isDrawingMode = true;
      canvas.freeDrawingBrush = new fabric.PencilBrush(canvas);
      canvas.freeDrawingBrush.width = 3;
      canvas.freeDrawingBrush.color = currentColor;
    } else if (tool === "eraser") {
      canvas.selection = false;
      canvas.defaultCursor = "crosshair";
      canvas.hoverCursor = "crosshair";
      canvas.forEachObject(function (obj) { obj.selectable = false; });
    }
  }

  function eliminaOggettoSottoPuntatore(e) {
    const target = canvas.findTarget(e, false);
    if (target) {
      canvas.remove(target);
      canvas.requestRenderAll();
    }
  }

  function eliminaOggettoSelezionato() {
    const attivo = canvas.getActiveObject();
    if (attivo) {
      canvas.remove(attivo);
      canvas.discardActiveObject();
      canvas.requestRenderAll();
    }
  }

  function handleMouseDown(opt) {
    if (currentTool === "eraser") {
      isErasingActive = true;
      eliminaOggettoSottoPuntatore(opt.e);
      return;
    }
    if (["line", "rect", "circle"].indexOf(currentTool) === -1) return;

    isDrawingShape = true;
    const pointer = canvas.getPointer(opt.e);
    shapeOrigin = { x: pointer.x, y: pointer.y };

    if (currentTool === "line") {
      activeShape = new fabric.Line([pointer.x, pointer.y, pointer.x, pointer.y], {
        stroke: currentColor, strokeWidth: 3, selectable: false,
      });
    } else if (currentTool === "rect") {
      activeShape = new fabric.Rect({
        left: pointer.x, top: pointer.y, width: 1, height: 1,
        fill: "transparent", stroke: currentColor, strokeWidth: 3, selectable: false,
      });
    } else if (currentTool === "circle") {
      activeShape = new fabric.Circle({
        left: pointer.x, top: pointer.y, radius: 1,
        fill: "transparent", stroke: currentColor, strokeWidth: 3, selectable: false,
      });
    }
    canvas.add(activeShape);
  }

  function handleMouseMove(opt) {
    if (currentTool === "eraser" && isErasingActive) {
      eliminaOggettoSottoPuntatore(opt.e);
      return;
    }

    if (!isDrawingShape || !activeShape) return;
    const pointer = canvas.getPointer(opt.e);

    if (currentTool === "line") {
      activeShape.set({ x2: pointer.x, y2: pointer.y });
    } else if (currentTool === "rect") {
      activeShape.set({
        width: Math.abs(pointer.x - shapeOrigin.x),
        height: Math.abs(pointer.y - shapeOrigin.y),
        left: Math.min(pointer.x, shapeOrigin.x),
        top: Math.min(pointer.y, shapeOrigin.y),
      });
    } else if (currentTool === "circle") {
      const radius = Math.sqrt(
        Math.pow(pointer.x - shapeOrigin.x, 2) + Math.pow(pointer.y - shapeOrigin.y, 2)
      ) / 2;
      activeShape.set({
        radius: radius,
        left: Math.min(pointer.x, shapeOrigin.x),
        top: Math.min(pointer.y, shapeOrigin.y),
      });
    }
    canvas.renderAll();
  }

  function handleMouseUp() {
    if (currentTool === "eraser") {
      isErasingActive = false;
      pushHistory();
      return;
    }

    if (!isDrawingShape) return;
    isDrawingShape = false;
    if (activeShape) {
      activeShape.set({ selectable: true });
      canvas.setActiveObject(activeShape);
    }
    activeShape = null;
    pushHistory();
    setTool("select");
    if (window.ToolbarUI) window.ToolbarUI.setActiveTool("select");
  }

  // ================== ESPORTAZIONE ==================

  function exportPNG() {
    const viewportSalvato = canvas.viewportTransform.slice();
    const larghezzaSalvata = canvas.getWidth();
    const altezzaSalvata = canvas.getHeight();

    canvas.setWidth(DOCUMENT_WIDTH);
    canvas.setHeight(DOCUMENT_HEIGHT);
    canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
    canvas.renderAll();

    const dataUrl = canvas.toDataURL({ format: "png", quality: 1 });

    canvas.setWidth(larghezzaSalvata);
    canvas.setHeight(altezzaSalvata);
    canvas.setViewportTransform(viewportSalvato);
    canvas.renderAll();

    return dataUrl;
  }

  function exportState() {
    return canvas.toJSON();
  }

  return {
    init, onResize, fitToScreen, zoomIn, zoomOut, resetFit,
    loadState, loadImageAsObject, addPhotoFromDataUrl,
    setTool, setColor, undo, redo, eliminaOggettoSelezionato,
    exportPNG, exportState,
    DOCUMENT_WIDTH, DOCUMENT_HEIGHT,
  };
})();
