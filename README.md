# BatchRenderObjects
A simple Blender-Addon to import and render multiple objects one by one in the same scene.


### How to use:
Once installed, the addon places a button in the "output properties" panel.
By clicking it, you open a file-browser-window. Select all your files you intend to render and press "Select Files to Render".

Blender then renders all of your selected objects into an "output"-folder, that is created in the same location, that your current .blend-file is located in.
The rendered images will be given the objects filename (without the extension). For example "suzanne.obj" may be rendered and saved to "suzanne.png".

Fileformat, rendersize, renderengine etc. are set as usual in their respective panels in Blender.

(Note that by default, Blender overwrites images, that have the same name. If you keep this setting, the addon would replace a "suzanne.obj" render with a "suzanne.fbx" render!)


### Currently supported file-formats:
- .obj
- .fbx
- .stl
- .blend


### Known limitations:
- The current render-progress is not displayed. Your operating-system may mark Blender as inresponsive. So once the rendering is started, you can't interact with Blender anymore, or see the progress. (Besides the appearing renders in the output-folder.)
