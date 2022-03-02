from scene import Scene
from scene_view import SceneView
from scene_gui import SceneGUI

from ..factory import register_view, register_gui
register_view(Scene, SceneView)
register_gui(SceneView, SceneGUI)


