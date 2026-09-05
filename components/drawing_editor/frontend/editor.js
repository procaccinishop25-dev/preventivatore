const DrawingEditor = (function () {
  let canvas = null;
  let currentTool = "select";
  let currentColor = "#000000";
  let historyStack = [];
  let historyIndex = -1;
  let isRestoring = false;
  let isDrawingShape = false;
  let isErasingActive = false;
  let shapeOrigin = null;
  let activeShape = null;

  function init(canvasId, width, height) {
    canvas = new fabric.Canvas(canvasId, { selection: true, backgroundColor: "#ffffff" });
    canvas.setWidth(width);
    canvas.setHeight(height);

    canvas.on("object:added", pushHistoryIfNeeded);
    canvas.on("object:modified", pushHistoryIfNeeded);
    canvas.on("object:removed", pushHistoryIfNeeded);
    canvas.on("path:created", pushHistoryIfNeeded);

    canvas.on("mouse:down", handleMouseDown);
    canvas.on("mouse:move", handleMouseMove);
    canvas.on("mouse:up", handleMouseUp);

    pushHistory();
    return canvas;
  }

  function resize(width, height) {
    if (!canvas) return;
    canvas.setWidth(width);
    canvas.setHeight(height);
    canvas.renderAll();
  }

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

  function loadImageAsObject(url) {
    fabric.Image.fromURL(url, function (img) {
      const maxDim = Math.min(canvas.getWidth(), canvas.getHeight()) * 0.7;
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
      const maxDim = Math.min(canvas.getWidth(), canvas.getHeight()) * 0.6;
      if (img.width > maxDim || img.height > maxDim) {
        const scale = maxDim / Math.max(img.width, img.height);
        img.scale(scale);
      }
      img.set({ left: 60, top: 60 });
      canvas.add(img);
      canvas.setActiveObject(img);
      canvas.renderAll();
    });
  }

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

  function exportPNG() {
    return canvas.toDataURL({ format: "png", quality: 1 });
  }

  function exportState() {
    return canvas.toJSON();
  }

  return { init, resize, loadState, loadImageAsObject, addPhotoFromDataUrl, setTool, setColor, undo, redo, exportPNG, exportState };
})();
