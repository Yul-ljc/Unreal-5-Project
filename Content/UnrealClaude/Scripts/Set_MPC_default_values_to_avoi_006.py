"""
@UnrealClaude Script
@Description: Set MPC_PoisonCircle default parameter values - CircleRadius=100000, EdgeSoftness=200, CircleCenter=(0,0)
"""
import unreal

mpc = unreal.load_asset('/Game/GamePlay/Materials/MPC_PoisonCircle')
if not mpc:
    unreal.log_error('MPC not found')
else:
    # Get current parameters
    scalar_params = mpc.get_editor_property('scalar_parameters')
    vector_params = mpc.get_editor_property('vector_parameters')
    
    # Find or set CircleRadius
    found_radius = False
    for p in scalar_params:
        name = p.get_editor_property('parameter_name')
        if str(name) == 'CircleRadius':
            p.set_editor_property('default_value', 100000.0)
            found_radius = True
            unreal.log(f'Updated CircleRadius default to 100000')
            break
    if not found_radius:
        new_p = unreal.MaterialParameterCollectionScalarParameter()
        new_p.set_editor_property('parameter_name', 'CircleRadius')
        new_p.set_editor_property('default_value', 100000.0)
        scalar_params.append(new_p)
        unreal.log('Added CircleRadius default 100000')
    
    # Find or set EdgeSoftness
    found_soft = False
    for p in scalar_params:
        name = p.get_editor_property('parameter_name')
        if str(name) == 'EdgeSoftness':
            p.set_editor_property('default_value', 200.0)
            found_soft = True
            unreal.log(f'Updated EdgeSoftness default to 200')
            break
    if not found_soft:
        new_p = unreal.MaterialParameterCollectionScalarParameter()
        new_p.set_editor_property('parameter_name', 'EdgeSoftness')
        new_p.set_editor_property('default_value', 200.0)
        scalar_params.append(new_p)
        unreal.log('Added EdgeSoftness default 200')
    
    # Find or set CircleCenter
    found_center = False
    for p in vector_params:
        name = p.get_editor_property('parameter_name')
        if str(name) == 'CircleCenter':
            p.set_editor_property('default_value', unreal.LinearColor(0, 0, 0, 0))
            found_center = True
            unreal.log('Updated CircleCenter default')
            break
    if not found_center:
        new_p = unreal.MaterialParameterCollectionVectorParameter()
        new_p.set_editor_property('parameter_name', 'CircleCenter')
        new_p.set_editor_property('default_value', unreal.LinearColor(0, 0, 0, 0))
        vector_params.append(new_p)
        unreal.log('Added CircleCenter default')
    
    mpc.set_editor_property('scalar_parameters', scalar_params)
    mpc.set_editor_property('vector_parameters', vector_params)
    unreal.EditorAssetLibrary.save_loaded_asset(mpc)
    unreal.log('MPC defaults updated and saved')