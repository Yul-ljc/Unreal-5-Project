"""
@UnrealClaude Script
@Description: Update existing MPC parameter defaults - CircleRadius=100000, CircleCenter=(0,0)
"""
import unreal

mpc = unreal.load_asset('/Game/GamePlay/Materials/MPC_PoisonCircle')
scalar_params = mpc.get_editor_property('scalar_parameters')
vector_params = mpc.get_editor_property('vector_parameters')

for p in scalar_params:
    name = str(p.get_editor_property('parameter_name'))
    if name == 'CircleRadius':
        p.set_editor_property('default_value', 100000.0)
        unreal.log(f'CircleRadius -> 100000')
    if name == 'EdgeSoftness':
        p.set_editor_property('default_value', 200.0)
        unreal.log(f'EdgeSoftness -> 200')

for p in vector_params:
    name = str(p.get_editor_property('parameter_name'))
    if name == 'CircleCenter':
        p.set_editor_property('default_value', unreal.LinearColor(0, 0, 0, 0))
        unreal.log(f'CircleCenter -> (0,0)')

mpc.set_editor_property('scalar_parameters', scalar_params)
mpc.set_editor_property('vector_parameters', vector_params)
unreal.EditorAssetLibrary.save_loaded_asset(mpc)
unreal.log('MPC saved')