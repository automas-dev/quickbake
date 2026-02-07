# Quick Bake

Quick and simple baking in Blender.

**ToDo**

- [ ] Add docs for how to download from release
- [ ] Tests + Coverage
- [ ] Can any blender extension code become more modern?
- [ ] Show progress (wm cursor)
- [ ] Render custom passes (eg. metallic) with emit channel
- [ ] Replace all materials of multi material object with one

## Usage

Download this repo as a zip file and install through the Blender addons.

### Interface

![Quickbake Interface](docs/panel.png)

### Inputs

| Field           | Description                                            |
| --------------- | ------------------------------------------------------ |
| Name            | Name used for baked images and material                |
| Size            | Bake image size in pixels                              |
| Assign Material | Assign material with baked images to object after bake |
| Save Images     | Save images to external directory                      |
| Layers          | Enable baking of different layers, one image per layer |
