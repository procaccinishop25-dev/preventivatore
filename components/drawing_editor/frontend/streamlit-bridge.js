(function () {
  function sendMessageToStreamlit(type, data) {
    const outboundData = Object.assign({
      isStreamlitMessage: true,
      type: type,
    }, data);
    window.parent.postMessage(outboundData, "*");
  }

  const Streamlit = {
    RENDER_EVENT: "streamlit:render",
    events: new EventTarget(),

    setComponentReady: function () {
      sendMessageToStreamlit("streamlit:componentReady", { apiVersion: 1 });
    },

    setFrameHeight: function (height) {
      sendMessageToStreamlit("streamlit:setFrameHeight", { height: height });
    },

    setComponentValue: function (value) {
      sendMessageToStreamlit("streamlit:setComponentValue", { value: value, dataType: "json" });
    },

    receiveMessageFromStreamlit: function (event) {
      if (!event.data || event.data.type !== Streamlit.RENDER_EVENT) return;
      const evt = new CustomEvent(Streamlit.RENDER_EVENT, { detail: event.data });
      Streamlit.events.dispatchEvent(evt);
    },
  };

  window.addEventListener("message", Streamlit.receiveMessageFromStreamlit);
  window.Streamlit = Streamlit;
})();
