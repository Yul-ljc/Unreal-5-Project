"""
@UnrealClaude Script
@Description: Rebuild M_PoisonCircle_PP from scratch - SceneTexture passthrough for testing
"""
import unreal

# Delete old material
path = '/Game/GamePlay/Materials/M_PoisonCircle_PP'
if unreal.EditorAssetLibrary.does_asset_exist(path):
    unreal.EditorAssetLibrary.delete_asset(path)
    unreal.log('Deleted old material')

# Create new material
mpc = unreal.load_asset('/Game/GamePlay/Materials/MPC_PoisonCircle')
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.MaterialFactoryNew()
mat = asset_tools.create_asset('M_PoisonCircle_PP', '/Game/GamePlay/Materials/', unreal.Material, factory)
mat.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
unreal.log('Material created')

editor = unreal.MaterialEditingLibrary

# Step 1: SceneTexture node
scene = editor.create_material_expression(mat, unreal.MaterialExpressionSceneTexture, 0, 0)
scene.set_editor_property('scene_texture_id', unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
unreal.log('SceneTexture created')

# Step 2: Connect SceneTexture -> EmissiveColor
result = editor.connect_material_property(scene, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
unreal.log(f'Connect result: {result}')

# Save
unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.log('Saved simple passthrough material')