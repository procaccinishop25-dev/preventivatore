import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "drawing_editor",
    path=os.path.join(os.path.dirname(__file__), "frontend")
)


def drawing_editor(title=None, background_image_url=None, initial_state=None, width=1100, height=700, key=None):
    return _component_func(
        title=title,
        background_image_url=background_image_url,
        initial_state=initial_state,
        width=width,
        height=height,
        key=key,
        default=None,
    )
