StableProjectorz core-features:

Create 3D models from 2D images and texture them via Automatic1111 StableDiffusion.

⦁	Preserves the original UVs.
⦁	Generates high-quality 3D geometry from 2D images using different generators locally, on your computer.
⦁	Makes multiple art variants (batches of art), via the Depth of the scene. Art is then automatically projected onto the 3D objects.
⦁	Texture entire object at once, via Multi-View-Projection. Great for visual consistency.
⦁	You can mix different art-projections and remove seams between them.
⦁	Adjust blending by painting/brushing directly on the 3D model.
⦁	Adjust Hue, Saturation, Value, Contrast of any 2D-art-projection.
⦁	Generate and use 2D Background to inspire the StableDiffusion when texturing your actual 3D-object.
⦁	Bake Ambient Occlusion shading, applies on top of all projections.
⦁	Uses several Control Net units, the first one is Depth (ON by default).
⦁	Uses img2img (Inpaint) Masking, to project only into selected areas. Ability to additionally enhance it with an inpaint-ControlNet unit.
⦁	You can use additional control net, such as Style-transfer control net, etc. Open your 3D models (OBJ), your own textures (PNG, JPG). Both txt2img and img2img capabilities.

StableProjectorz is created by Igor Aherne. 
Consider supporting the project 🙂

-------------------------------------------

Version 2.4.5:
⦁	3D: Added ability to Re-Texture an existing mesh, if the chosen 3D generator supports this
⦁	Corrected the thickness of a brush when erasing the projection mask
⦁	Bugfixes related to loading a different texture into an icon.
⦁	Bugfixes related to mesh deletion
⦁	Bugfixes related to Background-image vs Color-Gradient selection

Version 2.4.3:
⦁	3D: Introduced '3D' Mode for generating models from prompts and images.
⦁	3D: Added screenshot functionality with screenshot mirroring in 3D Mode.
⦁	3D: Created 3D API system for dynamic integration of 3D generators.
⦁	3D: Added downloadable generator catalogue starting with Trellis.
⦁	3D: Added 'Export 3D mesh' to Save dropdown menu.
⦁	3D: Implemented non-destructive 3D mesh import (swap-out mesh and keep  icons).
⦁	3D: Integrated rembg surroundings removal from BG, inside 3D Mode.
⦁	3D: Added a brush-eraser for manual background refinement.
⦁	3D: Added alpha channel visibility toggle for background editing.
⦁	Separated connection addresses for 2D and 3D modes.
⦁	Added Depth Brightness, very helpful for SDXL.
⦁	Automatic Depth-Noise-Dithering for low brightness. Helps to fix depth banding.
⦁	Added two WebUI-launch buttons with custom filepath support (StableDiffusion and 3D-generators).
⦁	Introduced "Import/Create background from current view".
⦁	Optimized UI dropdowns for instant slide-out, - more comfortable.
⦁	Enhanced thin surfaces anti-leak with 2k brush precision. 20MB VRAM per projection but much less leaks.
⦁	Added presets to quickly select background color or gradient.
⦁	Hovering the x2/x4 icon buttons inside an icon will show a full-screen preview of its Art.
⦁	Corrected the blending when baking brushed colors (hover the Color button -> Bake).
⦁	Added new settings for Ctrl clicking and paint-workflow scroll behavior.
⦁	Implemented Shift+1,2,etc. shortcuts for switching Art, Art(BG), etc.
⦁	Bugfix: fixed upscale from View, it works again when in ProjMask mode.
⦁	Bugfix: text prompt allows to copy small parts of text.
⦁	Bugfix: prevented the rare overflow of newline characters.
⦁	Bugfix: 'UV' Mode no longer culls the mesh.
⦁	Minor bugfix: fixed icon grid sizing for x2, x3, and x4 layouts.
⦁	Minor bugfix: resolved Control key becoming stuck after Ctrl+L and Ctrl+S.
⦁	Minor bugfix: improved cursor hiding when application not focused to prevent distraction.
⦁	Minor Bugfix: Fixed scrolling settings

Version 2.3.0:
⦁	Added Shadow_R integration, to reduce shadows, for Delighting ('Shadow Refiner', Wei Dong et al. 2024).
⦁	Displaying camera rotation / position (enable in Settings).
⦁	Button to relaunch Webui if you closed it to save memory.
⦁	Adding spz.config next to StableProjectorz.exe allows to avoid checking internet for updates. The spz.config should contain a line that says --skip-updates-check.

Version 2.2.1:
⦁	Ctrl+V and Shift+V launch upscale.
⦁	Major bugfix: icons maintain their correct order after Load.
⦁	Significant Improvement to the Total Obj workflow mode, respects edges and avoids stretches.
⦁	Added the Scheduler dropdown, to support the new Forge webui.

Version 2.2.0:
⦁	Revised the Upscaler Dropdown, refiner removed.
⦁	Upscaler Dropdown allows to upscale the current View.
⦁	Projection 2D icons have 'x2' and 'x4' upscaling buttons.
⦁	A view-upscale can be started via the 'Ctrl+E' and 'Shift+E' shortcuts.
⦁	Added the Scheduler dropdown, to support the new Forge webui.

Version 2.1.8:
⦁	Corrected the initial blending of multi-cameras.
⦁	Ctrl+A inside text prompt no longer accidentally reveals hidden meshes.
⦁	Corrected the behavior of the ControlNet thumbnails, during custom image and Save/Load

Version 2.1.5:
⦁	Major bugfix: Resolved black spots, for multi-cameras. Now a surface will be colored, as long as at least one camera sees it.
⦁	Corrections to the img2Img mode, in case Background is used.
⦁	Bugfix: It's again possible to sample colors during any Workflow mode.
⦁	Added Grid toggle to the viewport
⦁	Improvements to the Workflow Ribbon
⦁	FOV slider is always accessible, next to the cams slider, Sort Cameras button is returned
⦁	Copying text from the prompt will safely strip away the html color-tags.
⦁	The Re-do sliders are more accessible and comfortable.
⦁	Holding R no longer forces an eraser

Version 2.1.0:
⦁	Inpaint panel removed.  Workflow Modes tool ribbon added. Some Workflow-Modes will implicitly use the Inpaint.
⦁	UI panels redesigned, to work better with the new Workflow Modes ribbon.  Use settings to move the viewport if needed.
⦁	Controlnets show thumbnails under the prompt. Now it's much quicker to access them, or to remember which one is active
⦁	Ability to adjust Depth contrast directly from inside the controlnet thumbnail, below the prompt.
⦁	Major bugfix: LoRA notation no longer causes the text prompt to glitch. LoRa works fine, even with the text highlighting as On.
⦁	Bugfix: Normals Controlnet render order is corrected. It no longer behaves incorrectly during Object Select mode (ctrl+clicking).
⦁	Added "Avoid NSFW" toggle inside Settings. It's ON by default, and is less likely to generate 18+ images.
⦁	Settings have a new toggle, "Added "Avoid NSFW". It is ON by default, and is less likely to generate 18+ images.
⦁	Major bugfix: models without UV no longer glich-grayout the Gen Art button.
⦁	Major bugfix: UVs can touch the edges of the uv square zone, no longer causes glitches.
⦁	Minor bugfix: adjusted the Yes/No text in the confirmation popup to be more descriptive.
⦁	Major bugfix: project saving corrected, should load correctly now (Ctrl+S, Ctrl+L).

Version 2.0.4:
⦁	Inpaint improved: using depth algorithm to prevent "projection-auras". Prevents projections from "leaking" onto distant meshes.
⦁	Added drag-and-drop for 3d models and for textures
⦁	Bugfix: bucket fill works correctly with udims.
⦁	Bucket Fill is only accessible during Inpaint - prevents confusion and black colors.
⦁	Inpaint panel improved: EmptyNothing is removed. The only modes are 'Original' and 'WhereEmpty'.
⦁	Inpaint panel pulsates when erasing, reminding you that the Inpaint is ON.
⦁	Allowing Ctrl+A and Ctrl+D even when not hovering the main viewport.
⦁	Added a setting to avoid auto-focusing cameara when placing an orbit-pivot (Middle mouse click).
⦁	Saving over an existing file will ask for your confirmation. Avoids accidentally overwriting the work.
⦁	Far and Sft sliders affect icons of an entire batch group.
⦁	Bugfix: 3d mesh import glitch fixed: multi-material no longer causes black meshes.
⦁	Bugfix: 512x768 no longer causes inpaint's orange-mask to look stretched
⦁	MultiviewProjection has a Blend Cams button and shows text hints.

Version 2.0.3:
⦁	Ability to CTRL+Click on objects to show/hide them. Easier than searching for them in a 3d list
⦁	Major bugfix: Collapsing the Icons will never include brushed mask. More safe.
⦁	Major bugfix: Projection, Multiprojection, Brushing will safely ignore surfaces behind the camera. Avoids projections behind us in corridors etc.
⦁	Minor bugfix: bucket-fill tool no longer leaves seams.
⦁	Removed Auto-Erase button, use CTRL+E instead.
⦁	Delete-painted button is only shown while Inpaint is active. Use black/white bucket tool for masks.

Patch 2.0.2 additions:
⦁	Major bugfix: repetitive inpaint of the same area no longer causes the art to become blurry.
⦁	Clicking with Middle Mouse button sets an orbit pivot. Great for rotating around some specific detail. Press F to reset it.
⦁	Orbit pivot is set only if the user clicks the middle mouse (short time + short drag distance)
⦁	Bugfix: Single projection while inside Multiview Edit Mode. We can now erase this projection without it appearing frozen.
⦁	Multiview projection ignores normals when brushing/mixing the cameras. More intuitive.
⦁	Merging the layers is prevented during Gen Art. Will warn if there are brushed colors. + Red text for the Delete All Icons.
⦁	UVs at 1.0 are treated as the default _1001 udim.
⦁	Fixed the flickering of the Base neural net dropdown.
⦁	VAE dropdown list works with the newer Forge webui.

Version 2.0 additions:
⦁	Art-panel header has a button to collapse all icons into a single 4k texture. Helps to save VRAM.
⦁	Empty Nothing in Inpaint alows to use 'None Only' button. Masks the surfaces that never received projection yet.
⦁	Skybox can be blurred, for a more uniform surrounding/lighting.
⦁	Significant re-work of the top ribbon. It's now vertical, much closer to Inpaint panel. Reduces mouse travel by a half.
⦁	Improvement to the background rendering, objects blend better with it.
⦁	Fixed the depth contrast glitch, for the non-square resolutions above 1024.
⦁	Depth blur strength is now similar for different resolutions.
⦁	Added settings panel, alowing to fade out wireframe opacity and change its color
⦁	The settings panel allows to increase brush-uv-resolution from 1024 to 2048.
⦁	We ignore surface direction when Erasing - feels more comfortable. But is still used for Brushing.
⦁	Minor adjustment: alt-click sensitivity is reduced. Easier to sample colors on a tablet.
⦁	Minor bugfix: Brush opacity is no longer randomly stuck at 100% when exiting the inpaint.
⦁	Erase and BucketFill now have shortcuts Ctrl+F and Ctrl+E.

Patch 1.9.3 additions:
⦁	Masks can be brushed on the Custom UV textures as well.
⦁	New A1111 repo supported, controlnet no longer complains.
⦁	Major bugfix: Delete-Non-Selected: correct icons survive.
⦁	Bugfix: corrected the downloading/unzipping of the SF3D repository.
⦁	Bugfix: removed a bug that would erase white spaces from the prompt

Patch 1.9.2 additions:
⦁	Improved the installer - admin no longer required. Avoids dubious ownership git warnings.
⦁	Improved the installer - will attempt to re-download webui if connection drops.
⦁	GPUs compatibility: Using cuda 12.1 version of Forge for the installer, instead of the 12.4 version.
⦁	Fixed glitches with prompt-web find and the Get More url-dropdowns
⦁	Fixed the wrong sdxl-warnings

Version 1.9.1 additions:
⦁	Generate 3D meshes directly from Background images (powered by StableFast3D by StabilityAI).
⦁	Semantic Highlighting via NLP for text prompts: Nouns are detected and highlighted.
⦁	Installer significantly simplified: using Illyasviel's one-click install package. Helps with missing dependencies issues.
⦁	Added Point/Bilinear filtering. Use Point for pixelated low-res artisitc style. It's next to the -+ buttons under Save 2K.
⦁	Button to google highlighted text (in the prompts). Helps to confirm the common results are relevant for that text.
⦁	Ability to import Textured GBL meshes, for further refinement of generated stuff.
⦁	3D panel has tabs now: hierarchy and SF3D
⦁	Brush will fade out near edges of the mesh, to prevent leaving stretch-marks on the sides
⦁	Tablet-Pressure modes added: affect Size, affect Opacity/Transparency, affect Both, affect None
⦁	CFG scale slider is in 0.1 increments rather than 0.5
⦁	FAR slider in icons has 0.1 as the default, instead of 0.5
⦁	Added bucket and fill button to the lower-left inpaint panel, fixed the color-glitch in the brush ribbon (top right)
⦁	Bugfix: cleanup of resources improved: deleting icons correctly notifies its list-managers
⦁	Bugfix: Meshes with Morpher/BlendShapes import fine.
⦁	Major Bugfix for UDIMs: 3x3 udims no longer cause brushing glitches.

Version 1.8.4 additions:
⦁	Added delete button for the Inpaint and for Masking
⦁	Added 'Delete Last Generation', useful for discarding an entire recent batch of images.
⦁	Improved the UI fonts for the vertical Command Ribbon
⦁	Controlnet UI improved
⦁	Bugfix: the Load inside icon works again
⦁	Bugfix: input decimal-numbers are shown correctly regardless of user's Region/Locale
⦁	Bucket Fill is accessible both for Masking and for Inpainting
⦁	Bucket Fill with Clear mask works fine for multi-view Inpainting
⦁	No longer saving IP and Port during the project-save, to avoid exposing the user
⦁	Bugfix for Upscalers, - custom upscalers are detected and can be used.
⦁	Bugfix: Normals camera listens to FOV
⦁	Bugfix: Inpaint's Clear-mask will always paint with 100% transparency, to ensure results are always apparent.
⦁	Resolved issues around UV edges, when using FAR and SFT sliders inside icons (edge blur)
⦁	Improved the UI controls inside the Input panel

Version 1.8.1 additions:
⦁	Bugfix: Inpaint Brushing works for multiple UDIMs.
⦁	Bugfix: depth camera no longer accidentally culls sub-meshes when they are isolated with MultiView
⦁	Inpaint Screen Mask is also shown when hovering GenArt button.
⦁	Text prompts ignore Tab character.
⦁	Improved comfort: Tab, R, X, Shift+W can be used anywhere, without hovering Main View

Version 1.8.0 additions:
⦁	Major Bugfix: Inpaint is no longer ignored inside multiview (but can't paint in MultiView -yet)
⦁	Major Bugfix: Orthographic view no longer has visual outline-glich with FAR and SFT icon sliders
⦁	Bugfix: fixed annoying bug with the mini-text-prompt (main view context menu). Line no longer snaps
⦁	Bugfix: can drag multiview cameras around even when the inpaint mode is active.
⦁	Adjusting Depth or Fov sliders no longer drags cameras in Multiview

Version 1.7.8 additions:
⦁	Bugfix: Ctrl+hovering icon shows correct checker on the 3d model.
⦁	Added GenArt GenBG mini-buttons into MainView context menu (right click)
⦁	Added Hints into the intro screen
⦁	Bugfix: screen mask (orange) won't accidentally re-appear during generation.
⦁	Bugfix: corrected the Inpaint masking when background is used.
⦁	Added 3 buttons to the header of Art list: Delete Hidden, Delete All, Delete non-selected
⦁	Right-clicking the Viewport or pressing Space - opens Colorpicker with mini-prompts.
⦁	Improved brushing and erasing - removed residual brush traces that kept showing even after multiple erasing.
⦁	Minor Bugfix: clicking on an icon that's hidden (because of Solo) will correctly show it again.

Version 1.7.5 additions:
⦁	Significant upgrade for Inpaint. Now we paint it in UV space, and its screen-mask is made when rendering. Offers blur. 
⦁	Mask-Mode now works as Inpaint-Sketch, with ability to paint colors, or soft transparent masks.
⦁	Inpaint masks will be affected by FAR and SFT sliders inside each icon.
⦁	Removed Inpaint modes 'Latent Noise', 'Fill' because we can sketch with colors now. 'Original' and 'Latent Nothing' remain. 
⦁	Bucket-Fill tool added, to color isolated meshes. Accessible inside Inpaint mode
⦁	Mask-Invert tool added, to flip visible regions the mask (visible to invisible and vice-versa). 
⦁	Eye-dropper Tool, ability to sample any color by holding ALT (in Inpaint mode)
⦁	Right clicking the Viewport (in Inpaint mode) will spawn RGB color picker.
⦁	Top Ribbon adjusted, to accomodate new buttons and modes.
⦁	SDXL depth major bugfixes: resolution-relative Depth Blurring for any width and height. Depth controls remain visible while previewing depth.
⦁	Two pass depth-blur: blur the sharp-edges in a second iteration. Good for SDXL (removes wireframe glitches)
⦁	Bugfix: Depth no longer disappears for Non-square aspect ratios.
⦁	Bugfix: Hide and Solo can be turned of fine, after loading a project. Not compatible with the older saves.

Patch 1.7.0 additions:
⦁	UDIMs work. Projections land into several uv sectors, producing several textures at once.
⦁	Importing several textures (at once) creates a stack-icon, where each texture is applied to its UDIM.
⦁	Soft Inpaint added: ability to draw soft mask, which is then respected by StableDiffusion.
⦁	Significant Bugfix of the Depth Contrast, depth is more pronounced and accurate. 70% contrast is default.
⦁	Brush size can be changed by the [ ] keyboard buttons.
⦁	Fixed the brushing for older GPUs (Conservative Raster). Slight improvement for uv-seams
⦁	FAR and SFT sliders improved. Now SFT offers a blend between sharp, smooth, noisy falloff
⦁	Ability to disable Text shown in the Inpaint Brush, useful if using transparent inpaint brush
⦁	Cameras slider is more straightforward.
⦁	Camera can snap to 45 degrees (26 directions) instead of just 90.
⦁	Added hint in the Cmd intro panel, for new users, "how to launch webui manually"
⦁	Esc can be used to cancel the Yes/No panel.
⦁	Fixed the tablet-pressure bug.
⦁	Fixed the Content Camera bug (Export Views button).
⦁	Fixed the bug with 'Ignore Depth' and 'Ignore Normals' not deactivating after closing Inpaint.

Patch 1.6.3 additions:
⦁	Bufix: Saving correctly produces SPZ file
⦁	Bugfix: Custom DAT Upscalers are identified.
⦁	Bugfix: Controlnets correctly expand after loading a project.
⦁	Bugfix: Skinned/Rigged models can open and render correctly.
⦁	Ability to import custom 2D projection icon in Art panel.

Patch 1.5.8 additions:
⦁	ip adapter (control nets Style Transfer) - fixed a bug with custom image formats.
⦁	Style Transfer via 'reference_only' works correctly.
⦁	All preprocessors can activate 2 additional sliders inside ControlNet for fine-tuning.
⦁	Added Refiner, to finalize your images with extra details
⦁	Added Upscaler, to make your images larger, as a post-processing
⦁	Added 'Fast Webui' button, to launch webui with fast arguments. Helpful with Refiner + Upscaler.
⦁	Added Tiling into Inpaint settings (bottom left panel). Useful for 2D grass, road textures, etc.
⦁	Added 'Export Views' button - saves current camera views to disk (+Depth, Normals, etc)
⦁	Added 'delete all icons' button into Art and ArtBG panel.
⦁	ScreenMask button offers new mini-button, to inpaint when multiprojecting.
⦁	Holding Shift will draw a straight line from the previous brush stroke.
⦁	Icon can be cloned after right clicking it. (will implement 'make tile from screenshot' later)
⦁	Saving a project will cache the name
⦁	Auto-Soft-Edges button disabled by default. Prevents black rim, and makes Multiprojection sharper.
⦁	Bugfix: Inpaint with 'Original' will disable Controlnets to prevent blur.
⦁	Bugfix: preventing low quality inpaint image when 'Low FPS (Perform)' optimizaation is on.

Patch 1.5.6 additions:
⦁	Correction to the 'Back Side' text used in Multiprojection
⦁	Closing the program will show confirmation popup
⦁	Ensured compatibility with latest A1111 webui (1.9.3) and sd-webui-controlnet. 
⦁	Auto-soft-edge button added in Art header, disables/enables rim for projections
⦁	Minor cosmetic adjustment for the 'Back Side' text used in Multiprojection.

Patch 1.5.3 additions:
⦁	bugfix: transparency of exported textures is using correct alpha-Blending mode.
⦁	bugfix: isolated 3d mesh no longer causes permanent blackness on geometry that was hidden.
⦁	bugfix: isolated meshes might have glitched the masks of a preceding  Multi-Projections.
⦁	ControlNet always offers 'None' option. Useful for some Webui, when using Reference Only preprocessor.
⦁	Printing "Back Side" text, for reverse sides of Multi-Projection. Helps when brushing/blending

Version 1.5.1 additions:
⦁	1-6 cameras are mutually-additive inside any Multi-View projection, making their brushing and blending much easier.
⦁	For Multi-view projection, SFT slider inside icon provide extra help with blending.
⦁	Select VAE, to help with inpainting (desaturated issues).
⦁	Visibility of entire projection. Sliders replaced with circles. (drag left and right)
⦁	Super Depth button replaced by Contrast Slider.
⦁	Fading of the projection borders. You can paint them away if needed by white brush. Right-click an icon to control it.
⦁	When using several cameras, if brush is white, it will show "preview" inside cursor.
⦁	Screen mask brush is semi-transparent. Also, it has little toggle, to prevent Screen Mask from resetting.
⦁	Camera Circles removed, and now you can click anywhere in the Main Viewport, and it will enter Edit mode.
⦁	Ability to export without Dilation (only dilates 5 texels) and transparent background. 
⦁	Removed the anti-seam button, always dilating by 5 pixels now.
⦁	Vertex colors are shown on the model if toggled in 3D OBJ panel. Can be submitted as input to any ControlNet Unit. Right click its preview, and select Vert/View Normals/Depth.
⦁	Your model normals will be imported. Can help if fading a multi-view projection.
⦁	Removed bugs with the red Cams slider and the FOV slider
⦁	Cursor size increased to gigantic. Helps if you Shift + Right Drag during painting inside multiprojection, for a quick art-preview.
⦁	Brush circle changes color (black/white)
⦁	Saving a project will always save a 4k version of baked projections. This can defend you if save-file gets corrupted.
⦁	Ambient Occlusion is smoother by about 40%, hides low-polyness. Sharp variant of AO remains the same.

Version 1.4.7 additions:
⦁	Import normals (wrapped around object) or for background, from top of Arts or Arts BG tab. Only to be seen by CTRL Nets.
⦁	Fixed annoying bug that forced Edit Mode when there was a background and more than 1 camera.
⦁	Fixed bug during loading a save-file: control net preview-icon loads correctly.
⦁	Added warnings if there is 'XL' in name of your base neural net, but no XL in some Depth or Normal CTRL net.
⦁	Fixed the aspect-ratio glitch that happened during loading of non-square projections.
⦁	CTRL+click on preset will paste text where cursor (caret) is in the text prompt. No longer constrained for merely appending to the end.

Version 1.4.3 additions:
⦁	Saving / Loading of the project are possible. All art images are conveniently stored into the Data folder, next to the .spz file.
⦁	Added presets for the Text Prompts. Click to switch the text entirely. Ctrl+Click to append to the current text.
⦁	Memory improvements: deleting icon of a batch will release its GPU memory without waiting for you to delete the entire batch of icons.
⦁	Bugfix with the viewport-circles:  projections no longer ignore the models if viewports are outside the Main View window.
⦁	Minor adjustment to the Super Depth, making its contrast slightly more adequate.
⦁	ControlNet bugifx: now MyPromptIsMoreImportant and ControlNetIsMoreImportant are actually differing. (before it was only the former).
⦁	ControlNet bugfix: the LowVRAM in control net, - now it actually gets sent.
⦁	ControlNet bugfix: Fixed the preview-image from becoming desaturated.

Version 1.3.8 additions:
⦁	Support for Forge webui (new) + the Automatic1111 webui (legacy). 
Forge increases the speed of image generation by x2. For example, 8 seconds instead of 17. This allows to generate more images at once.
⦁	Smooth Depth: resolves wireframe-glitches of certain SDXL networks. Allows to blur the depthmap inside StableProjectorz, to conceal any low-polyness.
⦁	Mouse-Panning is no longer constrained to the Main Viewport.
⦁	Bugfix with projections not landing on isolated objects. For example, hiding the walls of a building, to texture a door mesh.
⦁	Viewport numbers will fade out when the mouse is moved away. Good for previews.

Version 1.3.1 additions:
⦁	Texture whole object at once, via Multi-View-Projection. Great for visual consistency of projections from different sides of your 3D models.
⦁	Preventing webui disconnects during high-resolution generations (longer timeout  4sec->20 sec).
⦁	Optimized GPU usage, especially when the app is idle.
⦁	'FPS Perform' toggle will also reduce + restore resolution while generating, making it easier for the GPU to focus on diffusing.
⦁	Added Camera Snapping (pressing CTRL while orbiting will align it to 1 of the 6 world directions)
⦁	FBX models load correctly even if they are skinned to bones (rigging)
⦁	Adjusting Camera field-of-view looks nicer, no longer zooms out.

Version 1.2.1 additions:
⦁	Grid can be toggled to show 2, 3, 4 icons per row.
⦁	Change the order of projections by rearranging the icons in the grid.
⦁	Pressing S or W while in the viewport will also rearrange icons, and A/D will change the selection.
⦁	Ability to move your custom textures up/down.
⦁	Improvements in texture memory of brush masks (memory consumption reduced).
⦁	Improved visibility of icon groups: borders + tinting of icons during hover. Can be switched off. This caused the removal of the icon-scaling effect.
⦁	Ambient occlusion bugfix: ensured its background is black instead of transparent.
⦁	Camera alignment bugfix: pressing 'Restore Camera' will definitely return it to the correct location.
⦁	Context menu is shown by default when hovering over an icon (good for new users). Can be switched off.
⦁	Minor improvements to the icon context menu.
⦁	Minor improvements to the header in the Art and Art-BG panel.
⦁	Minor corrections to Projection Draw Order (shown when the R key is held).

Patch 1.1.4 addtions: 
⦁	an actual seed displayed in the icon instead of -1
⦁	Backgrounds can be adjusted by Hue/Saturation/Value/Contrast
⦁	Ability to load FBX (though OBJ is preferred).
⦁	Ability to load image into custom icon
⦁	Brush resize - shortcuts (Shift + RightMouseDrag)

Patch 1.1.3 additions:
⦁	Corrected the projection tiling when camera is zoomed in
⦁	added texture dialtion. Hide sthe seams from showing.
⦁	improved the saving 
⦁	Improvements for brush controls + shortcuts (F1,F2, F3 for hardness)
⦁	ControlNet preprocessor resolution bugfix + ability to select resolution factor.
⦁	Support for legacy control net count parameter, for users with their own webui (apr 2023)
⦁	Added ability to throttle fps to save performance
⦁	Removed Reset Mask button. Resets automatically if mask mode is turned off.


Patch 1.1.2 additions:
⦁	improves the loading of obj files.
⦁	Added support for legacy control net count parameter, for users with their own webui (apr 2023)