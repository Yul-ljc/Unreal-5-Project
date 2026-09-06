"""
@UnrealClaude Script
@Description: Add EdgeSoftness scalar parameter to MPC_PoisonCircle
"""
import unreal

mpc = unreal.load_asset('/Game/GamePlay/Materials/MPC_PoisonCircle')

# Try to add scalar parameter using the proper API
# Use EditorTransaction to add parameter
scalar_params = mpc.get_editor_property('scalar_parameters')

# Check if EdgeSoftness exists
has_soft = False
for p in scalar_params:
    name = str(p.get_editor_property('parameter_name'))
    if name == 'EdgeSoftness':
        has_soft = True
        p.set_editor_property('default_value', 200.0)
        unreal.log('EdgeSoftness already exists, updated to 200')
        break

if not has_soft:
    # Try creating with new_object
    new_param = unreal.new_object(unreal.MaterialParameterCollectionScalarParameter.static_class())
    unreal.log('Created param type: ' + str(type(new_param)))

mpc.set_editor_property('scalar_parameters', scalar_params)
unreal.EditorAssetLibrary.save_loaded_asset(mpc)
unreal.log('Done')