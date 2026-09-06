"""
@UnrealClaude Script
@Description: Fix MPC defaults, rebuild post-process material with proper FName API, apply to PostProcessVolume
"""
import unreal

# ====== STEP 1: Fix MPC defaults ======
mpc = unreal.load_asset('/Game/GamePlay/Materials/MPC_PoisonCircle')
scalar_params = mpc.get_editor_property('scalar_parameters')
vector_params = mpc.get_editor_property('vector_parameters')

for p in scalar_params:
    name = str(p.get_editor_property('parameter_name'))
    if name == 'CircleRadius':
        p.set_editor_property('default_value', 10000.0)
        unreal.log(f'MPC: CircleRadius -> 10000')
    if name == 'EdgeSoftness':
        p.set_editor_property('default_value', 200.0)
        unreal.log(f'MPC: EdgeSoftness -> 200')

for p in vector_params:
    name = str(p.get_editor_property('parameter_name'))
    if name == 'CircleCenter':
        p.set_editor_property('default_value', unreal.LinearColor(2600.0/255.0, 4200.0/255.0, 0, 0))
        unreal.log(f'MPC: CircleCenter -> (2600,4200)')

mpc.set_editor_property('scalar_parameters', scalar_params)
mpc.set_editor_property('vector_parameters', vector_params)
unreal.EditorAssetLibrary.save_loaded_asset(mpc)
unreal.log('MPC saved')

# ====== STEP 2: Delete old material ======
path = '/Game/GamePlay/Materials/M_PoisonCircle_PP'
if unreal.EditorAssetLibrary.does_asset_exist(path):
    unreal.EditorAssetLibrary.delete_asset(path)
    unreal.log('Old material deleted')

# ====== STEP 3: Create new material ======
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.MaterialFactoryNew()
mat = asset_tools.create_asset('M_PoisonCircle_PP', '/Game/GamePlay/Materials/', unreal.Material, factory)
mat.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
unreal.log('New material created: PostProcess domain')

editor = unreal.MaterialEditingLibrary

# CollectionParameter: CircleCenter (vector)
n_center = editor.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, -800, 0)
n_center.set_editor_property('collection', mpc)
# CRITICAL FIX: use unreal.Name() not plain string
n_center.set_editor_property('parameter_name', unreal.Name('CircleCenter'))

# CollectionParameter: CircleRadius (scalar)
n_radius = editor.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, -800, 200)
n_radius.set_editor_property('collection', mpc)
n_radius.set_editor_property('parameter_name', unreal.Name('CircleRadius'))

# CollectionParameter: EdgeSoftness (scalar)
n_soft = editor.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, -800, 400)
n_soft.set_editor_property('collection', mpc)
n_soft.set_editor_property('parameter_name', unreal.Name('EdgeSoftness'))

# WorldPosition
n_wp = editor.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -500, 0)

# ComponentMask for WorldPosition (XY)
n_mwp = editor.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -300, -50)
n_mwp.set_editor_property('r', True)
n_mwp.set_editor_property('g', True)
n_mwp.set_editor_property('b', False)
n_mwp.set_editor_property('a', False)

# ComponentMask for CircleCenter (XY)
n_mc = editor.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -300, 150)
n_mc.set_editor_property('r', True)
n_mc.set_editor_property('g', True)
n_mc.set_editor_property('b', False)
n_mc.set_editor_property('a', False)

# Distance
n_dist = editor.create_material_expression(mat, unreal.MaterialExpressionDistance, -100, 50)

# Subtract: Distance - Radius
n_sub = editor.create_material_expression(mat, unreal.MaterialExpressionSubtract, 100, 50)

# Divide: Subtract / Softness
n_div = editor.create_material_expression(mat, unreal.MaterialExpressionDivide, 300, 50)

# Saturate
n_sat = editor.create_material_expression(mat, unreal.MaterialExpressionSaturate, 500, 50)

# SceneTexture: PostProcessInput0
n_scene = editor.create_material_expression(mat, unreal.MaterialExpressionSceneTexture, 500, 300)
n_scene.set_editor_property('scene_texture_id', unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)

# Multiply: SceneColor * 0.3 (dark)
n_mul = editor.create_material_expression(mat, unreal.MaterialExpressionMultiply, 700, 300)
n_mul.set_editor_property('const_b', 0.3)

# Lerp: mix original and dark
n_lerp = editor.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, 900, 150)

# ====== STEP 4: Connect nodes ======
editor.connect_material_expressions(n_wp, '', n_mwp, '')
editor.connect_material_expressions(n_center, '', n_mc, '')
editor.connect_material_expressions(n_mwp, '', n_dist, 'A')
editor.connect_material_expressions(n_mc, '', n_dist, 'B')
editor.connect_material_expressions(n_dist, '', n_sub, 'A')
editor.connect_material_expressions(n_radius, '', n_sub, 'B')
editor.connect_material_expressions(n_sub, '', n_div, 'A')
editor.connect_material_expressions(n_soft, '', n_div, 'B')
editor.connect_material_expressions(n_div, '', n_sat, '')
editor.connect_material_expressions(n_scene, '', n_mul, 'A')
editor.connect_material_expressions(n_scene, '', n_lerp, 'A')
editor.connect_material_expressions(n_mul, '', n_lerp, 'B')
editor.connect_material_expressions(n_sat, '', n_lerp, 'Alpha')
result = editor.connect_material_property(n_lerp, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
unreal.log(f'connect_material_property result: {result}')

# ====== STEP 5: Save material ======
unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.log('Material saved')

# ====== STEP 6: Apply to PostProcessVolume ======
ed_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = ed_sys.get_all_level_actors()
for a in actors:
    if a.get_class().get_name() == 'PostProcessVolume':
        mat = unreal.load_asset('/Game/GamePlay/Materials/M_PoisonCircle_PP')
        settings = a.get_editor_property('settings')
        bb = settings.get_editor_property('weighted_blendables')
        
        entry = unreal.WeightedBlendable()
        entry.set_editor_property('weight', 1.0)
        entry.set_editor_property('object', mat)
        
        bb.set_editor_property('array', [entry])
        settings.set_editor_property('weighted_blendables', bb)
        a.set_editor_property('settings', settings)
        unreal.log('Applied to PostProcessVolume')
        break

unreal.log('ALL DONE')