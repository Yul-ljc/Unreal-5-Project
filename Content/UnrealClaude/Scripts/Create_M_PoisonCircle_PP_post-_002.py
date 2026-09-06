/** @UnrealClaude Script
 * @Description: Create M_PoisonCircle_PP post-process material for poison circle darkening effect
 */
import unreal

# Load MPC
mpc = unreal.load_asset('/Game/GamePlay/Materials/MPC_PoisonCircle')
unreal.log('MPC loaded: ' + str(mpc))

# Create material
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.MaterialFactoryNew()
material = asset_tools.create_asset('M_PoisonCircle_PP', '/Game/GamePlay/Materials/', unreal.Material, factory)
unreal.log('Material created: ' + material.get_path_name())

# Set post-process properties
material.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
material.set_editor_property('blendable_location', unreal.BlendableLocation.BL_AFTER_TONEMAPPING)

# Helper function
editor = unreal.MaterialEditingLibrary

# 1. CollectionParameter: CircleCenter (vector)
node_center = editor.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -800, 0)
node_center.set_editor_property('collection', mpc)
node_center.set_editor_property('parameter_name', 'CircleCenter')

# 2. CollectionParameter: CircleRadius (scalar)
node_radius = editor.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -800, 200)
node_radius.set_editor_property('collection', mpc)
node_radius.set_editor_property('parameter_name', 'CircleRadius')

# 3. CollectionParameter: EdgeSoftness (scalar)
node_softness = editor.create_material_expression(material, unreal.MaterialExpressionCollectionParameter, -800, 400)
node_softness.set_editor_property('collection', mpc)
node_softness.set_editor_property('parameter_name', 'EdgeSoftness')

# 4. WorldPosition
node_worldpos = editor.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -500, 0)

# 5. ComponentMask for WorldPosition (XY only)
node_mask_wp = editor.create_material_expression(material, unreal.MaterialExpressionComponentMask, -300, -50)
node_mask_wp.set_editor_property('r', True)
node_mask_wp.set_editor_property('g', True)
node_mask_wp.set_editor_property('b', False)
node_mask_wp.set_editor_property('a', False)

# 6. ComponentMask for CircleCenter (XY only)
node_mask_center = editor.create_material_expression(material, unreal.MaterialExpressionComponentMask, -300, 150)
node_mask_center.set_editor_property('r', True)
node_mask_center.set_editor_property('g', True)
node_mask_center.set_editor_property('b', False)
node_mask_center.set_editor_property('a', False)

# 7. Distance
node_distance = editor.create_material_expression(material, unreal.MaterialExpressionDistance, -100, 50)

# 8. Subtract: Distance - Radius
node_sub = editor.create_material_expression(material, unreal.MaterialExpressionSubtract, 100, 50)

# 9. Divide: Subtract / Softness
node_div = editor.create_material_expression(material, unreal.MaterialExpressionDivide, 300, 50)

# 10. Saturate
node_sat = editor.create_material_expression(material, unreal.MaterialExpressionSaturate, 500, 50)

# 11. SceneTexture: PostProcessInput0
node_scene = editor.create_material_expression(material, unreal.MaterialExpressionSceneTexture, 500, 300)
node_scene.set_editor_property('scene_texture_id', unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)

# 12. Multiply: SceneColor * 0.3 (dark)
node_mul = editor.create_material_expression(material, unreal.MaterialExpressionMultiply, 700, 300)
node_mul.set_editor_property('const_b', 0.3)

# 13. Lerp: mix original and dark
node_lerp = editor.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, 900, 150)

# Connect nodes
# WorldPosition -> ComponentMask_WP
editor.connect_material_expressions(node_worldpos, '', node_mask_wp, '')
# CircleCenter -> ComponentMask_Center
editor.connect_material_expressions(node_center, '', node_mask_center, '')
# ComponentMask_WP -> Distance.A
editor.connect_material_expressions(node_mask_wp, '', node_distance, 'A')
# ComponentMask_Center -> Distance.B
editor.connect_material_expressions(node_mask_center, '', node_distance, 'B')
# Distance -> Subtract.A
editor.connect_material_expressions(node_distance, '', node_sub, 'A')
# CircleRadius -> Subtract.B
editor.connect_material_expressions(node_radius, '', node_sub, 'B')
# Subtract -> Divide.A
editor.connect_material_expressions(node_sub, '', node_div, 'A')
# EdgeSoftness -> Divide.B
editor.connect_material_expressions(node_softness, '', node_div, 'B')
# Divide -> Saturate
editor.connect_material_expressions(node_div, '', node_sat, '')
# SceneTexture -> Multiply.A
editor.connect_material_expressions(node_scene, '', node_mul, 'A')
# SceneTexture -> Lerp.A (original)
editor.connect_material_expressions(node_scene, '', node_lerp, 'A')
# Multiply -> Lerp.B (dark)
editor.connect_material_expressions(node_mul, '', node_lerp, 'B')
# Saturate -> Lerp.Alpha
editor.connect_material_expressions(node_sat, '', node_lerp, 'Alpha')

# Connect Lerp to Material EmissiveColor
material_prop = material.get_editor_property('expressions')
# Find the material output node and connect
editor.connect_material_property(node_lerp, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)

# Save
unreal.EditorAssetLibrary.save_loaded_asset(material)
unreal.log('Material M_PoisonCircle_PP created and saved!')