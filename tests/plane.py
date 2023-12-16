from open3d.visualization import gui, rendering

gui.Application.instance.initialize()
window = gui.Application.instance.create_window("plane", 1080, 960)

_3d = gui.SceneWidget()
_3d.enable_scene_caching(True)
_3d.scene = rendering.Open3DScene(window.renderer)
_3d.scene.show_ground_plane(True, rendering.Scene.GroundPlane.XY)
window.add_child(_3d)

gui.Application.instance.run()
