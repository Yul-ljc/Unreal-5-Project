"""
@UnrealClaude Script
@Description: Temporarily remove post-process blendable and check material structure
"""
import unreal

# Step 1: Remove blendable from PostProcessVolume
actors = unreal.EditorActorSubsystem().get_all_level_actors()
for a in actors:
    if a.get_class().get_name() == 'PostProcessVolume':
        settings = a.get_editor_property('settings')
        blendables = settings.get_editor_property('weighted_blendables')
        arr = blendables.get_editor_property('array')
        unreal.log(f'Current blendables: {len(arr)}')
        for b in arr:
            obj = b.get_editor_property('object')
            unreal.log(f'  Blendable: {obj}')
        # Clear array
        blendables.set_editor_property('array', [])
        settings.set_editor_property('weighted_blendables', blendables)
        a.set_editor_property('settings', settings)
        unreal.log('Removed all blendables from PostProcessVolume')
        break

# Step 2: Check the material
mat = unreal.load_asset('/Game/GamePlay/Materials/M_PoisonCircle_PP')
if mat:
    domain = mat.get_editor_property('material_domain')
    unreal.log(f'Material domain: {domain}')
    # Check expressions
    exps = mat.get_editor_property('expressions')
    unreal.log(f'Expression count: {len(exps)}')
    for e in exps:
        unreal.log(f'  {e.get_class().get_name()}')