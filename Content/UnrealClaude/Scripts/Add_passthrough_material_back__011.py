"""
@UnrealClaude Script
@Description: Add passthrough M_PoisonCircle_PP to PostProcessVolume
"""
import unreal

# Find PostProcessVolume
ed_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = ed_sys.get_all_level_actors()
for a in actors:
    if a.get_class().get_name() == 'PostProcessVolume':
        mat = unreal.load_asset('/Game/GamePlay/Materials/M_PoisonCircle_PP')
        settings = a.get_editor_property('settings')
        blendables = settings.get_editor_property('weighted_blendables')
        
        entry = unreal.WeightedBlendable()
        entry.set_editor_property('weight', 1.0)
        entry.set_editor_property('object', mat)
        
        arr = [entry]
        blendables.set_editor_property('array', arr)
        settings.set_editor_property('weighted_blendables', blendables)
        a.set_editor_property('settings', settings)
        unreal.log('PostProcessVolume updated with passthrough material')
        break