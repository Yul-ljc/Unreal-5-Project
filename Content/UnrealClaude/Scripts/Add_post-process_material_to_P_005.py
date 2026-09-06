"""
@UnrealClaude Script
@Description: Add M_PoisonCircle_PP as blendable on PostProcessVolume_0
"""
import unreal

# Find the post process volume
actors = unreal.EditorLevelLibrary.get_all_level_actors()
ppv = None
for a in actors:
    if a.get_class().get_name() == 'PostProcessVolume':
        ppv = a
        break

if not ppv:
    unreal.log_error('PostProcessVolume not found')
else:
    # Load the material
    mat = unreal.load_asset('/Game/GamePlay/Materials/M_PoisonCircle_PP')
    if not mat:
        unreal.log_error('Material not found')
    else:
        # Get current settings
        settings = ppv.get_editor_property('settings')
        blendables = settings.get_editor_property('weighted_blendables')
        arr = blendables.get_editor_property('array')
        
        # Add new blendable entry
        new_entry = unreal.WeightedBlendable()
        new_entry.set_editor_property('weight', 1.0)
        new_entry.set_editor_property('object', mat)
        arr.append(new_entry)
        
        blendables.set_editor_property('array', arr)
        settings.set_editor_property('weighted_blendables', blendables)
        ppv.set_editor_property('settings', settings)
        
        unreal.log('SUCCESS: Material added to PostProcessVolume')