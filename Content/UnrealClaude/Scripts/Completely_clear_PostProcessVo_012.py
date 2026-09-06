"""
@UnrealClaude Script
@Description: Clear all PP volume settings - remove blendables and reset to defaults
"""
import unreal

ed_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = ed_sys.get_all_level_actors()
for a in actors:
    cls = a.get_class().get_name()
    if cls == 'PostProcessVolume':
        # Get current state
        settings = a.get_editor_property('settings')
        bb = settings.get_editor_property('weighted_blendables')
        arr = bb.get_editor_property('array')
        unreal.log(f'Blendable count: {len(arr)}')
        for i, b in enumerate(arr):
            unreal.log(f'  [{i}]: {b.get_editor_property("object")} weight={b.get_editor_property("weight")}')
        
        # Clear array completely
        bb.set_editor_property('array', [])
        settings.set_editor_property('weighted_blendables', bb)
        a.set_editor_property('settings', settings)
        
        # Also check unbound
        unbound = a.get_editor_property('unbound')
        unreal.log(f'Unbound: {unbound}')
        
        # Set priority low so it doesn't interfere
        a.set_editor_property('priority', 0.0)
        unreal.log('Cleared all blendables, priority=0')
        break